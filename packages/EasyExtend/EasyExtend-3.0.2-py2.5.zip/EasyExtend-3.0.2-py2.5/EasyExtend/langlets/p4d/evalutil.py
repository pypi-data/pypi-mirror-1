import copy

def hide_bad_chars(s):
    return s.replace("'", '\x01').replace('"','\x02').replace('\n', '\x03')

def restringify(s):
    r = s.replace('\x01', "'").replace('\x02', '"').replace('\x03', '\n')
    if r:
        if r[0] == '"':
            return r.strip('"')
        elif r[0] == "'":
            return r.strip("'")
    return r

def objectify(obj):
    if hasattr(obj, "object_data"):
        return obj.object_data()
    else:
        return str(obj)

def eval_str(item, _globals, _locals):
    if isinstance(item, basestring):
        if item.startswith("evaltostr_"):
            return str(eval(item[10:], _globals, _locals))
        elif item.startswith("evaltonum_"):
            return eval(item[10:], _globals, _locals)
        elif item.startswith("restringify_"):
            return restringify(item[12:])
        return item
    else:
        return item


def mapeval(S, _globals, _locals):
    if isinstance(S, basestring):
        C = eval(S)
    else:
        C = S

    def eval_attr(container):
        for key, val in container.items():
            if isinstance(val, basestring):
                if val.startswith("evaltostr_"):
                    container[key] = str(eval(val[10:], _globals, _locals))
                elif val.startswith("evaltoobj_"):
                    obj = eval(val[10:], _globals, _locals)
                    container[key] = objectify(obj)
                elif val.startswith("restringify_"):
                    container[key] = eval(val[12:], _globals, _locals)

    def eval_all(container, pa, grandpa):
        # TODO: needs a more reliable algorithm.
        #       The following mess works within the bounds of the
        #       the tests but I suspect it's still broken.
        #
        from p4dbase import P4DContentList
        if isinstance(container, dict):
            eval_attr(container)
        elif isinstance(container, list):
            removable = False
            for i, item in enumerate(container):
                if isinstance(item, (dict, list)):
                    container[i] = eval_all(item, container, pa)
                elif isinstance(item, str):
                    obj = eval_str(item, _globals, _locals)
                    if obj is not item:
                        container[i] = obj
                    elif item.startswith("evaltoobj_"):
                        obj = eval(item[10:], _globals, _locals)
                        if hasattr(obj, "object_data"):
                            container[i] = obj.object_data()
                        elif hasattr(obj, "flow_value"):
                            pa[-1] = copy.copy(obj)
                            removable = True
                        else:
                            if isinstance(obj, (tuple, list)):
                                k = i
                                while True:
                                    if pa[0] == grandpa[k][0]:
                                        node = grandpa[k][:]
                                        break
                                    k+=1
                                data = eval_all([objectify(obj[0])],[],[])[0]
                                if isinstance(data, (int,float,basestring)):
                                    pa[-1] = data
                                    removable = True
                                else:
                                    container[i] = data
                                for item in obj[:0:-1]:
                                    elem = eval_all([objectify(item)], [],[])
                                    if isinstance(elem[0], (int,float,basestring)):
                                        obj = eval_str(elem[0],_globals,_locals)
                                        grandpa.insert(k+1, [node[0], dict(node[1]),[], obj])
                                    else:
                                        grandpa.insert(k+1, [node[0], dict(node[1]),elem, ''])
                            else:
                                if obj is not None:
                                    r = eval_str(obj, _globals, _locals)
                                    if pa[-1]:
                                        if isinstance(pa[-1], list):
                                            pa[-1].append(r)
                                        else:
                                            pa[-1] = P4DContentList([pa[-1], r])
                                    else:
                                        pa[-1] = r
                                removable = True
            if pa and removable:
                children = pa[2]
                for i in range(len(children))[::-1]:
                    if not type(children[i]) == list:
                        del pa[2][i]
        return container
    return eval_all(C,[],[])


