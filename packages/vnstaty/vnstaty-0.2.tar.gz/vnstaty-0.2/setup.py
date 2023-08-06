from setuptools import setup, Extension, find_packages

ext_mod = Extension('_vnstaty',
                    sources = ['vnstaty/ifinfo.c', 
                               'vnstaty/_vnstaty.c'])

setup (name = 'vnstaty',
       version = '0.2',
       packages=find_packages(),
       install_requires=['Elixir'],
       ext_modules = [ext_mod])
