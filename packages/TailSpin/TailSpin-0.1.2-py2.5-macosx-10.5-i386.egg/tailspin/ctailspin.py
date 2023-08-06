from .ctailspin_h import helper

def ctailspin(func):
    func.recur = False
    def help(*args,**kw):
        return helper(func,args,kw)
    return help
