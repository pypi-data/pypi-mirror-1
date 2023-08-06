from distutils.core import setup, Extension

module1 = Extension('netinfo',
                    sources = ['netinfo.c', 'iface.c', 'route.c'])

setup (name = 'Pynetinfo',
       version = '0.1.9',
       description = 'python network information',
       ext_modules = [module1])