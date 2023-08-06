

def callvalues(function, *args, **kwargs):
    """ profiling plugin to return result values of all invokations """
    result = function(*args, **kwargs)
    return [result], result


def callcounter(function, *args, **kwargs):
    """ profiling plugin to simply count the number of invokations """
    return 1, function(*args, **kwargs)

