import rel, optparse

def parse_input():
    parser = optparse.OptionParser('dez_test [-m MODULE]')
    parser.add_option("-p", "--port", dest="port", default="80", help="run test on PORT. default: 8888")
    parser.add_option("-d", "--domain", dest="domain", default="localhost", help="run test on DOMAIN. default: localhost")
    parser.add_option("-m", "--module", dest="module", help="test MODULE. required field. options: app_proxy, django_hello_world, echo_server, get_url, hello_client, http_client, http_client2, httpd_hello_world, http_proxy, new_conn, op_callback_server, op_callback_test, op_test, stomp_test, wsgi_test")
    parser.add_option("-f", "--function", dest="function", default="main", help="run this FUNCTION in test module. default: main")
    parser.add_option("-e", "--event", dest="event", default="pyevent", help="(event listener) notification method. default: pyevent. options: %s"%str(rel.supported_methods)[1:-1])
    parser.add_option("-r", "--report", action="store_true", dest="report", default=False, help="(event listener) status report every 5 seconds (non-pyevent only)")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="(event listener) verbose output")
    parser.add_option("-s", "--strict", action="store_true", dest="strict", default=False, help="(event listener) _only_ try specified notification method")
    return parser.parse_args()[0]

def main():
    options = parse_input()
    rel.override()
    rel_options = []
    if options.report:
        rel_options.append('report')
    if options.verbose:
        rel_options.append('verbose')
    if options.strict:
        rel_options.append('strict')
    rel.initialize([options.event],rel_options)
    try:
        testport = int(options.port)
    except:
        print 'error: non-integer port specified'
        return
    if not options.module:
        print "--module is required field"
        return
    testfile = options.module
    testfunc = options.function
    try:
        testmod = __import__("dez.samples.%s"%testfile,fromlist=["dez","samples"])
    except ImportError:
        print "invalid module specified"
        return
    if not hasattr(testmod, testfunc):
        print "invalid function specified"
        return
    testdomain = options.domain
    print 'running %s:%s on http://%s:%s'%(testfile,testfunc,testdomain,testport)
    getattr(testmod,testfunc)(domain=testdomain,port=testport)