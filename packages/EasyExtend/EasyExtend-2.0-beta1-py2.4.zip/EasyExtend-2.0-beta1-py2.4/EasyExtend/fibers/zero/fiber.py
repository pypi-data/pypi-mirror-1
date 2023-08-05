from conf import*       # fiber specific modules ( symbol, token ) and objects ( prompt, pprint, unparse ...)
import EasyExtend       # EasyExtend package
import PyGrammar        # contains fiber specific DFA tables used by the parser
from EasyExtend.csttools import*   # tools used to manipulate CSTs
from EasyExtend.eetransformer import Transformer, transform


class FiberTransformer(EasyExtend.eetransformer.Transformer):
    '''
    Defines fiber specific transformations
    '''

__publish__ = []

if __name__ == '__main__':
    import fiber
    (options,args) = opt.parse_args()
    fiber.options  = options.__dict__
    if args:
        py_module = args[-1]
        EasyExtend.run_module(py_module, fiber)
    else:
        console = EasyExtend.create_console("ZERO", fiber)
        console.interact()
