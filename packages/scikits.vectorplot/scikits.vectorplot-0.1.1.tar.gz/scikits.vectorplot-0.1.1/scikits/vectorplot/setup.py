from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from numpy.distutils.misc_util import Configuration


# To create or update `lic_internal.c`, simply execute:
# cython lic_internal.pyx

def configuration(parent_package='', top_path=None):

    config = Configuration('vectorplot', parent_package, top_path)

    config.add_extension("lic_internal",
        sources=["lic_internal.c"],
        include_dirs=['.'],
    )

    return config

if __name__ == '__main__':
    setup(cmdclass={'build_ext': build_ext}, **configuration(top_path='').todict())



