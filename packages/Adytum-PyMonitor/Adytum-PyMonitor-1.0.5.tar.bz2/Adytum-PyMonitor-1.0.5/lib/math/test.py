INT_TO_DIGIT = [ x for x in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                 "_abcdefghijklmnopqrstuvwxyz~!'()*+"]
DIGIT_TO_INT = dict([ (y, x) for x, y in enumerate(INT_TO_DIGIT) ])  


def convert(n, newbase=70, oldbase=10):
    nums = [ DIGIT_TO_INT[x] for x in str(n) ]
    nums.reverse()
    r = 1
    total = 0
    for x in nums:
        total += r * x
        r *= oldbase
    if total == 0:
        return '0'
    
    converted = []
    while total:
        total, remainder = divmod(total, newbase)
        converted.append(INT_TO_DIGIT[remainder])
    
    converted.reverse()    
    return ''.join(converted)

    
if __name__ == '__main__':
    
    numbers10 = (1, 256, 3, 34534, 20050427123456, 0, 453532, 100)
    bases = (70, 16, 2, 7, 39)
    for n in numbers10:
        print "\ndealing with %s" %n
        for base in bases:
            nbase = convert(n, base, 10)
            n10 = convert(nbase, 10, base)
            print "base %2s: %40s" % (base, nbase)
            assert (int(n10) == n)
        print "base 10: %40s" % n10
