
from conf import*   # defines some fiber properties e.g. the console prompt, paths etc.
                    # import this module first if it imports symbol, token and tokenize modules!
import EasyExtend   # EasyExtend package
import PyGrammar    # contains fiber specific DFA tables used by the parser
from EasyExtend.csttools import*
from EasyExtend.eetransformer import Transformer, transform

class FiberTransformer(Transformer):
    '''
    Defines fiber specific transformations
    '''
    @transform
    def transit_command(self, node):
        return any_test(Name("Transit"))

if __name__ == '__main__':
    import sys
    import fiber              # import this fiber
    from session.TransitSession import TransitSession
    console = TransitSession()
    console.interact()


