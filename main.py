# -*- coding: utf-8 -*-
import requests
import os
import zipfile
import random
import re
try:
    import ujson as json
except:
    import json
from .pica import pic2
from fuzzywuzzy import process
from os.path import join, getsize
from opencc import OpenCC

import hoshino
from hoshino import Service, priv, config, R
from hoshino.util import FreqLimiter, DailyNumberLimiter
from hoshino.typing import CQEvent


#forward_msg_name = config.FORWARD_MSG_NAME
#forward_msg_uid = config.FORWARD_MSG_UID
#导入类
p = pic2.Pica()

#转发消息画像
forward_msg_name = "神秘的HaruBot"
forward_msg_uid = 123456789

#请求标头
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}

#填写pica账号
pica_account = ""
pica_password = ""
p.login(pica_account, pica_password)

#pica存放的文件夹
pica_folder = os.path.abspath(f"{config.RES_DIR}/img/pica/")

#默认顺序
Order_Default = "ld"
'''
"ua"  # 默认
"dd"  # 新到旧
"da"  # 旧到新
"ld"  # 最多爱心
"vd"  # 最多指名
'''

#单日使用上限
_max = 5
_nlmt = DailyNumberLimiter(_max)
#单次使用冷却(s)
_cd = 180
_flmt = FreqLimiter(_cd)

#去除特殊字符,Windows下新建文件夹名不得包含以下字符
pattern = r"(\\)|(/)|(\|)|(:)|(\*)|(\?)|(\")|(\<)|(\>)"

#获取分区列表
categories = pic2.categories
#获取排序字典
orders = pic2.orders


'''
usage:生成合并转发消息节点
param:chain:list(固定空列表，用于合成输出), msg(消息内容), #image(图片,目前似乎无法使用)
return:chain(合成后的转发消息节点)
'''
def make_forward_msg(chain:list, msg, image = ''):
    msg = "".join(msg)
    if not image:
        data ={
                "type": "node",
                "data": {
                    "name": str(forward_msg_name),
                    "uin": str(forward_msg_uid),
                    "content": [
                        {"type": "text", "data": {"text": msg}}
                        ]
                        }
            }
        chain.append(data)
    else:
        data ={
                "type": "node",
                "data": {
                    "name": str(forward_msg_name),
                    "uin": str(forward_msg_uid),
                    "content": [
                        {"type": "text", "data": {"text": msg}},
                        {"type": "image", "data": {"file": image}}
                        ]
                        }
            }
        chain.append(data)
        
    return chain



'''
usage:进行指令模糊匹配
param:input(用户输入内容), command:list(匹配指令列表)
return:fuzzy_word(匹配到的第一个词), fuzzy_probability(匹配相关度)
'''
def guess_command(input, command:list):
    fuzzy = process.extractOne(input, command)
    fuzzy_word = fuzzy[0]
    fuzzy_probability = fuzzy[1]
    
    return fuzzy_word, fuzzy_probability


def download_img(url, booktitle, originalName):
    error_recall = []
    booktitle = booktitle.strip()
    sub = re.sub(pattern, "-", booktitle)
    #若不存在文件夹,先创建
    if not os.path.exists(pica_folder):
        os.mkdir(pica_folder)

    comic_folder = os.path.join(pica_folder,sub)
    if not os.path.exists(comic_folder):
        os.mkdir(comic_folder)

    rs = requests.get(url, headers=headers,timeout=(3.05, 27), stream=True)

    filename = str(originalName)
    image_path = os.path.join(comic_folder,filename)
    with open(image_path, "wb") as download:
        try:
            download.write(rs.content)
            download.close()
        except:
            error_recall = "pica资源获取失败:HTTP状态码:"+str(rs.status_code)
            print(error_recall)

    return error_recall


