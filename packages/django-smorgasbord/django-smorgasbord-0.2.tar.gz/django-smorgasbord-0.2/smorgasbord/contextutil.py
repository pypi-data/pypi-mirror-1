
def context_to_dict(ctxt):
    res={}
    for d in reversed(ctxt.dicts):
        res.update(d)
    return res

