from nonebot import get_driver,get_bot
from nonebot.plugin import PluginMetadata
from nonebot import on_command,on_startswith,on_endswith
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.params import CommandArg
from .LibaryPojo import *
from .QService import *
import datetime
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v12 import GroupMessageEvent
from .config import Config,GROUP_LIST,L_MANGER_GROUP_ID
from nonebot import logger
from nonebot.permission import SUPERUSER
import asyncio
from .QService import del_group_file,get_groupfolder_massage,get_allfile
import os
import json
import concurrent.futures
__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_libaryManger",
    description="用于管理q群文件的插件",
    usage="",
    config=Config,
)

L_SESSION = None
global_config = get_driver().config
config = Config.parse_obj(global_config)
#读取配置
l_config = os.path.join("data","libarySetting.json")

def init_config():
    global GROUP_LIST
    if not os.path.exists(l_config):
        #创建文件
        if not os.path.exists("data"):
            os.mkdir("data")
        with open(l_config, "w",encoding= "utf8") as f:
            f.write(json.dumps({"图书馆":{}},ensure_ascii=False))
    else:
        with open(l_config, "r",encoding ="utf8") as f:
            config_data = json.load(f)
            GROUP_LIST = config_data["图书馆"]

def task_asyn(tasks):
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as ts:
        for task in tasks:
            ts.submit(task[0],task[1])

#初始化图书馆
libary_init = on_command("图书馆初始化", rule=to_me(), aliases={"初始化图书馆", "图书馆初始化"}, priority=10, block=True, permission=SUPERUSER,)
#图书馆存档
libary_save = on_command("图书馆存档", rule=to_me(), aliases={"存档图书馆", "图书馆存档"}, priority=10, block=True,permission=SUPERUSER,)
#图书馆加群
libary_add = on_command("图书馆加群", rule=to_me(), aliases={"加群图书馆", "图书馆加群"}, priority=10, block=True, permission=SUPERUSER,)
#图书馆查找
libary_find = on_command("图书馆查找", rule=to_me(), aliases={"查找图书馆","图书查找","查找图书","查找", "图书馆查找"}, priority=10, block=True)
#图书馆清空
libary_clear = on_command("图书馆清空", rule=to_me(), aliases={"清空图书馆", "图书馆清空"}, priority=10, block=True,permission=SUPERUSER)
#图书馆打开
libary_open = on_command("图书馆打开", rule=to_me(), priority=10, block=True)
#图书馆日志
libary_log = on_command("图书馆日志", rule=to_me(), aliases={"图书馆日志", "图书日志"}, priority=10, block=True)

#定时器 在定时进行存档
@scheduler.scheduled_job("cron", hour=23 , id="job_0")
async def send_message_to_group():
    global L_MANGER_GROUP_ID
    global L_SESSION
    if(Libarylist.ifread == False):
        return
    if(SESSION == None):
        return
    #设置初始化时间
    Libarylist.librarytime = str(datetime.datetime.now())
    Libarylist.ifread = False
    #初始化时资源禁止访问
    librarylist = Libarylist.librarylist
    logger.error(librarylist)
    for groupname in librarylist:
        groupid = librarylist[groupname]['id'] 
        if(Libarylist.istrue(groupid)):
            data = await get_allfile(groupid,libary_save)
            if(data == None):
                return
            libraryA.books.update(data)
    libraryA.setAllId()
    Libarylist.ifread = True
    SESSION.send_group_msg(groupid=L_MANGER_GROUP_ID,message="图书馆存档成功")

@libary_init.handle()
async def init_function(bot:Bot,args: Message = CommandArg()):
    global LIBARYID
    global SESSION
    SESSION = bot
    #读取配置
    init_config()
    #将bot所有群加入
    Libarylist.librarylist = await get_groups(bot)
    LIBARYID = Libarylist.librarylist

    Libarylist.setAllNone()
    #将配置到的群号全部选为图书馆
    for groupid in GROUP_LIST:
        Libarylist.settrue(GROUP_LIST[groupid])
    return await libary_init.finish("图书馆初始化成功"+"\n"+get_help())


def fresh_list(groupid):
    data = get_allfile(groupid)
    if(data != None):
        libraryA.books.update(data)
        libraryA.setAllId()

@libary_save.handle()
async def save_function(bot:Bot,args: Message = CommandArg()):
    if(Libarylist.ifread == False):
        return await libary_save.finish("图书馆正在存档中"+"\n"+get_help())
    if(len(Libarylist.librarylist)<1):
        return await libary_save.finish("图书馆未进行初始化,请联系bot管理员。"+"\n"+get_help())
    await libary_save.send("图书馆存档中,请稍后......"+"\n"+get_help())
    #设置初始化时间
    Libarylist.librarytime = datetime.datetime.now()
    Libarylist.ifread = False
    #初始化时资源禁止访问
    librarylist = Libarylist.librarylist
    flasks= []
    for groupname in librarylist:
        groupid = librarylist[groupname]['id'] 
        if(Libarylist.istrue(groupid)):
            flasks.append([fresh_list,groupid])
    task_asyn(flasks)
    Libarylist.ifread = True
    newtime = datetime.datetime.now()-Libarylist.librarytime
    return await libary_save.finish(f"图书馆存档完毕,本次存档时间为:{newtime.seconds}s"+"\n"+get_help())

