

def maybe_list(arg):
    """ Make sure arg is a list, if it's a single value
    wrap it into a list. """
    if hasattr(arg, '__iter__'):
        return arg
    if arg is None:
        return []
    return [arg]


def list_merge(*args):
    """ Merge arguments into a new list. """
    result_list = []
    for sublist in args:
        result_list += maybe_list(sublist)
    return result_list


def list_to_dict(*args, **kwargs):
    value = kwargs.get("value", True)
    return dict([(key, value) for key in list_merge(*args)])
