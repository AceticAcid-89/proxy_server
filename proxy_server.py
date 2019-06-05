# ! /usr/bin/env python2.7
# encoding: utf-8


import eventlet
from eventlet import wsgi
import requests
import traceback

from webob import Request
from webob import Response

USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.1.1; ' \
             'Nexus 7 Build/JRO03D) AppleWebKit/535.19 ' \
             '(KHTML, like Gecko) Chrome/18.0.1025.166 ' \
             'Safari/535.19'


class ProxyHandler(object):

    def __call__(self, environ, start_process):
        url_list = []
        req = Request(environ)

        url = req.path.strip("/")
        if not url.startswith("http"):
            https_url = "https://" + url
            http_url = "http://" + url
            url_list.extend([https_url, http_url])
        else:
            url_list.append(url)

        action = req.method

        kwargs = dict()

        data = req.body
        kwargs["data"] = data
        headers = req.headers
        kwargs["headers"] = {}
        kwargs["headers"].update(headers)
        if kwargs["headers"].get("User-Agent", None):
            kwargs["headers"]["User-Agent"] = USER_AGENT

        if kwargs["headers"].get("Host", None):
            kwargs["headers"].pop("Host")

        # set timeout
        kwargs["timeout"] = 5

        # print info
        print("request url=%s" % url)
        print(kwargs)

        response = Response()
        for req_url in url_list:

            proxy_res = requests.request(action, req_url, **kwargs)
            if 200 <= proxy_res.status_code < 300:

                response.status_code = proxy_res.status_code
                response.body = proxy_res.content
                return response(environ, start_process)
            else:
                print("error occurred with url:%s" % req_url)
                continue
        else:
            response.status_code = 404
            response.body = "class not found"
            return response(environ, start_process)


class ProxyServer(object):

    def __init__(self, proxy_ip, proxy_port):
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.app = ProxyHandler()

    def start_server(self):

        _socket = eventlet.listen((self.proxy_ip, self.proxy_port))
        wsgi.server(_socket, site=self.app, max_size=50)


def main():
    ip = "0.0.0.0"
    port = 8890
    try:
        proxy_server = ProxyServer(ip, port)
        proxy_server.start_server()
    except BaseException as e:
        print(e, traceback.format_exc())


if __name__ == '__main__':
    main()
