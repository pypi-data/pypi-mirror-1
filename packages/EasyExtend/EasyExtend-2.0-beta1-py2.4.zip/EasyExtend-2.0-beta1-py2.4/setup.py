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
        version = '2.0-beta1'+version_ext,
        description = 'Preprocessor generator for Python',
        author = 'Kay Schluehr',
        author_email = 'easyextend@fiber-space.de',
        url = 'http://www.fiber-space.de/',
        download_url = 'http://www.fiber-space.de/EasyExtend/doc/main/Download_EE.html',
        license = "BSD",
        classifiers=[
          'Development Status :: beta 1',
          'Intended Audience :: Developers',
          'Intended Audience :: Researchers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: Any',
          'Programming Language :: Python',
          'Topic :: Language analysis and synthesis',
          'Topic :: Preprocessing',
          'Topic :: Macros'],

        packages = ['EasyExtend',
                    'EasyExtend.parser',
                    'EasyExtend.util',
                    'EasyExtend.fibers',
                    'EasyExtend.fibers.coverage',
                    'EasyExtend.fibers.coverage.fibermod',
                    'EasyExtend.fibers.coverage.fibercon',
                    'EasyExtend.fibers.gallery',
                    'EasyExtend.fibers.gallery.fibermod',
                    'EasyExtend.fibers.gallery.fibercon',
                    'EasyExtend.fibers.Py25Lite',
                    'EasyExtend.fibers.Py25Lite.fibermod',
                    'EasyExtend.fibers.Py25Lite.fibercon',
                    'EasyExtend.fibers.teuton',
                    'EasyExtend.fibers.teuton.fibermod',
                    'EasyExtend.fibers.teuton.fibercon',
                    'EasyExtend.fibers.macro',
                    'EasyExtend.fibers.macro.fibermod',
                    'EasyExtend.fibers.macro.fibercon',
                    'EasyExtend.fibers.transit',
                    'EasyExtend.fibers.transit.fibermod',
                    'EasyExtend.fibers.transit.fibercon',
                    'EasyExtend.fibers.transit.fiber_template',
                    'EasyExtend.fibers.transit.fiber_template.fibermod',
                    'EasyExtend.fibers.transit.fiber_template.fibercon',
                    'EasyExtend.fibers.zero',
                    'EasyExtend.fibers.zero.fibermod',
                    'EasyExtend.fibers.zero.fibercon',
                    ],
    package_data = {"EasyExtend":["fs"],
                    "EasyExtend.fibers.coverage":["Grammar"],
                    "EasyExtend.fibers.gallery":["Grammar"],
                    "EasyExtend.fibers.Py25Lite":["Grammar"],
                    "EasyExtend.fibers.macro":["Grammar"],
                    "EasyExtend.fibers.teuton":["Grammar"],
                    "EasyExtend.fibers.transit":["Grammar"],
                    "EasyExtend.fibers.transit.fiber_template":["Grammar"],
                    "EasyExtend.fibers.zero":["Grammar"]}
    )

