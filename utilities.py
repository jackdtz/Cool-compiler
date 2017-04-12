def align(n, alignment):
    if n % alignment == 0:
        return n
    
    return n + (alignment - (n % alignment))