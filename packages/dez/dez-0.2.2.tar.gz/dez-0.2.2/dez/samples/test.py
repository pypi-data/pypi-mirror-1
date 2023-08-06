def main():
    import rel, sys
    rel.override()
    sys.argv.pop(0)
    try:
        if len(sys.argv) == 0:
            print """
    arg 1 (test) - required:
        app_proxy
        django_hello_world
        echo_server
        get_url
        hello_client
        http_client
        http_client2
        httpd_hello_world
        http_load_test
        http_proxy
        new_conn
        op_callback_server
        op_test
        stomp_test
        wsgi_test
    arg2 (port) - optional:
        default: 8888
    arg3 (function) - optional:
        default: main
    arg4 (event notification method) - optional:
        default: pyevent
        epoll
        poll
        select
    arg5+ (options) - optional:
        report (non-pyevent only)
        verbose
                  """
            return
        testfile = sys.argv.pop(0)
        testport = 8888
        if len(sys.argv) > 0:
            try:
                testport = int(sys.argv.pop(0))
            except:
                print 'error: non-integer port specified'
                return
        testfunc = 'main'
        if len(sys.argv) > 0:
            testfunc = sys.argv.pop(0)
        if len(sys.argv) > 0:
            method = sys.argv.pop(0)
            rel.initialize([method],sys.argv)
        testmod = __import__("dez.samples.%s"%testfile,fromlist=["dez","samples"])
        print 'running %s:%s on %s'%(testfile,testfunc,testport)
        getattr(testmod,testfunc)(testport)
    except ImportError:
        print "invalid input"

if __name__ == "__main__":
    main()
