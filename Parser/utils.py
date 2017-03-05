
def fold_right(f, init, lst):
    if not lst:
        return init
    
    return f(lst[0], fold_right(f, init, lst[1:]))


def fold_left(f, init, lst):

    def helper(result, rest):
        if not rest:
            return result
        
        return helper(f(result, rest[0]), rest[1:])
    
    return helper(init, lst)

    