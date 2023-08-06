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

def mapeval(S, _globals, _locals):
    if isinstance(S, basestring):
        C = eval(S)
    else:
        C = S
    def eval_all(container, pa, grandpa):
        if isinstance(container, dict):
            for key, val in container.items():
                if isinstance(val, str):
                    if val.startswith("evaltostr_"):
                        container[key] = str(eval(val[10:], _globals, _locals))
                    elif val.startswith("evaltoobj_"):
                        obj = eval(val[10:], _globals, _locals)
                        container[key] = objectify(obj)
                    elif val.startswith("restringify_"):
                        container[key] = eval(val[12:], _globals, _locals)
                elif isinstance(val, (dict, tuple, list)):
                    container[key] = eval_all(val, container, pa)
        elif isinstance(container, list):
            for i, item in enumerate(container):
                if isinstance(item, (dict, list)):
                    container[i] = eval_all(item, container, pa)
                elif isinstance(item, str):
                    if item.startswith("evaltostr_"):
                        container[i] = str(eval(item[10:], _globals, _locals))
                    elif item.startswith("evaltoobj_"):
                        obj = eval(item[10:], _globals, _locals)
                        if type(obj) == int:
                            container[i] = str(obj)
                        else:
                            if hasattr(obj, "object_data"):
                                container[i] = obj.object_data()
                            else:
                                if isinstance(obj, (tuple, list)):
                                    node = grandpa[i][:]
                                    data = eval_all([objectify(obj[0])],[],[])[0]
                                    if isinstance(data, str):
                                        pa[-1] = data
                                        del container[i]
                                    else:
                                        container[i] = data
                                    for item in obj[:0:-1]:
                                        elem = eval_all([objectify(item)], [],[])
                                        if isinstance(elem[0], str):
                                            grandpa.insert(i+1, [node[0], dict(node[1]),[], elem[0]])
                                        else:
                                            grandpa.insert(i+1, [node[0], dict(node[1]),elem, ''])
                                else:
                                    container[i] = obj
                    elif item.startswith("restringify_"):
                        container[i] = restringify(item[12:])
        return container
    return eval_all(C,[],[])

def maybeval(S, _globals, _locals):
    if isinstance(S, basestring):
        return eval(S, _globals, _locals)
    return S

def evalto(S, _globals, _locals):
    if isinstance(S, basestring):
        if S.startswith("evaltostr_"):
            return str(eval(S[10:], _globals, _locals))
        elif item.startswith("evaltoobj_"):
            return eval(S[10:], _globals, _locals)
    return S


