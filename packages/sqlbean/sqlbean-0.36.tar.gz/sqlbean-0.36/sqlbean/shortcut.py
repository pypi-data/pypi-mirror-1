from decorator import decorator

from sqlbean.db.query import Query
from sqlbean.db.mc import mc,MMcCache,McCache
from sqlbean.db.relations import ForeignKey,OneToMany
from sqlbean.model import Model
from sqlbean.mcmodel import McModel

def transaction(func):
    def  _func(func,*args, **kwds):
        Query.begin()
        try:
            result = func(*args, **kwds)
            Query.commit()
            return result
        except:
            Query.rollback()
            raise
    return decorator(_func, func)
