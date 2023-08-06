from dez.http.application import HTTPApplication
import rel

def main():
    rel.override()
    rel.initialize(['select'])
    a = HTTPApplication("", 8888)
    a.add_proxy_rule('/', 'www.brbx.com', 80)
    a.add_static_rule('/static/', '.')
    a.start()    
    
    
if __name__ == "__main__":
    main()