'''
usage:从指定漫画id进行图片下载
param:bookid:str(漫画id)
return:error_recall(错误回执,无错误时为空)
'''
def get_comic_from_id(bookid:str):
    error_recall = []
    ex_input = bookid.strip()
    try:
        cm = p.comic_info(ex_input).text
        cm_read = json.loads(cm)
        cm_name = cm_read["data"]["comic"]["title"]
        thumb_url = cm_read["data"]["comic"]["thumb"]["fileServer"] + "/static/" + cm_read["data"]["comic"]["thumb"]["path"]
        download_thumb(thumb_url, cm_name)
    except:
        error_recall = "pica获取失败,可能是输入id错误"
        print(error_recall)
        return error_recall
    pic_post = p.picture(ex_input).text
    pic_result = json.loads(pic_post)
    if not pic_result["code"] == 200:
        error_recall = "pica请求出错:HTTP状态码:"+str(pic_result["code"])+"\n响应信息:" + pic_result["message"]
        print(error_recall)
    else:
        pages_num = pic_result["data"]["pages"]["pages"]
        for x in range(1, pages_num+1):
            post_pic = p.picture(ex_input,page=x).text
            meta = json.loads(post_pic)
            docs = meta["data"]["pages"]["docs"]
            for y in range(len(docs)):
                ogname = docs[y]["media"]["originalName"]
                imgpath = docs[y]["media"]["path"]
                fileServer = docs[y]["media"]["fileServer"]
                url = fileServer + "/static/" + imgpath
                print(f"当前正在下载:第{x}页第{y}张:{ogname}")
                download_img(url,cm_name,ogname)

'''
usage:下载指定url的封面图
param:url(图片url), booktitle(漫画名,用来作为文件名)
'''
def download_thumb(url, booktitle):
    booktitle = booktitle.strip()
    sub = re.sub(pattern, "-", booktitle)
    #若不存在文件夹,先创建
    if not os.path.exists(pica_folder):
        os.mkdir(pica_folder)

    comic_folder = os.path.join(pica_folder,sub)
    if not os.path.exists(comic_folder):
        os.makedirs(comic_folder)

    rs = requests.get(url, headers=headers, timeout=(3.05, 27), stream=True)
    filename = sub+"_cover"+".jpg"
    image_path = os.path.join(comic_folder,filename)
    with open(image_path, "wb") as download:
        try:
            download.write(rs.content)
            download.close()
        except:
            print("pica资源获取失败:HTTP状态码:"+str(rs.status_code))


'''
usage:获取我的收藏遍历列表
param:res:dict(存有漫画信息的字典)
return:我的收藏遍历列表
'''
def get_random_favorite(res:dict):
    comic_info = []
    favor = {}
    meta = res["data"]["comics"]["docs"]
    for x in range(0, len(meta)):
        value_list = []
        bkid = meta[x]["_id"]
        bktitle = str(meta[x]["title"])
        author = str(meta[x]["author"])
        bkthumb = str(meta[x]["thumb"]["fileServer"] + "/static/" + meta[x]["thumb"]["path"])
        value_list.append(bktitle)
        value_list.append(author)
        value_list.append(bkthumb)
        favor[bkid] = value_list
    
    for key,value in favor.items():
        detail = f"{value[0]}：\n漫画ID:{key}\n作者:{value[1]}"
        thumb_url = value[2]
        download_thumb(thumb_url, value[0])
        comic_info.append(detail)

    return comic_info

