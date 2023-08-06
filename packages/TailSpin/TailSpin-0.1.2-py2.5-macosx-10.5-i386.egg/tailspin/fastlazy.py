from .fastlazy_h import helper,force

def tail(func):
    func.recur = False
    def help(*args,**kw):
        return helper(func,args,kw)
    return help

__all__ = ['tail','force']
