# 美国签证预约时间 自动化爬取+邮件推送

国内版：[https://tuixue.online/visa/](https://tuixue.online/visa/)

国际版：[https://tuixue.online/global/](https://tuixue.online/global/)

## Overview

目前采用的是部分前后端分离，姑且将其称之为前端服务器和爬虫服务器。整体逻辑为前端服务器定时向爬虫服务器发送数据请求，拉取到其本地、更新静态页面和推送通知。

爬虫服务器使用Django构建，代码位于[/api](/api)文件夹下，cgi系统使用纯requests拉取数据，ais使用requests和selenium混合模式拉取数据

前端服务器采用nginx部署，使用python和爬虫服务器进行交互（详见lite_visa.py），和用户交互使用静态html或者php

前端展示表格使用echart，评论区使用disqus第三方服务

邮件通知、QQ群和Telegram channel通知均使用python实现，详见notify.py

## Usage

爬虫的使用请移步 [/api](/api)，包括各种请求字段，甚至免费的cgi验证码破解器也有（准确率大概98%）

国内版（`/visa`）和国际版（`/global`）的前端部署其实差不多，在对应文件夹下找到 `lite_visa.py` 之后启动起来就行，这个是个定时拉数据的脚本。在获取新的数据之后会调用 `notify.py` 更新

# Website Documentation

## 日期存储

日期变化情况存放于 `/visa2/{type}/{location}/{YYYY}/{MM}/{DD}` 或者 `/global/crawler/{type}/{location}/{YYYY}/{MM}/{DD}` 中，其中：

- `type`：**大写**字符，签证类型，为 "FBHOL" 其中一种
- `location`：字符串，使馆所在城市，cgi系统为中文字符，ais系统为英文字符
- `YYYY`、`MM`、`DD`：年月日

存储格式为若干行文本，每行格式是 `mm:ss YYYY/MM/DD`，表示在当天第`mm`分`ss`秒，能查到的最早预约日期是 `YYYY/MM/DD`

如果没有可预约的日期，则不用写入该文本中。更进一步，如果当天没有任何可预约日期，则可以不用创建该文本。

## 当前最新日期

这个是若干个个json文件，（不过我觉得可以重构的时候把这个废掉），为了判断是否需要发送更新提醒用的。

json文件存放于 `/visa/visa-{type}.json`、`/visa/visa-{type}-last.json` 和 `/global/visa-{type}.json`、`/global/visa-{type}-last.json`，这里的type是**小写**，注意有个历史遗留问题是 `/visa/visa-f.json` 和 `/visa/visa-f-last.json` 没有，是 `/visa/visa.json` 和 `/visa/visa-last.json`，需要改改

json文件格式是

```
{
    "time": "{YYYY}/{MM}/{DD} {hh}:{mm}:{ss}",
    "index": ["{YYYY}/{MM}/{DD}", "{YYYY}/{MM}/{DD}", ...],
    "{location}-{YYYY}/{MM}/{DD}": "{YYYY}/{MM}/{DD}" 或者 "/",
    "{location}2-{YYYY}/{MM}/{DD}": "{YYYY}/{MM}/{DD}" 或者 "/",
    ...
}
```

其中 `location` 与上面一致；2一栏表示的是最早日期；`index` 记录了日期跨度（按照由近到远排序），最多50个日期；`time` 表示更新这个json的具体时间

举个例子，比如有一条叫做 `"北京-2020/04/05": "2020/11/29"` 的数据，意思是北京这个地方在4月5号访问cgi网站的时候，显示最早日期是11月29日。

## 邮件系统

邮件系统主文件夹位于 `/asiv`，详情参考对应文件夹下的[readme](asiv/readme.md)

## QQ、Telegram通知

QQ使用mirai第三方框架，部署在前端服务器中，需要的参数为：

- `mirai_base_uri`：string，mirai的java接口地址
- `mirai_auth_key`：string，认证秘钥
- `qq_num`：string，机器人的qq号
- `qq_group_id`：List[string]，通知群的号码

Telegram本身支持API调用来进行通知，需要的参数为：

- `tg_bot_token`：string，Telegram bot的id
- `tg_chat_id`：string，channel的id
