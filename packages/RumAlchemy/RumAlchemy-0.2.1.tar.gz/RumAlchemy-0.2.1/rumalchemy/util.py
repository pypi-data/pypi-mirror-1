from sqlalchemy.orm import class_mapper, object_mapper
from rum import app

#from sqlalchemy.orm.exc import UnmappedError

__all__ = ["get_mapper", "get_foreign_keys"]

def get_mapper(obj):
    try: return class_mapper(obj)
    except:
        try: return object_mapper(obj)
        except: return None


def get_foreign_keys(prop):
    # This wrapper is to support both SA 0.5 and <
    try:
        return prop._foreign_keys # 0.5
    except AttributeError:
        return prop.foreign_keys # 0.4
    #XXX Why did SA "privatize" foreign_keys??

def primary_key_property_names(obj):
    mapper = get_mapper(obj)
    assert mapper
    return [p.key for p in mapper.iterate_properties if hasattr(p,"columns")\
       and len([c for c in p.columns if c.primary_key])>0]

def version_id_name(obj):
    mapper = get_mapper(obj)
    assert mapper
    col = mapper.version_id_col
    if col:
        return col.key

def get_dialect_name():
    try:
        return app.repositoryfactory.session_factory.bind.dialect.name
    except AttributeError:
        return "GENERIC"