from conf import*            # fiber specific modules ( symbol, token ) and objects ( prompt, pprint, unparse ...)
from EasyExtend.csttools import*   # tools used to manipulate CSTs

class FiberTransformer(Transformer):
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
        console = EasyExtend.create_console(fiber_name, fiber)
        console.interact()
