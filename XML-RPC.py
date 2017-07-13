
# coding: utf-8

# In[ ]:

from xmlrpclib import ServerProxy
from xmlrpclib import Binary
from os.path import join,isfile
from SimpleXMLRPCServer import SimpleXMLRPCServer
from urlparse import urlparse
import sys

SimpleXMLRPCServer.allow_reuse_address = 1
MAX_HISTORY_LENTH = 6

OK = 1
FAIL = 2
EMPTY = ''

def getPort(url):
    '用url中提取端口'
    parsed = urlparse(url) 
    return int(parsed.port)

class Node:
    """
    P2P节点类
    """
    def __init__(self,url,dirname,secret):
        self.url = url
        self.dirname = dirname
        self.secret = secret
        self.known = set()
    
    def query(self,query,history=[]):
        """
        查询
        """
	print "Start query"
        code,data = self._handle(query)
        if code == OK:
            return code,data
        else:
            history = history + [self.url]
            if len(history) >= MAX_HISTORY_LENTH:
                return FAIL,EMPTY
            return self._broadcast(query,history)
        
    def hello(self,other):
        """用于将节点介绍给其他节点"""
        self.known.add(other)
        return OK
    
    def fetch(self,query,secret):
        """用于让节点找到文件并下载"""
        if secret != self.secret: return FAIL
        code,data = self.query(query)
        if code == OK:
            f = open(join(self.dirname,query),'wb')
            f.write(data.data)
            f.close()
            return OK
        else:
            return FAIL
        
    def _start(self):
        """启动服务"""
        s = SimpleXMLRPCServer(("",getPort(self.url)),logRequests=False)
        s.register_instance(self)
        s.serve_forever()
    
    def _handle(self,query):
        """处理请求"""
        dir = self.dirname
        name = join(dir,query)
        if not isfile(name): return FAIL,EMPTY
        return OK,Binary(open(name,'rb').read())
    
    def _broadcast(self,query,history):
        """广播"""
        for other in self.known.copy():
            if other in history :continue
            try:
                s = ServerProxy(other)
                code,data = s.query(query,history)
                if code ==OK:
                    return code,data
            except:
                self.known.remove(other)
        return FAIL,EMPTY
    
def main():
	url,directory,secret = sys.argv[1:]
	n = Node(url,directory,secret)
	n._start()
        
if __name__=='__main__':main()

