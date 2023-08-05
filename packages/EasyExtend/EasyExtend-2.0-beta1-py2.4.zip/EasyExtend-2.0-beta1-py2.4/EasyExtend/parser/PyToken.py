from EasyExtend.eetoken import*

FIBER_OFFSET = 0

class FiberToken(EEToken):
    def __new__(cls):
        EEToken.__new__(cls)
        return cls


