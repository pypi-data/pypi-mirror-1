

def mkcallback():
    collected = []
    def callback(obj, result, context):
        collected.append(context)
        return result
    return collected, callback


def mkcallbackwithcontext(suffix=''):
    collected = []
    def callback(obj, result, context):
        collected.append((obj, context))
        return result + suffix
    return collected, callback

