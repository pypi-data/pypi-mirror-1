
def START():
    return RECOVERED

def RECOVERED(db, message, args):
    return SECOND_RECOVER

def SECOND_RECOVER(db, message, args):
    return THIRD_RECOVER

def THIRD_RECOVER(db, message, args):
    return END

def END():
    """Does nothing but just stays in END."""
