# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    12 Nov 2006

import symbol as py_symbol
import token as py_token
import cst

class FSConfig(object):
    '''
    Used to supply information about the state of the fiberspace
    in terms of data provided by individual fibers.
    '''
    fiber_table = [ {"offset":0, "symbol":py_symbol, "token":py_token} ]

    @classmethod
    def get_sym_name(cls, node_id):
        if node_id < 512:
            nids = [row["offset"]+node_id for row in cls.fiber_table]
        else:
            nids = [node_id]
        for row in cls.fiber_table:
            for nid in nids:
                name = row["symbol"].sym_name.get(nid)
                if name:
                    return name
        return ""

    @classmethod
    def get_tok_name(cls, node_id):
        if node_id < 512:
            nids = [row["offset"]+node_id for row in cls.fiber_table]
        else:
            nids = [node_id]
        for row in cls.fiber_table:
            for nid in nids:
                name = row["token"].tok_name.get(nid)
                if name:
                    return name
        return ""


