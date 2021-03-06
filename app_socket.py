# -*- enconding: utf-8 -*-
import socket
import sys
import time
import pages

PORT=8080

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", PORT))
s.listen(1)

version_system = "CCO-130 Socket"
version_http = "HTTP/1.1"

html_error_template = '''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
           <html><head>
           <title>%(ret_code)d %(msg_short)s</title>
           </head><body>
           <h1>%(msg_short)s</h1>
           <p>%(msg_long)s<br />
           </p>
           </body></html>'''

return_codes = {
    200: ('OK','OK'),
    400: ('Bad Request', 'Your browser sent a request that this server could not understand'),
    404: ('Not Found','Page not found'),
    500: ('Internal Server Error', 'We have problems, :('),
}

def do_GET(caminho, options):

    #troca "index.html" por "index_html"
    name_page = caminho.replace(b'.',b'_')
    name_page = name_page.replace(b'/',b'').decode("UTF-8")
    print(name_page, options)

    if hasattr(sys.modules[pages.__name__], "%s" % name_page):
        body = getattr(sys.modules[pages.__name__], "%s" % name_page)()
    elif name_page == '':
        body = pages.index_html()
    else:
        head, body = send_error(404)
        return head, body


    head = (
                '%s %d %s\r\nServer: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nDate: %s\r\nConnection: keep-alive\r\n\r\n' %
                (
                    version_http,
                    200,
                    return_codes[200][0],
                    version_system,
                    len(body),
                    date_time_string()
                )
                ).encode("utf-8")
    return head, body

def do_HEAD(caminho, options):

    #troca "index.html" por "index_html"
    name_page = caminho.replace(b'.',b'_')
    name_page = name_page.replace(b'/',b'').decode("UTF-8")
    print(name_page)

    if hasattr(sys.modules[pages.__name__], "%s" % name_page):
        body = getattr(sys.modules[pages.__name__], "%s" % name_page)()
    elif name_page == '':
        body = pages.index_html()
    else:
        head, body = send_error(404)
        return head, body


    head = (
                '%s %d %s\r\nServer: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nDate: %s\r\nConenction: close\r\n\r\n' %
                (
                    version_http,
                    200,
                    return_codes[200][0],
                    version_system,
                    len(body),
                    date_time_string()
                )
                ).encode("utf-8")

    return head, ""

def send_error(ret_code):
    print(ret_code)
    msg_short, msg_long = return_codes[ret_code]

    body = (html_error_template % {'ret_code': ret_code, 'msg_short': msg_short, 'msg_long': msg_long}).encode("utf-8")

    head = ('%s %d %s\r\nServer: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nDate: %s\r\nConenction: close\r\n\r\n' %
                (
                version_http,
                ret_code,
                msg_short,
                version_system,
                len(body),
                date_time_string()
                )
            ).encode("utf-8")
    return head, body

def date_time_string(timestamp=None):

    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
    weekdayname[wd],
    day, monthname[month], year,
    hh, mm, ss)
    return s


while True:
    cli, addr = s.accept()


    while True:
        try:
            req = b''
            while not (b'\r\n\r\n' in req or b'\n\n' in req):
                req += cli.recv(1024)
            if req == '':
                break

            print(req)
            print('requisição tem %d bytes' % len(req))

            metodo, caminho, options = req.split(b' ', 2)

            metodoStr = metodo.decode("utf-8")
            if hasattr(sys.modules[__name__], "do_%s" % metodoStr):
                head, body = getattr(sys.modules[__name__], "do_%s" % metodoStr )(caminho,options)
            else:
                head, body = send_error(400)
        except ValueError:
            head, body = send_error(400)
        except:
            head, body = send_error(500)
        finally:
            print("Chegou Aqui\n %s \n%s" % (head, body))
            cli.send(head)
            cli.send(body)
            break

    cli.close()
    print('<conexao fechada>')
