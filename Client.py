# -*- coding: utf-8 -*-
from xmlrpclib import ServerProxy,Fault
from cmd import Cmd
from random import choice
from string import lowercase
from server import Node,UNHANDLED
from threading import Thread
from time import sleep
import sys

HEAD_START = 0.1# seconds
SECRET_LENGTH = 100

def randomString(length):
    """
    返回指定长度的由字母组成的随机字符串
    """
    chars = []
    letters = lowercase[:26]
    while length > 0:
        length -=1
        chars.append(choice(letters))
    return ''.join(chars)

class Client(Cmd):
    """
	Node类的简单基于文本的界面
    """
    prompt = '>'
    def __init__(self,url,dirname,urlfile):
        """
	设定Url，dirname，urlfile，并且在单独的线程中启动node服务器
        """
        Cmd.__init__(self)
        self.secret = randomString(SECRET_LENGTH)
        n = Node(url,dirname,self,secret)
        t = Thread(target=n._start)
        t.setDaemon(1)
        t.start()
        #让服务器先启动
        sleep(HEAD_START)
        self.server = ServerProxy(url)
        for line in open(urlfile):
            line = line.strip()
            self.server.hello(line)
        
    def do_fetch(self,arg):
        """
	调用服务器的fetch方法
        """
        try:
            self.server.fetch(arg,self.secret)
        except Fault,f:
            if f.faultCode != UNHANDLED:raise
            print "Couldn't find the file",arg
            
    def do_exit(self,arg):
        "退出程序"
        print
        sys.exit()
        
    do_EOF = do_exit
    
def main():
    urlfile,directory,url = sys.argv[1:]
    client = Client(url,directory,urlfile)
    client.cmdloop()
    
if __name__=='__main__':main
