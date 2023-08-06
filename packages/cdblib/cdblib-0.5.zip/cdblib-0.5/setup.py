from distutils.core import setup, Extension

setup(name="cdblib",
      version="0.5",
      description='Read and write cdb ("constant database") files',
      long_description=open("README.txt").read(),
      author="John E. Barham",
      author_email="jbarham@gmail.com",
      license="MIT",
      platforms="All",
      py_modules=["cdblib"],
      ext_modules=[Extension("_cdblib", ["_cdblib.c"])],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.5",
          "Topic :: System :: Filesystems"
    ]
)
