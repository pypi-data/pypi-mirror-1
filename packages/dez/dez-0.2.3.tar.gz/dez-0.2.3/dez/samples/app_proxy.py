from dez.http.application import HTTPApplication

def main(port):
    a = HTTPApplication("", port)
    a.add_proxy_rule('/', 'www.brbx.com', 80)
    a.add_static_rule('/static/', '.')
    a.start()    

