from distutils.core import setup, Extension
import sys

py_version_t = (2,5)
py_version_s = ".".join([str(x) for x in py_version_t])

class VersionError(Exception):pass

if sys.platform == 'win32':
    Scripts     = ['scripts/p4d.py', 'scripts/p4d_bat.py']
    P4D_data    = []
    trail_data  = ['cyTrail.pyd']
    ext_modules = []
else:
    Scripts     = ['scripts/p4d.py']
    ext_modules = [Extension('cyTrail', ['EasyExtend/trail/cyTrail.c'])]
    P4D_data    = []
    trail_data  = ['cyTrail.c']


eepath = "lib/site-packages/EasyExtend"

if __name__ == '__main__':
    version_ext = ""
    if 'sdist' in sys.argv:
        version_ext = '-py'+py_version_s

    setup(
        name = 'EasyExtend',
        version = '3.0.1'+version_ext,
        description = 'Preprocessor generator for Python',
        author = 'Kay Schluehr',
        author_email = 'easyextend@fiber-space.de',
        url = 'http://www.fiber-space.de/',
        download_url = 'http://www.fiber-space.de/EasyExtend/doc/main/Download_EE.html',
        license = "BSD",
        packages = ['EasyExtend.langlets',
          'EasyExtend.langlets.coverage',
          'EasyExtend.langlets.coverage.lexdef',
          'EasyExtend.langlets.coverage.parsedef',
          'EasyExtend.langlets.coverage.reports',
          'EasyExtend.langlets.coverage.tests',
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
          'EasyExtend.langlets.p4d',
          'EasyExtend.langlets.p4d.lexdef',
          'EasyExtend.langlets.p4d.parsedef',
          'EasyExtend.langlets.p4d.reports',
          'EasyExtend.langlets.p4d.tests',
          'EasyExtend.langlets.teuton',
          'EasyExtend.langlets.teuton.lexdef',
          'EasyExtend.langlets.teuton.parsedef',
          'EasyExtend.langlets.teuton.reports',
          'EasyExtend.langlets.teuton.tests',
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
          'EasyExtend.util',
          'EasyExtend'],
        package_data = {'EasyExtend': ['exo.space', 'fs', 'Grammar', 'Token'],
           'EasyExtend.langlet_template': ['conf.py_template'],
           'EasyExtend.langlet_template.lexdef': ['lex_token.py_template', 'Token.ext'],
           'EasyExtend.langlet_template.parsedef': ['Grammar.ext'],
           'EasyExtend.langlets.coverage': ['test.log'],
           'EasyExtend.langlets.coverage.lexdef': ['Token', 'Token.ext'],
           'EasyExtend.langlets.coverage.parsedef': ['Grammar', 'Grammar.ext'],
           'EasyExtend.langlets.gallery.lexdef': ['Token', 'Token.ext'],
           'EasyExtend.langlets.gallery.parsedef': ['Grammar', 'Grammar.ext'],
           'EasyExtend.langlets.gallery.reports': ['gallery_test_gallery.ees'],
           'EasyExtend.langlets.gallery.tests': ['funcs.gal',
                                                 'test_gallery.gal',
                                                 'test_ip.gal'],
           'EasyExtend.langlets.grammar_langlet.lexdef': ['Token'],
           'EasyExtend.langlets.grammar_langlet.parsedef': ['Grammar'],
           'EasyExtend.langlets.p4d': ['flexutils.p4d'],
           'EasyExtend.langlets.p4d.lexdef': ['Token', 'Token.ext'],
           'EasyExtend.langlets.p4d.parsedef': ['Grammar', 'Grammar.ext'],
           'EasyExtend.langlets.p4d.reports': ['p4d_test.ees'],
           'EasyExtend.langlets.p4d.tests': ['p4d_football.p4d',
                                             'p4d_ogbuji.p4d',
                                             'p4d_soap.p4d',
                                             'soap_example.xml',
                                             'test_bytelet.p4d',
                                             'test_p4d.p4d'],
           'EasyExtend.langlets.teuton': ['demo.teu', 'umlaute.teu'],
           'EasyExtend.langlets.teuton.lexdef': ['Token', 'Token.ext'],
           'EasyExtend.langlets.teuton.parsedef': ['Grammar', 'Grammar.ext'],
           'EasyExtend.langlets.teuton.reports': ['sentinel.txt'],
           'EasyExtend.langlets.zero.lexdef': ['Token', 'Token.ext'],
           'EasyExtend.langlets.zero.parsedef': ['Grammar', 'Grammar.ext'],
           'EasyExtend.langlets.zero.reports': ['zero_test_creation.ees',
                                                'zero_test_cstgen.ees'],
           'EasyExtend.trail': trail_data},
    scripts=Scripts,
    ext_modules = ext_modules,
    ext_package = "EasyExtend\trail"
    )

