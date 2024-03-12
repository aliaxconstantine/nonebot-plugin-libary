import random
from collections import defaultdict
class Books:
    def __init__(self) -> None:
        self.id = list()
        self.books = defaultdict()
    
    def setAllId(self):
        """
        设置id
        """
        for bookurl in self.books:
            getid = random.randint(0,99999)
            for id in self.id:
                if(getid == id):
                    getid = random.randint(0,99999)
            
            self.id.append(getid)
            self.books[bookurl].update({"id":getid})

    def getUrl(self,getid)->dict:
        """
        根据id获取url
        """
        for ud in self.books:
            if(getid == self.books[ud]['id']):
                return {'id':str(ud),"busid":self.books[ud]['busid'],'group_id':self.books[ud]['group_id']}
        return 'error'


class Libarylist:
    librarytime = ""
    ifread = True
    librarylist = defaultdict()

    @classmethod
    def setAllNone(cls):
        if(not Libarylist.librarylist):
            return False
        for name in Libarylist.librarylist:
            id = Libarylist.librarylist[name] 
            Libarylist.librarylist[name] = {"is":False,"id":id}

    @classmethod
    def isgroup(cls,gid):
        """
        判断群组是否存在
        True:群组存在
        False:群组不存在
        """
        if(Libarylist.librarylist):
            for name in Libarylist.librarylist:
                if(Libarylist.librarylist[name]['id'] == int(gid)):
                    return True
            return False
    
    @classmethod
    def settrue(cls,gid):
        """
        设置群组允许被读取文件
        """
        if(not Libarylist.librarylist):
            return False
        for name in Libarylist.librarylist:
            if(Libarylist.librarylist[name]['id'] != int(gid)):
                continue
            id = Libarylist.librarylist[name]['id'] 
            Libarylist.librarylist[name] = {"is":True,"id":id}

    @classmethod
    def istrue(cls,gid):
        """
        判断群组是否允许被读取文件
        True:群组允许被读取文件
        False:群组不允许被读取文件
        """
        if(Libarylist.librarylist):
            for name in Libarylist.librarylist:
                if(Libarylist.librarylist[name]['id'] == int(gid) and Libarylist.librarylist[name]['is'] == True):
                    return True
            return False

libraryA = Books()
LIBARYID = defaultdict()