@libary_find.handle()
async def find_function(args: Message = CommandArg()):
    if(Libarylist.ifread == False):
        return await libary_find.finish("图书馆正在存档中"+"\n"+get_help())
    booklist = list()
    for id in libraryA.books:
        data = libraryA.books[id]
        if(args.extract_plain_text() in data['name']):
            booklist.append(data['name']+":"+str(data['id']))
        if(booklist is None):                         
            return await libary_find.finish("未找到相关图书"+"\n"+get_help())  
    if len(booklist) < 20:
        return await libary_find.finish("---------目录--------\n"+"\n".join(booklist))
    else:
        booklist = [booklist[i:20+i] for i in range(0, len(booklist), 20)]
        for i in booklist:
            await libary_find.send("---------目录--------\n"+"\n".join(i))
    return await libary_find.finish("已查到"+str((len(booklist)-1)*20+len(booklist[-1]))+"条记录"+"\n"+get_help())

@libary_clear.handle()
async def clear_function(args: Message = CommandArg()):
    if(Libarylist.ifread == False):
        return await libary_find.finish("图书馆正在存档中"+"\n"+get_help())
    oldtime = datetime.datetime.now()
    if(libraryA.books):
        await libary_find.send("图书馆清理中----"+"\n"+get_help())
        #获得一个图书分组
        ls = list(libraryA.books.items())
        list_new = [ls[i:60+i] for i in range(0,len(ls),60)]
        tasks = []
        for grouop in list_new:
            tasks.append([group_del,dict(grouop)]) 
        task_asyn(tasks)
    newtime = datetime.datetime.now() - oldtime
    return await libary_clear.finish(f"图书馆清空成功,本次清理时间为{newtime.seconds}s"+"\n"+get_help())

def group_del(grouop):
    for ud in grouop:
        file_data = libraryA.getUrl(libraryA.books[ud]['id'])
        url = send_file(file_data['group_id'],file_data['id'],file_data["busid"])
        if(url is None):
            del_group_file(file_data['group_id'],file_data['id'],file_data["busid"])



@libary_add.handle()
async def add_function( event: GroupMessageEvent ):
    if(Libarylist.ifread == False):
        return await libary_find.finish("图书馆正在存档中"+"\n"+get_help())
    gid = event.group_id
    if(not Libarylist.isgroup(gid)):
        return await libary_add.finish("图书馆已存在该群号"+"\n"+get_help())
    if(not Libarylist.istrue(gid)):
        Libarylist.settrue(gid)
    #获取群组名称
    if(gid not in LIBARYID.values()):                
        LIBARYID[get_group_name(gid)] = int(gid)
    
    if(gid not in GROUP_LIST):
        GROUP_LIST.append(gid)

    with open( l_config, "w" ) as file:
        json.dump({"图书馆":GROUP_LIST}, file)

    return await libary_add.finish("图书馆加群成功"+"\n"+get_help())


@libary_log.handle()
async def log_function(bot:Bot,args: Message = CommandArg()):
    logste = []
    if(Libarylist.ifread == False):
        return await libary_log.finish("图书馆正在存档中")
    logste.append("-----------图书馆日志--------------")
    #最近更新时间
    if(Libarylist.librarytime == ""):
        logste.append("上次更新时间:未进行初始化！请联系管理员")
    else:
        logste.append(f"上次更新时间:{Libarylist.librarytime}")
    #图书馆图书数量
    logste.append("图书总数量为:"+ str(len(libraryA.books))+"/10000")
    #图书馆列表
    namelist = list()
    for name in Libarylist.librarylist:
        id = Libarylist.librarylist[name]['id']
        if(not Libarylist.istrue(id)):
            continue
        namelist.append(name+":"+str(id))
    await libary_log.send("\n".join(logste))
    logfile = []
    for name in Libarylist.librarylist:
        id = Libarylist.librarylist[name]['id']
        if(not Libarylist.istrue(id)):
            continue
        logfile.append(get_groupfolder_massage(id))
    return await libary_log.finish("\n".join(logfile)+"\n"+get_help())

libary_help = on_command("图书馆帮助", rule=to_me(), priority=10, block=True)
@libary_help.handle()
async def help_function(bot:Bot,args: Message = CommandArg()):
    helpste = []
    #欢迎语句与开头
    helpste.append("----图书馆指令帮助----")
    helpste.append("qs:欢迎使用图书馆")
    helpste.append("<图书馆初始化>:初始化图书馆")
    helpste.append("<图书馆存档>:将图书馆的群聊所有文件存档")
    helpste.append("<图书馆加群>:将本群加入图书馆")
    helpste.append("<图书馆日志>:查看图书馆运行状况")
    helpste.append("<图书馆查找><书名>:关键字查找图书(不需要打<>)")
    helpste.append("<图书馆打开>:通过id获取图书的下载链接")
    helpste.append("<图书馆清空>:清空图书馆")
    helpste.append("url使用方法:查询到url后,请使用其他浏览器打开url下载文件,然后将后缀改为查找到文件名的后缀名即可")                                                                                                                                                                              
    helpste.append("提示:请尽量使用私聊进行操作")
    return await libary_help.finish('\n'.join(helpste))+'\n'

@libary_open.handle()
async def open_function(args: Message = CommandArg()):
    if(Libarylist.ifread == False):
        return await libary_open.finish("图书馆正在存档中"+"\n"+get_help())
    try:
        id = int(args.extract_plain_text())
        if(id in libraryA.id):
            file_data = libraryA.getUrl(id)
            url = send_file(file_data['group_id'],file_data['id'],file_data["busid"])
            if(url is None):
                return await libary_open.finish("图书馆中没有该图书"+"\n"+get_help())
            else:
                await libary_open.send("url使用方法:查询到url后,请使用其他浏览器打开url下载文件,然后将后缀改为查找到文件名的后缀名即可"+"\n"+get_help())
                return await libary_open.finish(url)
        else:
            return await libary_open.finish("图书馆中没有该图书"+"\n"+get_help())
    except ValueError:
        return await libary_open.finish("请输入正确的图书id"+"\n"+get_help())
    

def get_help():
    return "使用指令<图书馆帮助>查看全部指令"
