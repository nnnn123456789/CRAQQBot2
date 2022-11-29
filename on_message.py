
import asyncio
import os
import datetime
import time
#import qrcode


import botpy
from botpy import logging, BotAPI
from botpy.types.message import Ark, ArkKv

from botpy.message import Message
from botpy.ext.cog_yaml import read
from botpy.types.message import Embed, EmbedField

import lib
import craverify

_log = logging.get_logger()

channel_msg_ans_pool = {}


# async def del_pic(img_path : str, delay = 60):
#     await asyncio.sleep(delay)
#     os.remove(img_path)

# def gen_qrcode(userid : str):
#     path = ".\\temp\\%s.png" % userid
#     url = "https://mirrors.sustech.edu.cn/service/qqv?qq=%s" % userid
#     img = qrcode.make(url)

#     with open(path, "wb") as f:
#         img.save(f)
    
#     return path
#     pass



class Command:

    def __init__(self, handle):
        self.execute = handle

    async def __call__(self, args, api:BotAPI, message: Message):
        try:
            ret = await self.execute(args, api, message)
        except Exception as e:
            _log.error("uncatched exception during handling channel message")
            _log.error(e)
            msg = e.args
            ret = "执行出现错误, %s" % msg
        return ret
    


    
### jrrp for debug

def date():
    return int((time.time()+8*3600)/86400)


def gen_jrrp(qqid):
    s = str(date()) + str(qqid)
    ret = 1 + hash(s)%100;
    #print(ret);
    return ret;


async def jrrp(args, api:BotAPI, message: Message):
    return "<@!%s> 人品值是：%d" % (message.author.id, gen_jrrp(message.author.id))

channel_msg_ans_pool["/jrrp"] = Command(jrrp)





async def SUSTech_auth(args, api:BotAPI, message: Message):
    ID_s = message.author.id[-8:]
    if len(args) == 1:
        return "<@!%s> 您的本频道ID为%s, 请访问cra网站 , 填写本频道ID, 获得验证Token. 使用\"#南科认证 Token\"认证南科身份, 访问频道内容. " % (message.author.id, ID_s)
    elif len(args) == 2:
        if(craverify.verify(args[1], ID_s)):
            l = await api.get_guild_roles(message.guild_id)
            _log.info(l)
            l = l["roles"]
            aim_role_id_s = 0;
            for i in l:
                if i["name"] == "已认证":
                    aim_role_id_s = (i["id"])
                    print(i)
            await api.create_guild_role_member(message.guild_id, aim_role_id_s, message.author.id)
            return "<@!%s>已获得认证用户权限" % message.author.id
        else:
            return "<@!%s> 无法验证您的南科身份, 请重试. \n您的本频道ID为%s, 访问cra网站 , 填写本频道ID, 获得验证Token. 使用\"#南科认证 Token\"认证南科身份, 访问频道内容. " % (message.author.id,ID_s)
    pass

async def SUSTech_auth2(args, api:BotAPI, message: Message):
    authed_role_name = "已认证"
    ID_s = message.author.id[-8:]

    if len(args) == 1:
        ret = "<@!%s> 您的本频道ID为%s, 请访问https://mirrors%%2Esustech%%2Eedu%%2Ecn/service/qqv?qq=%s , 填写本频道ID, 获得验证Token. 使用\"#南科认证 Token\"认证南科身份, 访问频道内容. " % (message.author.id,ID_s, ID_s)
    elif len(args) == 2:
        if(craverify.verify(args[1], ID_s)):
            l = await api.get_guild_roles(message.guild_id)
            _log.info(l)
            l = l["roles"]
            aim_role_id_s = "0";
            for i in l:
                if i["name"] == authed_role_name:
                    aim_role_id_s = (i["id"])
                    print(i)
            if i == "0":
                create_ret = await api.create_guild_role(message.guild_id, name = authed_role_name, hoist = 1)
                aim_role_id_s = create_ret["role_id"]
            await api.create_guild_role_member(message.guild_id, aim_role_id_s, message.author.id)
            ret =  "<@!%s>已获得认证用户权限" % message.author.id
        else:
            ret =  "<@!%s> 无法验证您的南科身份, 请重试. \n您的本频道ID为%s, 请访问https://%%6D%%69%%72%%72%%6F%%72%%73.%%73%%75%%73%%74%%65%%63%%68.%%65%%64%%75.%%63%%6E/service/qqv?qq=%s  , 填写本频道ID, 获得验证Token. 使用\"#南科认证 Token\"认证南科身份, 访问频道内容. " % (message.author.id, ID_s, ID_s)
    await api.post_message(channel_id=message.channel_id, content=ret, msg_id=message.id)
 
    return None

#https://mirrors.sustech.edu.cn/service/qqv?qq=%s

channel_msg_ans_pool["/南科认证"] = Command(SUSTech_auth2)
channel_msg_ans_pool["/南科认证2"] = Command(SUSTech_auth2)

async def main(api: BotAPI,  message: Message):

    rawmsg = message.content

    args = lib.div_args(rawmsg)
    _log.info(args)
    if '<@!' == args[0][0:3] and args[1][0] == '/':
        args = args[1:]
    elif args[0][0] == '/':
        pass
    else:
        return

    if len(args) == 0:
        return
    cmd = channel_msg_ans_pool.get(args[0])

    # print(cmd)
    if not cmd == None:
        ans = await cmd(args, api, message)
        _log.info(ans)
        if (not ans == "") and (not ans == None):
           # await message.reply(content =ans)
            await api.post_message(channel_id=message.channel_id, content=ans, msg_id=message.id)
    pass

