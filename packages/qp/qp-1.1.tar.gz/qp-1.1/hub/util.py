"""
$URL: svn+ssh://svn.mems-exchange.org/repos/trunk/qp/hub/util.py $
$Id: util.py 26636 2005-04-21 10:11:07Z dbinger $
"""
import socket

def scgi_request(content, **headers):
    """(content:str, **headers) -> str
    This is intended for testing purposes, for use by send_scgi() (below).
    Returns an scgi-formatted request string using the given content and headers.
    """
    headers = '\0'.join(
        ['%s\0%s' % item for item in
         [('CONTENT_LENGTH', len(content)), ('SCGI', 1)] + headers.items()])
    return "%s:%s\0,%s" % (len(headers)+1, headers, content)

def send_scgi(port, host='localhost', content='',
              PATH_INFO='/', SCRIPT_NAME='', **kwargs):
    """
    This function *only* for testing the response of a running scgi server.
    It sends a request in scgi format and returns the beginning part of the
    response.  
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(scgi_request(content,
                        PATH_INFO=PATH_INFO,
                        SCRIPT_NAME=SCRIPT_NAME,
                        **kwargs))
    result = s.recv(1000)
    s.close()
    return result
