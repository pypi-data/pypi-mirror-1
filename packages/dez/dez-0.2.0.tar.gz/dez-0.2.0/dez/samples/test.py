def main():
    import sys
    sys.argv.remove(sys.argv[0])
    try:
        testfile = sys.argv[0]
        testfunc = 'main'
        if len(sys.argv) > 2:
            testfunc = sys.argv[1]
        testmod = __import__("dez.samples.%s"%testfile,fromlist=["dez","samples"])
        getattr(testmod,testfunc)()
    except ImportError:
        print "invalid input"

if __name__ == "__main__":
    main()
