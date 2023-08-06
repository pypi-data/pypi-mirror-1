from lamson.routing import route, route_like
from lamson.spam import spam_filter


ham_db = "tests/sddb"

@route("(anything)@(host)", anything=".+", host=".+")
@spam_filter(ham_db, "tests/.hammierc", "run/queue")
def START(message, **kw):
    print "Ham message received. Going to END."
    return END

@route_like(START)
def END(message, *kw):
    print "Done."
