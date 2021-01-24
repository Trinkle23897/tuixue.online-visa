# 美国签证预约时间 自动化爬取+推送通知

[https://tuixue.online/visa/](https://tuixue.online/visa/)

包含国内以及国外各种地区，目前包含：

- CGI系统：中国、柬埔寨、新加坡、韩国、越南、巴拿马、澳大利亚、日本、尼泊尔、泰国
- AIS系统：英国、加拿大、阿联酋、厄瓜多尔、法国、塞尔维亚、土耳其、希腊、哥伦比亚、墨西哥

## Overview

目前采用的是部分前后端分离，姑且将其称之为前端服务器和爬虫服务器。整体逻辑为前端服务器定时向爬虫服务器发送数据请求，拉取到其本地、更新数据库、推送通知。

爬虫服务器使用Django构建，代码位于 [api](/api) 文件夹下，CGI系统使用纯requests拉取数据，AIS系统由于有recaptcha2，使用requests和selenium/xdotool混合模式拉取数据（感谢[z3dd1cu5](https://github.com/z3dd1cu5)）

~~前端服务器采用nginx部署，使用python和爬虫服务器进行交互（详见lite_visa.py），和用户交互使用静态html或者php~~

前端服务器采用Nginx部署，使用FastAPI前后端分离，使用python和爬虫服务器进行交互（详见[backend/visa_status_fetcher.py](/backend/visa_status_fetcher.py)），使用mongo存储数据，前端网页使用React+Redux，展示表格使用EChart，评论区使用Disqus第三方服务，使用WebSocket+WebNotification实现网页版穿透通知（感谢[BenjiTheC](https://github.com/BenjiTheC)）

邮件通知、QQ群和Telegram channel通知均使用python实现，详见[backend/Notifier.py](/backend/Notifier.py)

## Usage

爬虫的使用请移步 [api](/api)，包括各种请求字段，甚至免费的CGI验证码破解器也有（准确率大概98%）

前端部署详见 [backend](/backend) 和 [frontend](/frontend)

## API

https://api.tuixue.online/docs

请善待它orz，频繁请求会造成服务器卡死，建议一分钟一次请求（不过都做了网页版穿透通知了……直接开着网页或者加了QQ群、Telegram频道就能收到通知，为啥还要自己造个轮子呢？

