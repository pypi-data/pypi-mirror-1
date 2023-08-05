from distutils.core import setup
import sys

py_version_t = (2,5)
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
        version = '3.0-beta1'+version_ext,
        description = 'Preprocessor generator for Python',
        author = 'Kay Schluehr',
        author_email = 'easyextend@fiber-space.de',
        url = 'http://www.fiber-space.de/',
        download_url = 'http://www.fiber-space.de/EasyExtend/doc/main/Download_EE.html',
        license = "BSD",
        packages =
        ['EasyExtend.langlets',
         'EasyExtend.langlets.gallery',
         'EasyExtend.langlets.gallery.lexdef',
         'EasyExtend.langlets.gallery.parsedef',
         'EasyExtend.langlets.gallery.reports',
         'EasyExtend.langlets.gallery.tests',
         'EasyExtend.langlets.grammar_langlet',
         'EasyExtend.langlets.grammar_langlet.lexdef',
         'EasyExtend.langlets.grammar_langlet.parsedef',
         'EasyExtend.langlets.grammar_langlet.reports',
         'EasyExtend.langlets.grammar_langlet.tests',
         'EasyExtend.langlets.zero',
         'EasyExtend.langlets.zero.lexdef',
         'EasyExtend.langlets.zero.parsedef',
         'EasyExtend.langlets.zero.reports',
         'EasyExtend.langlets.zero.tests',
         'EasyExtend.langlet_template',
         'EasyExtend.langlet_template.lexdef',
         'EasyExtend.langlet_template.parsedef',
         'EasyExtend.langlet_template.reports',
         'EasyExtend.langlet_template.tests',
         'EasyExtend.tests',
         'EasyExtend.trail',
         #'EasyExtend.trail.tests',
         'EasyExtend.util',
         'EasyExtend'],
    package_data = {'EasyExtend': ['exo.space', 'fs', 'Grammar', 'Token'],
                    'EasyExtend.langlet_template': ['conf.py_template'],
                    'EasyExtend.langlet_template.lexdef': ['Token.ext'],
                    'EasyExtend.langlet_template.parsedef': ['Grammar.ext'],
                    'EasyExtend.langlet_template.reports': ['sentinel.txt'],
                    'EasyExtend.langlets.gallery.lexdef': ['Token', 'Token.ext'],
                    'EasyExtend.langlets.gallery.parsedef': ['Grammar', 'Grammar.ext'],
                    'EasyExtend.langlets.gallery.reports': ['gallery_test_gallery.ees'],
                    'EasyExtend.langlets.gallery.tests': ['funcs.gal',
                                                          'test_gallery.gal',
                                                          'test_ip.gal'],
                    'EasyExtend.langlets.grammar_langlet.lexdef': ['Token', 'Token.ext'],
                    'EasyExtend.langlets.grammar_langlet.parsedef': ['Grammar'],
                    'EasyExtend.langlets.zero.lexdef': ['Token', 'Token.ext'],
                    'EasyExtend.langlets.zero.parsedef': ['Grammar', 'Grammar.ext'],
                    'EasyExtend.langlets.zero.reports': ['zero_test_creation.ees',
                                                         'zero_test_cstgen.ees']}

    )

