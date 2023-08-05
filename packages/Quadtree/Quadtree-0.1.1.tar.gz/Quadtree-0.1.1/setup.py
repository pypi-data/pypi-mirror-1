
from setuptools import setup, Extension

_tree = Extension('quadtree._tree',
                  sources=['quadtree/_treemodule.c',
                           'shapelib/shptree.c',
                           'shapelib/shpopen.c'],
                  include_dirs=['shapelib']
                  )

setup(name          = 'Quadtree',
      version       = '0.1.1',
      description   = 'Quadtree spatial index for Python GIS',
      license       = 'BSD',
      keywords      = 'spatial index',
      author        = 'Sean Gillies',
      author_email  = 'sgillies@frii.com',
      maintainer    = 'Sean Gillies',
      maintainer_email  = 'sgillies@frii.com',
      url               = 'http://icon.stoa.org/trac/pleiades/wiki/QuadTree',
      packages      = ['quadtree'],
      namespace_packages    = ['quadtree'],
      ext_modules   = [_tree],
      classifiers   = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Database',
        ],
)

