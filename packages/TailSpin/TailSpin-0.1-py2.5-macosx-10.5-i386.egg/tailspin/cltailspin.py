from .cltailspin_h import helper

def cltailspin(func):
    func.recur = False
    def help(*args,**kw):
        return helper(func,args,kw)
    return help

def force(thing):
    thing.__force__()
