from setuptools import setup, Extension
from losetup import __version__
setup(name='losetup',
      version=__version__,
      description='Python API for "loop" Linux module',
      author='Sergey Kirillov',
      author_email='serg@rainboo.com',
#      ext_modules=[Extension('_losetup', ['src/losetupmodule.c'], include_dirs=['src'])],
      py_modules=['losetup']
)
