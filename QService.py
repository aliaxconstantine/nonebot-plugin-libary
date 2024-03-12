import requests
import uuid
import os
import datetime
from nonebot.adapters.onebot.v11 import Bot
from collections import defaultdict
from nonebot import logger
import asyncio
import httpx
import threading
import time

cqhttp_url = "http://localhost:8700"
image_path = "image"

def split_text(text: str) -> list:
    n = 1500
    return [text[i:i + n] for i in range(0, len(text), n)]
    
#获取群列表
async def get_groups(bot:Bot):
    try:
        res = await bot.get_group_list()
        groupdict = defaultdict()
        for group in res:
            groupdict[group['group_name']] = group['group_id']

        return groupdict
    except Exception as error:
        logger.error("获取全部群失败"+str(error))

#删除群文件
def del_group_file(gid, file_id, busid):
    try:
        requests.post(url=cqhttp_url + "/delete_group_file",
                      params={'group_id': int(gid), 'file_id': file_id, 'busid': busid})

    except Exception as error:
        logger.error("获取文件url失败" + str(error))

   
#开启全员禁言
def set_group_whole_ban(gid):
    try:
        requests.post(url=cqhttp_url+'/set_group_whole_ban',
                        params={'groupuid':str(gid)})
        logger.error('群'+str(gid)+'已设置全员禁言')
    except:
        logger.error('未能全员禁言')

#设置群专属头衔
def set_group_special_title(gid,uid,spt,time):
    try:
        requests.post(url=cqhttp_url+'/set_group_special_title',params={'group_id':int(gid),'user_id':int(uid),'spcial_title':spt,'duration':time})
        logger.error('在群'+str(gid)+'给qq='+str(uid)+'设置专属头衔成功')
    except:
        logger.error('设置专属头衔失败')

#小程序
def send_group_xiao(gid,name):
    try:
        message = "[CQ:json,data={app:"+"\"com.tencent.miniapp\""+"&#44;\"desc\":""&#44;\"view\":\"notification\"&#440;\"ver\":\"0.0.0.1\"&#44;\"prompt\":\"点击参加"+name+"创办的银趴\"&#44;\"meta\":{\"notification\":{\"appInfo\":{\"appName\":\"银趴通知\"&#44;\"appType\":4&#44;\"appid\":2034149631&#44;\"iconUrl\":\"https:\/\/q.qlogo.cn\/headimg_dl?dst_uin=D00D2B5BF35B8B79453E11B5CAD17370&amp;spec=100\"}&#44;\"data\":&#91;{\"title\":\"通知内容\"&#44;\"value\":\"由"+name+"举办的大型银趴"+str(datetime.date.today())+"下午开始，请群友及时参加。\n\n\n"+name+"\n"+str(datetime.datetime.today())+"\"}"+"&#93;&#44;\"emphasis_keyword\":\"\"}]"
        res = requests.post(url=cqhttp_url + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()

    except:
        logger.error("消息发送失败")
        
#获得群文件根目录
def get_folder(gid)->dict:
    try:
        data = requests.post(url=cqhttp_url+"/get_group_root_files",params={'group_id':int(gid)}).json()
        return data
    except:
        logger.error("获取群文件根目录失败")

#获取文件夹下的子目录:
def get_sonfolder(gid,file_id)->dict:
    try:
        data = requests.post(url=cqhttp_url+"/get_group_files_by_folder",params={'group_id':int(gid),'folder_id':file_id}).json()
        return data
    except:
        logger.error("获取子目录失败")


client = httpx.AsyncClient()
#获取所有群文件：
def get_allfile(gid)->dict:
    try:
        logger.info("获取"+str(gid)+"群文件列表")
        filedict = defaultdict()
        root = get_folder(gid)
        if(root['data'] != None):
            if(root['data']['files'] != None):
                for file in root['data']['files']:
                    filedict[file['file_id']] = {
                        'name':file['file_name'],
                        'busid':file['busid'],
                        'group_id':file['group_id'],
                    }
            if(root["data"]['folders'] != None):
                for node in root['data']['folders']:
                    data = get_sonfolder(gid,node['folder_id'])
                    if(data['data']['files']!=None):
                        for file in data['data']['files']:
                            filedict[file['file_id']] = {
                            'name':file['file_name'],
                            'busid':file['busid'],
                            'group_id':file['group_id']
                        }
            else:
                return None
        else:
            return None
                    
        return filedict

    except Exception as error:
       logger.error("获取所有群文件失败"+str(error))
    

def send_file(gid,file_id,busid):
    try:
        data = requests.post(url=cqhttp_url+"/get_group_file_url",params={'group_id':int(gid),'file_id':file_id,'busid':busid}).json()

        if data['data'] != None:
            return str(data['data']['url'])
        else:
            return None
    
    except Exception as error:
        logger.error("获取文件url失败"+str(error))

def get_group_name(gid):
    try:
        data = requests.post(url=cqhttp_url+"/get_group_info",params={'group_id':int(gid)}).json()
        if(data['data']!= None):
            return data['data']['group_name']
        return None

    except Exception as error:
        logger.error("获取群名称失败"+str(error))

def get_groupfolder_massage(gid):
    try:
        data = requests.post(url=cqhttp_url+"/get_group_file_system_info",params={'group_id':int(gid)}).json()
        if(data['data'] != None):
            return get_group_name(gid)+"\n  #文件情况:"+str(data['data']['file_count'])+"/"+str(data['data']['limit_count'])+'\n  #空间情况'+str(round(float(data['data']['used_space']/1073741824),2))+"GB/"+str(round(float(data['data']['total_space']/1073741824),2))+"GB"

        return None
    except Exception as error:
        logger.error("获取群名称失败"+str(error))


