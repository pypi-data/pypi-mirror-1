from distutils.core import setup
#from setuptools import setup

from poachplatelib import meta

setup(name="poachplate",
      version=meta.__version__,
      author=meta.__author__,
      description="a script to create python script boilerplate (setup.py/package/README/etc)",
      scripts=["bin/poachplate"],
      package_dir={"poachplatelib":"poachplatelib"},
      packages=['poachplatelib'],
)
           
