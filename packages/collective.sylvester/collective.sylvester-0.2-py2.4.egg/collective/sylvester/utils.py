from time import time

def _cache_key_base(fun, obj, *args, **kwargs):
    """  
    Generic cache key
    """
    s_args = str(args)

    li = kwargs.items()
    li.sort()
    s_kwargs = str(li)

    #import logging
    #logger = logging.getLogger('sylvester')
    #logger.info("cache key: args = %s, kwargs = %s" % (s_args, s_kwargs))

    return "%s%s%s%s" % \
        (fun.func_name, str(obj.context.getPhysicalPath()), s_args, s_kwargs)

def cache_key_3600(fun, obj, *args, **kwargs):
    result = _cache_key_base(fun, obj, *args, **kwargs)
    return '%s%s' % (result, time()//3600)

def cache_key_60(fun, obj, *args, **kwargs):
    result = _cache_key_base(fun, obj, *args, **kwargs)
    return '%s%s' % (result, time()//60)
