if __name__ == '__main__':
    import EasyExtend.util.pypackage as pypackage
    from test import test_support
    import sys
    pypackage.stdtest.importer = sys.modules["langlet"].importer
    pypackage.stdtest.test_contextlib.test_main()


