from distutils.core import setup, Extension

module1 = Extension('netinfo',
                    sources = ['netinfo.c'])

setup (name = 'Pynetinfo',
       version = '0.1',
       description = 'python network information',
       ext_modules = [module1])