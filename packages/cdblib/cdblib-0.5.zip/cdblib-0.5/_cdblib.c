#include <stdint.h>
#include <Python.h>

static uint32_t CDB_HASHSTART = 5381;

/*
 * Conceptually cdb hash tables form a mapping from key hash values to lists
 * of record locations.  Storing such a mapping in a Python dictionary would
 * be straightforward, but at the expense of comparatively high memory usage
 * given the overhead of Python objects.
 *
 * However, given the following:
 *  - by definition a cdb is limited to 4 GB, so record locations are 32-bit values
 *  - the cdb hash function returns a 32-bit unsigned integer
 *  - the cdb hash function is relatively collision resistant (e.g., it will
 *    generate only 1 collision given an input of 65536 unique SHA-1 digests)
 *  - many cdbs store records with unique keys
 * for cdbs that store records with unique keys and have less than, e.g., 65536
 * records, the vast majority of hash values will map to only a single record,
 * so we need only 8 bytes to store such hash/location pairs.  For hash values
 * that map to multiple records, we can store the sentinel value 0xFFFFFFFF
 * in the location (since it is not a valid record location) to signal that the
 * records' locations list is stored in a separate auxiliary structure containing
 * only lists of record locations that share the same hash value.
 *
 * E.g., given the above conditions and an average record size of 8K, we can store
 * the hash/location indexes for 100 GB of data in 100 MB of memory
 * (i.e., 1/1000th the size of the data) which is pretty darn good.
 */

static uint32_t MULTI_SENTINEL = 0xFFFFFFFF;

typedef struct LiteIndexObject LiteIndexObject;
typedef struct HashLocation HashLocation;
typedef struct HashMultiLocation HashMultiLocation;

struct LiteIndexObject {
	PyObject_HEAD
	HashLocation *hashlist;
	int n; /* total number of hash values */
	HashMultiLocation *hashmultilist;
	int nmulti; /* number of hash values with multiple records */
};

struct HashLocation {
	uint32_t hash;
	uint32_t location;
};

struct HashMultiLocation{
	uint32_t hash;
	int n;
	uint32_t *locations;
};

static PyTypeObject LiteIndex_Type;

static void
LiteIndex_dealloc(LiteIndexObject *self)
{
	int i;

	PyMem_Free(self->hashlist);
	for (i = 0; i < self->nmulti; i++)
		PyMem_Free(self->hashmultilist[i].locations);
	PyMem_Free(self->hashmultilist);
        self->ob_type->tp_free((PyObject *)self);
}

static int
checkPyObjectIsInt(PyObject *obj)
{
	if (PyInt_Check(obj) || PyLong_Check(obj))
		return 1;
	else {
		PyErr_SetNone(PyExc_TypeError);
		return 0;
	}
}

static int
LiteIndex_init(LiteIndexObject *self, PyObject *args, PyObject* kwargs)
{
	Py_ssize_t i, j, n, nmulti, imulti, nlocations;
	PyObject *hashtable, *hashlist, *hash, *locationlist;
	HashLocation *hloc;
	HashMultiLocation *hmultiloc;

	self->n = self->nmulti = 0;
	self->hashlist = NULL;
	self->hashmultilist = NULL;

	if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &hashtable)) {
		PyErr_SetNone(PyExc_ValueError);
		return -1;
	}

	/* Build a list of sorted dictionary keys so that we can build the
	 * LiteIndexObject hashlist in hash order and use binary search.
	 */
	hashlist = PyDict_Keys(hashtable);
	if (hashlist == NULL)
		return -1;
	if (PyList_Sort(hashlist) == -1)
		goto error;
	n = PyList_Size(hashlist);

	/* Do a sanity type-check over the dictionary and count the number of
	 * hash values that map to multiple locations.
	 */
	nmulti = 0;
	for (i = 0; i < n; i++) {
		hash = PyList_GetItem(hashlist, i);
		if (hash == NULL || !checkPyObjectIsInt(hash))
			goto error;

		locationlist = PyDict_GetItem(hashtable, hash);
		if (locationlist == NULL || !PyList_Check(locationlist)) {
			PyErr_SetNone(PyExc_ValueError);
			goto error;
		}

		nlocations = PyList_Size(locationlist);
		if (nlocations == 0) {
			PyErr_SetNone(PyExc_ValueError);
			goto error;
		}
		for (j = 0; j < nlocations; j++) {
			if (!checkPyObjectIsInt(PyList_GetItem(locationlist, j)))
				goto error;
		}
		if (nlocations > 1)
			nmulti++;
	}

	self->hashlist = PyMem_Malloc(n * sizeof(HashLocation));
	if (self->hashlist == NULL) {
		PyErr_SetNone(PyExc_MemoryError);
		goto error;
	}
	self->n = n;

	self->hashmultilist = PyMem_Malloc(nmulti * sizeof(HashMultiLocation));
	if (self->hashmultilist == NULL) {
		PyErr_SetNone(PyExc_MemoryError);
		goto error;
	}
	memset(self->hashmultilist, 0, nmulti * sizeof(HashMultiLocation));
	self->nmulti = nmulti;

	/* Here's where we do the real work of the populating the LiteIndexObject
	 * index from the Python dictionary.  This time we can skip type checking.
	 */
	imulti = 0;
	for (i = 0; i < n; i++) {
		hloc = &(self->hashlist[i]);

		hash = PyList_GetItem(hashlist, i);
		locationlist = PyDict_GetItem(hashtable, hash);
		nlocations = PyList_Size(locationlist);

		hloc->hash = PyInt_AsUnsignedLongMask(hash);
		if (nlocations == 1)
			hloc->location = PyInt_AsUnsignedLongMask(PyList_GetItem(locationlist, 0));
		else { /* nlocations > 1 */
			hloc->location = MULTI_SENTINEL;

			hmultiloc = &(self->hashmultilist[imulti]);
			hmultiloc->hash = hloc->hash;
			hmultiloc->n = nlocations;
			hmultiloc->locations = PyMem_Malloc(nlocations * sizeof(uint32_t));
			if (hmultiloc->locations == NULL) {
				PyErr_SetNone(PyExc_MemoryError);
				goto error;
			}

			for (j = 0; j < nlocations; j++)
				hmultiloc->locations[j] = PyInt_AsUnsignedLongMask(PyList_GetItem(locationlist, j));

			imulti++;
		}
	}

	Py_DECREF(hashlist);
	return 0;