'''
usage:获取漫画id及信息
param:result:dict(存有漫画信息的字典)
return:error_recall(错误回执/若有), comic_info(漫画信息)
'''
def get_search_bookid(result:dict):
    error_recall = []
    comic_info = []
    if result["data"]["comics"]["total"] == 0:
        error_recall = "pica搜索出错:搜索结果为空.请尝试更换关键词"
        print(error_recall)
        return error_recall, comic_info

    elif result["data"]["comics"]["total"] == 1:
        meta = result["data"]["comics"]["docs"][0]
        bookid = meta["_id"]
        thumb_url = meta["thumb"]["fileServer"] + "/static/" + meta["thumb"]["path"]
        title = meta["title"]
        author = meta["author"]
        try:
            chineseTeam = meta["chineseTeam"]
        except:
            chineseTeam = "Unknown"
        comic_info = f"{title}：\n漫画ID:{bookid}\n作者:{author}\n汉化:{chineseTeam}"
        download_thumb(thumb_url, title)
        return error_recall, comic_info

    elif result["data"]["comics"]["total"] > 5:
        meta_1 = result["data"]["comics"]["docs"][0]
        meta_2 = result["data"]["comics"]["docs"][1]
        meta_3 = result["data"]["comics"]["docs"][2]
        #有时返回的JSON不存在chineseTeam
        try:
            chineseTeam_1 = meta_1["chineseTeam"]
        except:
            chineseTeam_1 = "Unknown"
        
        try:
            chineseTeam_2 = meta_2["chineseTeam"]
        except:
            chineseTeam_2 = "Unknown"
        
        try:
            chineseTeam_3 = meta_3["chineseTeam"]
        except:
            chineseTeam_3 = "Unknown"
        cm_info1 = meta_1["title"] + "\n" +"漫画ID:" + meta_1["_id"] + "\n" + "作者:" + meta_1["author"] + "\n" + "汉化:" + chineseTeam_1
        cm_info2 = meta_2["title"] + "\n" +"漫画ID:" + meta_2["_id"] + "\n" + "作者:" + meta_2["author"] + "\n" + "汉化:" + chineseTeam_2
        cm_info3 = meta_3["title"] + "\n" +"漫画ID:" + meta_3["_id"] + "\n" + "作者:" + meta_3["author"] + "\n" + "汉化:" + chineseTeam_3
        comic_info = cm_info1+"\n"+cm_info2+"\n"+cm_info3
        return error_recall, comic_info
        
    else:
        meta_1 = result["data"]["comics"]["docs"][0]
        try:
            chineseTeam_1 = meta_1["chineseTeam"]
        except:
            chineseTeam_1 = "Unknown"
        cm_info1 = meta_1["title"] + "\n" +"漫画ID:" + meta_1["_id"] + "\n" + "作者:" + meta_1["author"] + "\n" + "汉化:" + chineseTeam_1
        return error_recall, cm_info1

'''
usage:生成压缩包
param:source_dir(需要压缩文件的目录), output_filename(压缩包文件名)
return:压缩包目录
'''
def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')    
    pre_len = len(os.path.dirname(source_dir))
    for parent, _, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            zipf.write(pathfile, arcname)
    zipf.close()
    print(f"压缩包创建完成:位于{output_filename}")
    return output_filename



sv_help = """
======因需向远程请求,视网络环境等因素可能等待时间较长======

根据关键字搜本:
1.[搜pica +关键字],返回符合的本子信息
2.利用[1]中的漫画id, [看pica +漫画id]

指定分区的关键字搜本:
1.[分区搜 +分区+关键字],返回指定分区下的本子信息,空格分割
2.利用[1]中的漫画id, [看pica +漫画id]

随机本子:
1.[随机本子],返回随机本子信息
2.利用[1]中的漫画id, [看pica +漫画id]

指定分区的随机本子:
1.[指定随机 +分区名],返回指定分区下的随机本子信息
2.利用[1]中的漫画id, [看pica +漫画id]

本子推荐:
1.[本子推荐],返回我的收藏下的本子信息
2.利用[1]中的漫画id, [看pica +漫画id]
""".strip()

