def start():
    try:
        import simple_server
    except:
        import traceback
        traceback.print_exc()
        reload(simple_server)
    else:
        try:
            simple_server.run(9889)
        except:
            import traceback
            traceback.print_exc()


from time import sleep
from mypy.reload_server import auto_reload
import sys
while 1:
    auto_reload(start)
    print "\nSleep 4 seconds"
    for i in xrange(10, 0, -1):
        sleep(0.4)
        print i,
    print ""
