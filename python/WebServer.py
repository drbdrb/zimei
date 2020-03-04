#!/usr/bin/python3
import os
import importlib
import sys
import json
import re
import gc
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process

#-------------------------------------------------------------------------------

class ServerException(Exception):
    '''服务器内部错误'''
    pass

#-------------------------------------------------------------------------------

class base_case(object):
    '''条件处理基类'''

    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content, handler.mimetype)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'

#-------------------------------------------------------------------------------

class case_no_file(base_case):
    '''文件或目录不存在'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))

#-------------------------------------------------------------------------------

class case_cgi_file(base_case):
    '''可执行脚本'''

    def run_cgi(self, handler):
        module = os.path.basename(handler.path)[:-3]

        package = importlib.import_module(r'.'+ module, package='webroot.api')
        moduleClass = getattr(package, module)
        process = moduleClass(handler)
        data = process.main()
        del package,moduleClass,process
        gc.collect()

        mimetype = handler.mimetype
        status = 200
        handler.send_content(data.encode("utf-8"), mimetype, status)

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self, handler):
        self.run_cgi(handler)

#-------------------------------------------------------------------------------

class case_existing_file(base_case):
    '''文件存在的情况'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)

#-------------------------------------------------------------------------------

class case_directory_index_file(base_case):
    '''在根路径下返回主页文件'''

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))

#-------------------------------------------------------------------------------

class case_always_fail(base_case):
    '''默认处理'''

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

#-------------------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):

    Http_Root = os.path.dirname(os.path.abspath(__file__)) + '/webroot'

    '''
    请求路径合法则返回相应处理
    否则返回错误页面
    '''
    Cases = [case_no_file(),
             case_cgi_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]

    # 错误页面模板
    Error_Page = """\
        <html>
        <body>
        <h1>访问错误 {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    Mimedic = [
        ('.html', 'text/html'),
        ('.htm', 'text/html'),
        ('.py', 'text/html'),
        ('.js', 'application/javascript'),
        ('.css', 'text/css'),
        ('.json', 'application/json'),
        ('.png', 'image/png'),
        ('.jpg', 'image/jpeg'),
        ('.gif', 'image/gif'),
        ('.txt', 'text/plain'),
        ('.avi', 'video/x-msvideo'),
    ]

    # 处理身份验证
    def do_OPTIONS(self):
        result = parse.urlparse(self.path)
        self.path  = result.path
        if result.query:
            self.query = result.query
        self.handle_request()

    # 处理GET请求
    def do_GET(self):
        result = parse.urlparse(self.path)
        self.path  = result.path
        self.query = result.query
        self.handle_request()

    # 处理POST请求
    def do_POST(self):
        result = parse.urlparse(self.path)
        self.path  = result.path
        self.query = ''
        if result.query:
            self.query = result.query
        req_datas = self.rfile.read(int(self.headers['content-length'])) #重点在此步!
        query = req_datas.decode()
        query_dict = {}
        if len(query)>0:
            try:
                query_dict = json.loads(query)
                for qkey in query_dict:
                    self.query += '&' + str(qkey) + '=' + query_dict[qkey]
                self.query = self.query.strip('&')
            except:
                pass
        self.handle_request()

    def handle_request(self):
        try:
            # 得到完整的请求路径
            self.full_path = self.Http_Root + self.path

            self.mimetype = ''
            filename, fileext = os.path.splitext(self.full_path)
            for e in self.Mimedic:
                if e[0] == fileext:
                    self.mimetype = e[1]
            del filename,fileext

            # 遍历所有的情况并处理
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break

        # 处理异常
        except Exception as msg:
            self.handle_error(msg)


    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode("utf-8"), self.mimetype, 404)

    # 发送数据到客户端
    def send_content(self, content, mimetype='', status=200):
        self.send_response(status)

        if mimetype != '':
            self.send_header("Content-type", mimetype)
        self.send_header("Content-Length", str(len(content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "X-Token")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        self.end_headers()
        self.wfile.write(content)

#-------------------------------------------------------------------------------
class WebServer():
    '''HTTP服务器类'''

    def start(self):
        # http.server 使用stderr.write写日志。故转发到空设备屏蔽之
        serverAddress = ('0.0.0.0', 8088)
        server = HTTPServer(serverAddress, RequestHandler)
        server.serve_forever()

    # 开始运行
    def Run(self, argv=''):
        if argv.lower() != 'debug':
            sys.stderr = open(os.devnull, 'w')
        p = Process(target=self.start)
        p.start()


if __name__ == '__main__':
    argv = ''
    if len(sys.argv) > 1:
        argv = sys.argv[1]
    # Web服务器
    webser = WebServer()
    webser.Run(argv)
