from EasyExtend.eetoken import*

class FiberToken(EEToken):
    def __new__(cls):
        EEToken.__new__(cls)
        cls.PATH_PREFIX_p = (100, 'p', STR_PREFIX)
        cls.PATH_PREFIX_P = (101, 'P', STR_PREFIX)
        cls.SIGIL = (102, '$', OPERATOR)
        cls.FAT_TOKEN = (103,r'(?P<fat_token>(\w+\-\w+))', FAT_MODE)
        cls.QUESTIONMARK = (104, '?', OPERATOR)
        return cls


