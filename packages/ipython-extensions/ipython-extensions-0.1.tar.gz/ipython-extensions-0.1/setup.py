from distutils.core import setup
setup(
    name = 'ipython-extensions',
    version = "0.1",
    author = "Ville M. Vainio",
    author_email = 'vivainio@gmail.com',
    url = 'http://ipython.scipy.org',
    py_modules = [
 'ipy_miscapps',
 'ipy_gmail',
],
    description = 'Optional extensions for IPython',
    long_description = """IPython extensions of varying usability and maturity

You may install this package to add interesting and/or useful features to 
enhance your IPython experience. Contributions to this package are encouraged,
with the 'release early, release often' maxim - it is expected that the original
contributor (as opposed to the core IPython team) will take care of most of the 
maintenance of his/her own extension.

Installation: run 'setup.py install' or 'easy_install ipython-extensions'

Currently provided:

 - ipy_gmail: A gmail interface
 
 - ipy_miscapps: Tab completers for various command line apps
 	   
"""        
)
