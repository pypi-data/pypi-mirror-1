from api import create, retrieve, retrieve_one, update, delete, count
import sqlalchemy as sa
from turbogears.database import session

class_test = 'isSqlAlchemyClass(class_)'
obj_test = 'isSqlAlchemyObject(obj)'


def isSqlAlchemyClass(class_):
    try:
        mapper = sa.orm.class_mapper(class_)
    except sa.exceptions.InvalidRequestError:
        return False
    return True
    
def isSqlAlchemyObject(obj):
    try:
        mapper = sa.orm.object_mapper(obj)
    except sa.exceptions.InvalidRequestError:
        
        return False
    return True

def sa_create(class_, **kw):
    try:
        obj = class_(**kw)
    except TypeError:
        obj = class_()
    sa_update(obj, **kw) # update takes care of save/flush
    return obj
sa_create = create.when(class_test)(sa_create)

def sa_retrieve(class_, **kw):
    return session.query(class_).select_by(**kw)
sa_retrieve = retrieve.when(class_test)(sa_retrieve)

def sa_retrieve_one(class_, **kw):
    r = sa_retrieve(class_, **kw)
    count = len(r)
    if count == 0:
        return None
    elif count == 1:
        return r[0]
    else:
        raise LookupError, 'Received %d results.' % count
sa_retreive_one = retrieve_one.when(class_test)(sa_retrieve_one)
    
def sa_update(obj, **kw):
    [setattr(obj, key, value) for key, value in kw.iteritems()]
    push_to_db(obj)
sa_update = update.when(obj_test)(sa_update)

def sa_delete(obj):
    session = session_for_obj(obj)
    session.delete(obj)
    session.flush()
sa_delete = delete.when(obj_test)(sa_delete)

def sa_count(class_, **kw):
    return session.query(class_).count_by(**kw)
sa_count = count.when(class_test)(sa_count)
    
def push_to_db(obj):
    session = session_for_obj(obj)
    session.save(obj)
    session.flush((obj,))
    
def session_for_obj(obj):
    s = sa.orm.session.object_session(obj)
    if not s:
        s = session
    return s
    
        
    

