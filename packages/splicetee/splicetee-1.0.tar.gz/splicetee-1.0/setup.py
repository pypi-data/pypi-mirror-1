from distutils.core import setup, Extension

LONG_DESCRIPTION = '\
Interface for Python for the Linux (2.6.17+) splice and tee system calls\n\
The splicetee module is an interface to the Linux splice() and tee() system \
calls from the Python programming language.\n\
\n\
These system calls allow you to :\n\
\n\
 * transfer data between two pipes without consuming the input.\n\
 * move data from a stream to another without need for user-space involvment\n\
   and with minimal (or no) copying.\n\
'

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: POSIX :: Linux
"""

module1 = Extension('splicetee',
                    sources = ['spliceteemodule.c'])

setup (name = 'splicetee',
       version = '1.0',
       author = 'Omar Ait Mous',
       author_email = 'dev.python.splicetee@enix.fr',
       maintainer = 'Omar Ait Mous',
       maintainer_email = 'dev.python.splicetee@enix.fr',
       url = 'www.enix.org',
       license = 'http://www.gnu.org/licenses/gpl.txt',
       platforms = ['Linux'],
       description = 'A Python interface to splice and tee system calls.',
       long_description = LONG_DESCRIPTION,
       classifiers = filter(None, classifiers.split("\n")),
       ext_modules = [module1])
