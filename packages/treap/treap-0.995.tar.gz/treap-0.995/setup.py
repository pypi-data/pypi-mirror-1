
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

version = open('Version', 'r').readline().rstrip()

setup(
    name='treap',
    py_modules=['treap', 'duptreap', 'py_treap_node', 'py_duptreap_node', 'nest' ],
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("pyx_treap_node", ["pyx_treap_node.c"]), Extension("pyx_duptreap_node", ["pyx_duptreap_node.c"])],
    version=version,
    description='Python implementation of treaps',
    long_description='''
A set of python modules implementing treaps is provided.

Treaps perform most operations in O(log2n) time, and are innately sorted.
They're very nice for keeping a collection of values that needs to
always be sorted, or for optimization problems in which you need to find
the p best values out of q, when p is much smaller than q.

Modules are provided for both treaps that enforce uniqueness, and treaps that allow duplicates.

Pure python versions are included, as are Cython-enhanced versions for performance.
''',
    author='Daniel Richard Stromberg',
    author_email='strombrg@gmail.com',
    url='http://stromberg.dnsalias.org/~dstromberg/treap/',
    platforms='Cross platform',
    license='Apache v2',
    )

