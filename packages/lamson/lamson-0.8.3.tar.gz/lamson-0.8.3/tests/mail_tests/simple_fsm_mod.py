# for the test this expects to have var1 and var2 to print as globals

def START():
    return TEST

def TEST(p):
    print p
    print var1
    print var2

    if p == "error":
        raise RuntimeError
    elif p == "reset":
        return END
    else:
        return NEXT

def NEXT(p):
    print p
    print var2
    print var1
    return END

def END(p):
    print "Ended"

def ERROR(exc, state):
    print "Got an exception", exc, "at state", state
    return END