sv = Service(
    name = "PICA",  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = "pica", #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助pica", "pica帮助"])
async def bangzhu_pica(bot, ev):
    await bot.send(ev, sv_help)


#>>>根据关键字搜本<<<
@sv.on_prefix(("搜pica","搜bica","搜pika","搜bika","搜哔咔"))
async def search_pica(bot, ev: CQEvent):
    chain = []
    input = ev.message.extract_plain_text()
    gid = ev["group_id"]
    uid = ev["user_id"]
    #获取好友列表,并判断当前用户是否在好友列表中
    bot_friend_list = await bot.get_friend_list()
    fd_list = []
    for fd in bot_friend_list:
        gfd = fd["user_id"]
        fd_list.append(str(gfd))    
    #冷却限制
    if not _nlmt.check(uid):
        if uid in config.SUPERUSERS:#超级用户不受限,便于测试
            pass
        else:
            EXCEED_NOTICE = f'您今天已经查看{_max}次了，请不要滥用哦~'
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
    if not _flmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            await bot.send(ev, f"您查询的太快了，有{_cd}秒冷却哦", at_sender=True)
            return
    #忽略空关键词
    if not input:
        await bot.send(ev, "输入为空！")
        return
    else:
        #转换为繁体
        ex_input = OpenCC('s2t').convert(input.strip())
        #去除特殊字符(使用标题作为文件夹名时,不能包含特殊字符)
        pattern = r"(\\)|(/)|(\|)|(:)|(\*)|(\?)|(\")|(\<)|(\>)"
        sub = re.sub(pattern, "-", ex_input)
        zipname = sub+".zip"
        zippath = os.path.join(pica_folder, zipname)
        #检查是否已存在该本,若有,发送本地缓存
        if os.path.exists(zippath):
            await bot.send(ev, "本地已存在此结果,将发送本地缓存")
            #若当前用户是bot好友,私聊发送文件,否则上传到群文件
            if str(uid) in fd_list:
                await bot.send_private_msg(user_id=uid,message=sub)
                await bot.upload_private_file(user_id=int(uid),file=zippath,name=zipname)
            else:
                await bot.send(ev, sub)
                await bot.upload_group_file(group_id=int(gid),file=zippath,name=zipname)
        else:
            search_post = p.search(ex_input, sort=Order_Default).text
            search_result = json.loads(search_post)
            if not search_result["code"] == 200:
                error_recall = "pica请求出错:HTTP状态码:"+str(search_result["code"])+"\n响应信息:" + search_result["message"]
                await bot.send(ev, error_recall)
            else:
                error, comic_info = get_search_bookid(search_result)
                #合并转发消息节点
                out = make_forward_msg(chain, comic_info)
                #有错误信息时,发送错误信息
                if not error:
                    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=out)
                else:
                    await bot.send(ev, error)
    #冷却计时
    _flmt.start_cd(uid)
    _nlmt.increase(uid)


#>>>指定分区的关键字搜本<<<
@sv.on_prefix(("分区搜"))
async def search_pica_cate(bot, ev: CQEvent):
    chain = []
    uid = ev["user_id"]
    input2 = ev.message.extract_plain_text()
    if not _nlmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            EXCEED_NOTICE = f'您今天已经查看{_max}次了，请不要滥用哦~'
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
    if not _flmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            await bot.send(ev, f"您查询的太快了，有{_cd}秒冷却哦", at_sender=True)
            return
    if not input2:
        await bot.send(ev, "输入为空！")
        return
    else:
        ex_input = input2.strip().split(" ")
        sort_ca = []
        #分区在前,关键字在后
        cate = ex_input[0]
        cates_ex = OpenCC('s2t').convert(cate)
        #模糊匹配分区
        fuzzy_word, fuzzy_probability = guess_command(cates_ex, categories)
        if fuzzy_probability == 100:
            pass
        else:
            tips = f"您有{fuzzy_probability}%的可能想搜索“{fuzzy_word}”。"
            await bot.send(ev, tips)
            cates_ex = fuzzy_word
        words = ex_input[1]
        keyword = OpenCC('s2t').convert(words)
        sub = re.sub(pattern, "-", keyword)
        sort_ca.append(cates_ex)
        search_post = p.search(keyword=keyword, categories=sort_ca, sort=Order_Default).text
        search_result = json.loads(search_post)
        if not search_result["code"] == 200:
            error_recall = "pica请求出错:HTTP状态码:"+str(search_result["code"])+"\n响应信息:" + search_result["message"]
            await bot.send(ev, error_recall)
        else:
            comic_folder = os.path.join(pica_folder,sub)
            filename = sub+"_cover"+".jpg"
            image_path = os.path.join(comic_folder,filename)
            error, comic_info = get_search_bookid(search_result)
            error, comic_info = get_search_bookid(search_result)
            out = make_forward_msg(chain, comic_info, image_path)
            if not error:
                await bot.send_group_forward_msg(group_id=ev['group_id'], messages=out)
            else:
                await bot.send(ev, error_recall)
    #冷却计时
    _flmt.start_cd(uid)
    _nlmt.increase(uid)


