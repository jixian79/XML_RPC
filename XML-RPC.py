
# coding: utf-8

# In[ ]:

from xmlrpclib import ServerProxy,Fault
from xmlrpclib import Binary
from os.path import join,isfile,abspath
from SimpleXMLRPCServer import SimpleXMLRPCServer
from urlparse import urlparse
import sys

SimpleXMLRPCServer.allow_reuse_address = 1

MAX_HISTORY_LENTH = 6

UNHANDLED = 100
ACCESS_DENIED = 200

class UnhandledQuery(Fault):
    """表示无法处理的查询异常"""
    def __init__(self,message = "Couldn't handle the query"):
        Fault.__init__(self,UNHANDLED,message)
class AccessDenied(Fault)
    """用户试图访问未被授权的资源时引发的异常"""
    def __init__(self,message = "ACCESS DENIED"):
        Fault.__init__(self,ACCESS_DENIED,message)
        
def inside(pdir,name):
    """检查指定的目录中是否有给定的文件名"""
    pdir = abspath(pdir)
    name = abspath(name)
    return name.startswith(join(pdir,''))

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
        try:
            return self._handle(query)
        except UnhandledQuery:
            history = history + [self.url]
            if len(history) >= MAX_HISTORY_LENTH:raise
            return self._broadcast(query,history)
        
    def hello(self,other):
        """用于将节点介绍给其他节点"""
        self.known.add(other)
        return 0
    
    def fetch(self,query,secret):
        """用于让节点找到文件并下载"""
        if secret != self.secret: raise AccessDenied
        result = self.query(query)
        f = open(join(self.dirname,query),'wb')
        f.write(result.data)
        f.close()
        return 0
        
    def _start(self):
        """启动服务"""
        s = SimpleXMLRPCServer(("",getPort(self.url)),logRequests=False)
        s.register_instance(self)
        s.serve_forever()
    
    def _handle(self,query):
        """处理请求"""
        dir = self.dirname
        name = join(dir,query)
        if not isfile(name): raise UnhandledQuery
        if not inside(dir,name):raise AccessDenied
        return Binary(open(name,'rb').read())
    
    def _broadcast(self,query,history):
        """广播"""
        for other in self.known.copy():
            if other in history :continue
            try:
                s = ServerProxy(other)
                return s.query(query,history)
            except Fault,f:
                if f.faultCode = UNHANDLED:pass
                else:self.known.remove(other)
            except:
                self.known.remove(other)
        raise UnhandledQuery
        
    
def main():
	url,directory,secret = sys.argv[1:]
	n = Node(url,directory,secret)
	n._start()
        
if __name__=='__main__':main()

