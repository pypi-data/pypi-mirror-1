from setuptools import setup, Extension, find_packages

ext_mod = Extension('_vnstaty',
                    sources = ['vnstaty/ifinfo.c', 
                               'vnstaty/_vnstaty.c'])

setup (name='vnstaty',
       version='0.1',
       author='Sergio Campos',
       author_email='seocam@seocam.net',
       license='PSF',
       description='Python implementation of vnstat.',
  
       packages=find_packages(),
       install_requires=['Elixir'],
       ext_modules = [ext_mod],
)