#>>>使用漫画ID查看本子<<<
@sv.on_prefix(("看pica","看bika","看哔咔","看pika","看bica"))
async def get_pica(bot, ev: CQEvent):
    input3 = ev.message.extract_plain_text()
    gid = ev["group_id"]
    uid = ev["user_id"]
    if not _nlmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            EXCEED_NOTICE = f'您今天已经查看{_max}次了，请不要滥用哦~'
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
    if not _flmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            await bot.send(ev, f"您查询的太快了，有{_cd}秒冷却哦", at_sender=True)
            return
    if not input3:
        await bot.send(ev, "输入为空！")
        return
    else:
        src = p.comic_info(input3).text
        src_data = json.loads(src)
        name = src_data["data"]["comic"]["title"].strip()
        author = src_data["data"]["comic"]["author"]
        try:
            chineseTeam = src_data["data"]["comic"]["chineseTeam"]
        except:
            chineseTeam = "Unknown"
        zipname = name+".zip"
        zippath = f"{pica_folder}/{zipname}"
        if os.path.exists(zippath):
            await bot.send(ev, "本地已缓存")
        else:
            get_comic_from_id(input3)
            dirname = os.path.join(pica_folder,str(name))
            output_filename = dirname+".zip"
            zippath = make_zip(source_dir=dirname, output_filename=output_filename)

    bot_friend_list = await bot.get_friend_list()
    fd_list = []
    for fd in bot_friend_list:
        gfd = fd["user_id"]
        fd_list.append(str(gfd))
    
    thbname = name+"_cover.jpg"
    thb_path = R.img(f"pica/{name}/{thbname}").cqcode
    msg = f"{name}：\n作者:{author}\n汉化:{chineseTeam}"
    if str(uid) in fd_list:
        await bot.send(ev, f"消息处理成功, 请注意私聊窗口")
        await bot.send_private_msg(user_id=uid,message=thb_path)
        await bot.send_private_msg(user_id=uid,message=msg)
        await bot.upload_private_file(user_id=int(uid),file=zippath,name=name+".zip")
    else:
        await bot.send_group_msg(group_id=gid,message=thb_path)
        await bot.send_group_msg(group_id=gid,message=msg)
        await bot.upload_group_file(group_id=int(gid),file=zippath,name=name+".zip")
     #冷却计时
    _flmt.start_cd(uid)
    _nlmt.increase(uid)



