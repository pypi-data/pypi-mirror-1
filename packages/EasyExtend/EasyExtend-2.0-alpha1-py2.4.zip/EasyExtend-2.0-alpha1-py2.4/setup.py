from distutils.core import setup
import sys

py_version_t = (2,4)
py_version_s = ".".join([str(x) for x in py_version_t])



class VersionError(Exception):pass

'''
if sys.version_info[:2] !=py_version_t:
    raise VersionError, "Python %s required for installation of this package"%py_version_s
'''

eepath = "lib/site-packages/EasyExtend"

if __name__ == '__main__':
    version_ext = ""
    if 'sdist' in sys.argv:
        version_ext = '-py'+py_version_s

    setup(
        name = 'EasyExtend',
        version = '2.0-alpha1'+version_ext,
        description = 'Preprocessor generator for Python',
        author = 'Kay Schluehr',
        author_email = 'easyextend@fiber-space.de',
        url = 'http://www.fiber-space.de/',
        packages = ['EasyExtend',
                    'EasyExtend.parser',
                    'EasyExtend.util',
                    'EasyExtend.fibers',
                    'EasyExtend.fibers.coverage',
                    'EasyExtend.fibers.coverage.fibermod',
                    'EasyExtend.fibers.gallery',
                    'EasyExtend.fibers.gallery.fibermod',
                    'EasyExtend.fibers.Py25Lite',
                    'EasyExtend.fibers.Py25Lite.fibermod',
                    'EasyExtend.fibers.teuton',
                    'EasyExtend.fibers.teuton.fibermod',
                    'EasyExtend.fibers.macro',
                    'EasyExtend.fibers.macro.fibermod',
                    'EasyExtend.fibers.transit',
                    'EasyExtend.fibers.transit.fibermod',
                    'EasyExtend.fibers.transit.fiber_template',
                    'EasyExtend.fibers.transit.fiber_template.fibermod',
                    ],
    data_files = [(eepath,
                   ["EasyExtend/fs"]),
                  (eepath+"/fibers/coverage",
                   ["EasyExtend/fibers/coverage/Grammar"]),
                  (eepath+"/fibers/gallery",
                   ["EasyExtend/fibers/gallery/Grammar"]),
                  (eepath+"/fibers/Py25Lite",
                   ["EasyExtend/fibers/Py25Lite/Grammar"]),
                  (eepath+"/fibers/macro",
                   ["EasyExtend/fibers/macro/Grammar"]),
                  (eepath+"/fibers/teuton",
                   ["EasyExtend/fibers/teuton/Grammar"]),
                  (eepath+"/fibers/transit",
                   ["EasyExtend/fibers/transit/Grammar"]),
                  (eepath+"/fibers/transit/fiber_template",
                   ["EasyExtend/fibers/transit/fiber_template/Grammar"]),
                  ],
    )


