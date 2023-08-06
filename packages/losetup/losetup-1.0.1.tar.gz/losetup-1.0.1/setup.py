from setuptools import setup, Extension
setup(name='losetup',
      version='1.0.1',
      description='Python API for "loop" Linux module',
      author='Sergey Kirillov',
      author_email='serg@rainboo.com',
      ext_modules=[Extension('_losetup', ['src/losetupmodule.c'], include_dirs=['src'])],
      py_modules=['losetup']
)
