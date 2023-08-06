
from distutils.core import setup, Extension

module1 = Extension('SwishE',
                    sources = [ 'SwishE.c'],
                    include_dirs = ['/usr/local/include', '/usr/include'],
                    library_dirs = ['/usr/local/lib', '/usr/include'],
                    libraries = ['swish-e'])
                    
setup (name = 'SwishE',
       version = '0.5',
       description = 'SwishE/Python API',
       author = 'JB Robertson',
       license = 'BSD',
       author_email='jibe@freeshell.org',
       url='http://jibe.freeshell.org/bits/SwishE/',
       #py_modules = ['SwishE'],
       ext_modules = [module1])


