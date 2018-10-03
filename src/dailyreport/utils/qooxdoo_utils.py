# -*- coding: utf-8 -*-

def get_item(dict, *args):
    """
    """
    result = None
    try:
        if len(args) > 0:
            result = dict
            for arg in args:
                result = result['$$user_' + arg]
    except:
        pass
    return result 

def has_key(dict, key):
    """
    
    """
    return dict.has_key('$$user_' + key)
