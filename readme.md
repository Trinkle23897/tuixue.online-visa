# 美国签证预约时间 自动化爬取+邮件推送

[https://tuixue.online/visa/](https://tuixue.online/visa/)

## Dependency

没从零重新部署过，缺了啥import不了就安装啥，啥文件夹没创建就mkdir一下

前端采用<s>apache2+php部署</s>改成了nginx+静态html，后端python3+<s>selenium</s>改成了request，没有使用数据库（因为太懒了而且之前也没用过）

## Usage

在visa2文件夹下起一个 `python3 visa.py --secret your_secret` 即可，其中your\_secret是一个文件，包含你的[斐斐打码平台](http://www.fateadm.com/)上的pd\_id和pd\_key。如果没有的话，bhys就只能手动命令行输入验证码

改进版爬虫：详见 [#12](https://github.com/Trinkle23897/us-visa/pull/12)

visa2/notify.py是更新的脚本，包含了邮件推送功能+主页刷新功能（主页手动做了下cache，直接php的话会有效率问题）。

出于某些原因，邮件推送功能的api不对外公布。（因为阿里云25端口被封的死死的，所以只好想些别的dirty implementation）

asiv文件夹下存放邮件订阅状态，出于安全考虑，请在apache2/nignx配置文件中加入重定向 `/asiv/email` 至首页。