error:
	Py_DECREF(hashlist);
	return -1;
}

/* get_hash_locations() takes a single argument, the cdb hash value, and returns
 * a tuple of locations of records with keys for the given hash.  Otherwise it
 * raises KeyError.
 */
static PyObject *
LiteIndex_get_hash_locations(LiteIndexObject *self, PyObject *args)
{
	int i, low, mid, high, nmulti;
	uint32_t hash, *multilocations;
	PyObject *location, *multituple;

	if (!PyArg_ParseTuple(args, "k", &hash))
		return NULL;

	/* Binary search to find location of hash/location record. */
	low = 0; high = self->n;
	while (low < high) {
		mid = low + ((high - low) / 2);
		if (self->hashlist[mid].hash < hash)
			low = mid + 1;
		else
			high = mid;
	}
	if ((low < self->n) && (self->hashlist[low].hash == hash)) {
		if (self->hashlist[low].location != MULTI_SENTINEL) {
			/* Single location for hash. */
			location = PyLong_FromUnsignedLong(self->hashlist[low].location);
			if (location == NULL)
				return NULL; /* Shouldn't happen... */
			return PyTuple_Pack(1, location);
		}

		/* Multiple locations for hash. */
		low = 0; high = self->nmulti;
		while (low < high) {
			mid = low + ((high - low) / 2);
			if (self->hashmultilist[mid].hash < hash)
				low = mid + 1;
			else
				high = mid;
		}
		if ((low < self->n) && (self->hashmultilist[low].hash == hash)) {
			nmulti = self->hashmultilist[low].n;
			multilocations = self->hashmultilist[low].locations;

			multituple = PyTuple_New(nmulti);
			if (multituple == NULL) {
				PyErr_SetNone(PyExc_MemoryError);
				return NULL;
			}
			for (i = 0; i < nmulti; i++) {
				location = PyLong_FromUnsignedLong(multilocations[i]);
				if (location == NULL) {
					Py_DECREF(multituple);
					return NULL;
				}
				PyTuple_SetItem(multituple, i, location);
			}
			return multituple;
		}
		else
			return NULL; /* Shouldn't happen! */
	}
	else {
		PyErr_SetNone(PyExc_KeyError); /* Hash value isn't in index. */
		return NULL;
	}
}

static PyMethodDef LiteIndex_methods[] = {
	{"get_hash_locations", (PyCFunction)LiteIndex_get_hash_locations, METH_VARARGS,
	 	PyDoc_STR("get_hash_locations(hash) -> locations")},
	{NULL,	NULL},
};

static PyTypeObject LiteIndex_Type = {
	PyObject_HEAD_INIT(NULL)
	0,			/*ob_size*/
	"_cdblib.LiteIndex",	/*tp_name*/
	sizeof(LiteIndexObject),/*tp_basicsize*/
	0,			/*tp_itemsize*/
	(destructor)LiteIndex_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	0,			/*tp_getattr*/
	0,			/*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
	0,                      /*tp_call*/
	0,                      /*tp_str*/
	0,                      /*tp_getattro*/
	0,                      /*tp_setattro*/
	0,                      /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	0,                      /*tp_doc*/
	0,                      /*tp_traverse*/
	0,                      /*tp_clear*/
	0,                      /*tp_richcompare*/
	0,                      /*tp_weaklistoffset*/
	0,                      /*tp_iter*/
	0,                      /*tp_iternext*/
	LiteIndex_methods,      /*tp_methods*/
	0,                      /*tp_members*/
	0,                      /*tp_getset*/
	0,                      /* tp_base */
	0,                      /* tp_dict */
	0,                      /* tp_descr_get */
	0,                      /* tp_descr_set */
	0,                      /* tp_dictoffset */
	(initproc)LiteIndex_init, /* tp_init */
	0,                      /* tp_alloc */
	0,                      /* tp_new */
	0                       /* tp_free */
};

static PyObject *
cdb_hash(PyObject *self, PyObject *args)
{
	unsigned char *key;
	int n;
	uint32_t hash;

	if (!PyArg_ParseTuple(args, "s#", &key, &n))
		return NULL;

	hash = CDB_HASHSTART;
	while (n--)
		hash = (hash + (hash << 5)) ^ *key++;

	return PyLong_FromUnsignedLong(hash);
}

static PyMethodDef cdblib_methods[] = {
	{"cdb_hash", cdb_hash, METH_VARARGS,
	"cdb_hash(s) -> CDB hash of byte string"},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
init_cdblib(void)
{
	PyObject *m;

	m = Py_InitModule("_cdblib", cdblib_methods);
	if (m == NULL)
		return;

	LiteIndex_Type.tp_new = PyType_GenericNew;
	if (PyType_Ready(&LiteIndex_Type) < 0)
		return;

	Py_INCREF(&LiteIndex_Type);
	PyModule_AddObject(m, "LiteIndex", (PyObject *)&LiteIndex_Type);
}