#>>>随机本子<<<
@sv.on_fullmatch(("随机本子"))
async def get_pica_random(bot, ev: CQEvent):
    chain = []
    gid = ev["group_id"]
    uid = ev["user_id"]
    if not _nlmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            EXCEED_NOTICE = f'您今天已经查看{_max}次了，请不要滥用哦~'
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
    if not _flmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            await bot.send(ev, f"您查询的太快了，有{_cd}秒冷却哦", at_sender=True)
            return
    #随机分区
    cate = random.choice(categories)
    await bot.send(ev, f"随机分区:{cate}")
    #随机排序
    od_list = []
    for key in orders.keys():
        od_list.append(key)
    order = random.choice(od_list)
    order_cn = orders[order]
    await bot.send(ev, f"随机排序:{order_cn}")
    #随机第几页
    pages = random.randint(1,50)
    res = p.comics(block=cate, order=order,page=pages)
    out = res["data"]["comics"]["docs"][0]
    bookid = out["_id"]
    thumb_url = out["thumb"]["fileServer"] + "/static/" + out["thumb"]["path"]
    title = out["title"].strip()
    #去除特殊字符(使用标题作为文件夹名时,不能包含特殊字符)
    pattern = r"(\\)|(/)|(\|)|(:)|(\*)|(\?)|(\")|(\<)|(\>)"
    sub = re.sub(pattern, "-", title)
    author = out["author"]
    try:
        chineseTeam = out["chineseTeam"]
    except:
        chineseTeam = "Unknown"
    comic_info = f"{sub}：\n漫画ID:{bookid}\n作者:{author}\n汉化:{chineseTeam}"
    download_thumb(thumb_url, sub)
    get_comic_from_id(bookid)
    dirname = os.path.join(pica_folder,str(sub))
    output_filename = dirname+".zip"
    zippath = make_zip(source_dir=dirname, output_filename=output_filename)
    output = make_forward_msg(chain, comic_info)

    bot_friend_list = await bot.get_friend_list()
    fd_list = []
    for fd in bot_friend_list:
        gfd = fd["user_id"]
        fd_list.append(str(gfd))

    thbname = sub+"_cover.jpg"
    thb_path = R.img(f"pica/{sub}/{thbname}").cqcode
    if str(uid) in fd_list:
        await bot.send_private_msg(user_id=uid,message=thb_path)
        await bot.send_private_msg(user_id=uid,message=comic_info)
        try:
            await bot.upload_private_file(user_id=int(uid),file=zippath,name=title+".zip")
            await bot.send(ev, f"消息处理成功, 请注意私聊窗口")
        except:
            await bot.send(ev, f"消息已响应, 但上传失败.请查看日志窗口")
    else:
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=output)
        await bot.upload_group_file(group_id=int(gid),file=zippath,name=title+".zip")
     #冷却计时
    _flmt.start_cd(uid)
    _nlmt.increase(uid)



#>>>指定分区的随机本子<<<
@sv.on_prefix(("指定随机"))
async def get_pica_cate_random(bot, ev: CQEvent):
    uid = ev["user_id"]
    if not _nlmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            EXCEED_NOTICE = f'您今天已经查看{_max}次了，请不要滥用哦~'
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
    if not _flmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            await bot.send(ev, f"您查询的太快了，有{_cd}秒冷却哦", at_sender=True)
            return
    input5 = ev.message.extract_plain_text()
    cates = OpenCC('s2t').convert(input5)
    fuzzy_word, fuzzy_probability = guess_command(cates, categories)
    if fuzzy_probability == 100:
        pass
    else:
        tips = f"您有{fuzzy_probability}%的可能想搜索“{fuzzy_word}”。"
        await bot.send(ev, tips)    
    od_list = []
    for key in orders.keys():
        od_list.append(key)
    order = random.choice(od_list)
    order_cn = orders[order]
    await bot.send(ev, f"随机排序:{order_cn}")
    ex_input5 = OpenCC('s2t').convert(input5)
    res = p.comics(block=ex_input5, order=order)
    out = res["data"]["comics"]["docs"][0]
    bookid = out["_id"]
    thumb_url = out["thumb"]["fileServer"] + "/static/" + out["thumb"]["path"]
    title = out["title"].strip()
    author = out["author"]
    try:
        chineseTeam = out["chineseTeam"]
    except:
        chineseTeam = "Unknown"
    comic_info = f"{title}：\n漫画ID:{bookid}\n作者:{author}\n汉化:{chineseTeam}"
    download_thumb(thumb_url, title)
    await bot.send(ev, comic_info)
    get_comic_from_id(bookid)
    dirname = os.path.join(pica_folder,str(title))
    output_filename = dirname+".zip"
    make_zip(source_dir=dirname, output_filename=output_filename)
     #冷却计时
    _flmt.start_cd(uid)
    _nlmt.increase(uid)


