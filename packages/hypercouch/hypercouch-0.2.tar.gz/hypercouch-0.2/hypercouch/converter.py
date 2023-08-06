
import sys
import types
import couchdb

def view_wrapper(row):
    ret = to_unicode(row.get("doc"))
    if not isinstance(ret, types.DictType):
        row["doc"] = ret
    else:
        row["doc"] = couchdb.Document(ret)
    return row

def to_unicode(obj):
    if isinstance(obj, types.UnicodeType):
        return obj
    elif isinstance(obj, types.DictType):
        ret = {}
        for k, v in obj.iteritems():
            ret[to_unicode(k)] = to_unicode(v)
        return ret
    elif isinstance(obj, types.ListType):
        ret = []
        for v in obj:
            ret.append(to_unicode(v))
        return ret
    elif isinstance(obj, types.StringType):
        return obj.decode("utf-8")
    else:
        return obj
