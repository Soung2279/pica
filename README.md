<p align="center">
  <a href="https://sm.ms/image/EzUXf3ZpwoA7VBx" target="_blank"><img src="https://s2.loli.net/2022/09/06/EzUXf3ZpwoA7VBx.png" ></a>
  </a>
</p>


Pica for HoshinoBot
===========================
<div align="left">


→→ **[查看更新日志](#更新日志)**

  
功能介绍
===========================

适用于``Hoshinobot V2+``的 **Pica漫画插件**

本项目具备的功能有如下：
- 根据 **指定关键词** 搜索漫画
- 根据 **指定分区** 搜索漫画, 例如"最多爱心","最多人指名"等
- **自动打包** 漫画本体
- 随机漫画
- 本子推荐, 使用登陆账号的 **收藏夹** 随机选择
- ……

在以下环境下，插件已经过测试：
- [x] ``Windows 10``
- [x] ``Windows 11``
- [x] ``python 3.8.9 32&64bit``
- [x] ``python 3.9.13 32&64bit``
- [x] ``Hoshinobot V2.0``
- [x] ``nonebot 1.8.2``
- [ ] 理论上支持 ``python 3.9+``，``nonebot 1.6.0+``

[![OS](https://img.shields.io/badge/Windows10-0078d6?style=flat-square&logo=windows&logoColor=fff)](https://www.microsoft.com/zh-cn/windows)  [![Python](https://img.shields.io/badge/Python-yellow?style=flat-square&logo=python)](https://www.python.org/)

> 由于本人不熟悉Linux环境，且插件均在Windows环境下编写完成，在Linux上使用可能有bug，请见谅

**不适用于 ``nonebot2`` ！**

**已尽量避免使用相对路径, 但尚未在Linux平台测试**

插件安装
===========================


0. 确保Bot客户端所在网络**可以访问** [PicAcg资源](https://storage1.picacomic.com/static/653cc9e0-1548-4cc3-bba0-d6e2e1bd9c18.jpg)

可尝试 
```cmd
Ping storage1.picacomic.com
Ping picaapi.picacomic.com
```

<details>
    <summary>若能访问>>>下一步</summary>

1. 在**hoshino/modules**文件夹中，打开cmd或者powershell，输入以下代码 按回车执行：

```powershell
git clone https://github.com/Soung2279/pica.git
```

2. 之后关闭cmd或powershell，打开 **hoshino/config** 的 `__bot__.py` 文件，在 **MODULES_ON** 里添加 ``pica``
```python
# 启用的模块
MODULES_ON = {
    'xxx',
    'pica',  #注意英文逗号！
    'xxx',
}
```

3. 之后，安装依赖 ``pip install -r requirements.txt`` 或 双击目录下的 ``安装依赖.bat``

4. 打开 ``main.py`` ,进行配置填写

```python
#转发消息画像
forward_msg_name = "神秘的HaruBot"
forward_msg_uid = 123456789

#填写pica账号
pica_account = ""
pica_password = ""
p.login(pica_account, pica_password)

#pica图片存放的文件夹
pica_folder = ""

#默认顺序
Order_Default = "ld"

#单日使用上限
_max = 5
_nlmt = DailyNumberLimiter(_max)
#单次使用冷却(s)
_cd = 180
_flmt = FreqLimiter(_cd)
```

5. 打开 ``pica/pic2.py``, 进行apikey填写

```python
nonce = ""
api_key = ""
secret_key = ""
```

> 此处的api可通过 [picacomic作者主页](https://zhuanlan.zhihu.com/p/547321040) 获得

6. ENJOY IT!
</details>

指令
===========================

### 根据关键字搜本:
- 1.**[搜pica +关键字]**, 返回符合的本子信息
- 2.利用[1]中的 **漫画id**, **[看pica +漫画id]**

### 指定分区的关键字搜本:
- 1.**[分区搜 +分区+关键字]**, 返回指定分区下的本子信息,空格分割
- 2.利用[1]中的 **漫画id**, **[看pica +漫画id]**

### 随机本子:
- 1.**[随机本子]**, 返回随机本子信息
- 2.利用[1]中的 **漫画id**, **[看pica +漫画id]**

### 指定分区的随机本子:
- 1.**[指定随机 +分区名]**, 返回指定分区下的随机本子信息
- 2.利用[1]中的 **漫画id**, **[看pica +漫画id]**

### 本子推荐:
- 1.**[本子推荐]**, 返回我的收藏下的本子信息
- 2.利用[1]中的 **漫画id**, **[看pica +漫画id]**

> 插件会自动识别使用者是否为bot好友，若是，则bot以私聊形式发送打包文件与消息，否则上传到群文件

> 建议使用者添加Bot为好友

> 视网络环境等情况，可能导致远程请求/下载等候过久。

说明
========================

默认的Pica图片存放目录为 ``RES_DIR/img/pica``

该目录结构如下:
```
主目录: RES_DIR/img/pica/
漫画目录: RES_DIR/img/pica/{规范化后的漫画名}
漫画图片: RES_DIR/img/pica/{规范化后的漫画名}/{图片原始名}
封面图片: RES_DIR/img/pica/{规范化后的漫画名}/{规范化后的漫画名}_cover.jpg
打包文件: RES_DIR/img/pica/{规范化后的漫画名}.zip

例如：
访问A漫画的图片：/img/pica/A/01.jpg
A漫画的封面：/img/pica/A/A_cover.jpg
A漫画打包文件：/img/pica/A.zip
```


### 其它

若有安装上的问题，可以提Issue，或加入群聊 [SoungBot交流](https://jq.qq.com/?_wv=1027&k=DXw3Feqg) 向群主(我)提问

PicAcg Comic Api 提供：[picacomic](https://github.com/AnkiKong/picacomic)

HoshinoBot ：[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)

made by [Soung2279@Github](https://github.com/Soung2279/)

### 鸣谢

[picacomic](https://github.com/AnkiKong/picacomic)

[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)

****

### 更新日志


#### 2022/9/6  v1.0

首次上传。已实现基本功能。