#>>>本地随机本子<<<
@sv.on_fullmatch(("本地随机"))
async def get_pica_local_random(bot, ev: CQEvent):
    gid = ev["group_id"]
    uid = ev["user_id"]
    if not _nlmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            EXCEED_NOTICE = f'您今天已经查看{_max}次了，请不要滥用哦~'
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
    if not _flmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            await bot.send(ev, f"您查询的太快了，有{_cd}秒冷却哦", at_sender=True)
            return
    
    filelist = os.listdir(pica_folder)
    random.shuffle(filelist)
    for filename in filelist:
        if str(filename).endswith(".zip"):
            zipname = filename
    
    zippath = f"{pica_folder}/{zipname}"
    bot_friend_list = await bot.get_friend_list()
    fd_list = []
    for fd in bot_friend_list:
        gfd = fd["user_id"]
        fd_list.append(str(gfd))
    
    if str(uid) in fd_list:
        try:
            await bot.upload_private_file(user_id=int(uid),file=zippath,name=zipname)
            await bot.send(ev, f"消息处理成功, 请注意私聊窗口")
        except:
            await bot.send(ev, f"消息已响应,但上传失败了.请注意日志窗口")
            
    else:
        await bot.upload_group_file(group_id=int(gid),file=zippath,name=zipname)
     #冷却计时
    _flmt.start_cd(uid)
    _nlmt.increase(uid)


@sv.on_fullmatch(("本子推荐"))
async def get_pica_cate_random(bot, ev: CQEvent):
    my_list = []
    uid = ev["user_id"]
    if not _nlmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            EXCEED_NOTICE = f'您今天已经查看{_max}次了，请不要滥用哦~'
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
    if not _flmt.check(uid):
        if uid in config.SUPERUSERS:
            pass
        else:
            await bot.send(ev, f"您查询的太快了，有{_cd}秒冷却哦", at_sender=True)
            return
    await bot.send(ev, "将获取完整收藏列表,条目较多,请耐心等待...")
    comment = p.my_favourite().text
    comment_js = json.loads(comment)
    page_num = comment_js["data"]["comics"]["pages"]
    for loop in range(1, page_num):
        comment = p.my_favourite(page=loop,order=Order_Default).text
        com_js = json.loads(comment)
        favors = get_random_favorite(com_js)
        #遍历我的收藏,并将相关信息放入查询列表
        my_list.extend(favors)
    
    random.shuffle(my_list)
    lipr = int(random.randint(0,len(my_list)))
    #打乱列表顺序后,随机下标取值
    recomment = my_list[lipr]
    await bot.send(ev, recomment)
    await bot.send(ev, "请使用 [看pica+漫画id] 来查看")
     #冷却计时
    _flmt.start_cd(uid)
    _nlmt.increase(uid)
    #todo:随机获取一篇漫画后,直接发送



# 获取文件目录大小
def getdirsize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size

def countFile(dir):
    tmp = 0
    for item in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, item)):
            tmp += 1
        else:
            tmp += countFile(os.path.join(dir, item))
    return tmp

@sv.on_fullmatch(["检查pica", "检查pika", "检查bica", "检查bika", "检查哔咔"])
async def check_pica(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):   #建议使用priv.SUPERUSER
        await bot.send(ev, f"权限不足,只有Bot主人才可使用此指令", at_sender=True)
        return
    else:
        shots_all_num = countFile(str(pica_folder)) #同上
        shots_all_size = getdirsize(pica_folder)  #同上
        all_size_num = '%.3f' % (shots_all_size / 1024 / 1024)
        info_before = f"当前目录有{shots_all_num}个文件，占用{all_size_num}Mb"
        await bot.send(ev, info_before)
        p.login(pica_account, pica_password)
        ts = p.comics(order=Order_Default)
        pic2_ck = ts["code"]
        rs = requests.get("https://storage1.picacomic.com/static/653cc9e0-1548-4cc3-bba0-d6e2e1bd9c18.jpg")
        await bot.send(ev, f"pic2API连通测试:{pic2_ck}")
        await bot.send(ev, f"PicAcg资源连通测试:{rs.status_code}")


'''
原项目地址：
作者主页：https://github.com/Soung2279
'''