# 美国签证预约时间 自动化爬取+邮件推送

[https://tuixue.online/visa/](https://tuixue.online/visa/)

## Dependency

没从零重新部署过，缺了啥import不了就安装啥

前端采用apache2+php部署，后端python3+selenium，没有使用数据库（因为太懒了而且之前也没用过）

## Usage

在visa2文件夹下起一个 `python3 visa2.py --secret your_secret` 即可，其中your\_secret是一个文件，包含你的[斐斐打码平台](http://www.fateadm.com/)上的pd\_id和pd\_key。如果没有的话，bhys就只能手动命令行输入验证码

visa2/notify.py是更新的脚本，包含了邮件推送功能+主页刷新功能（主页手动做了下cache，直接php的话会有效率问题）。

出于某些原因，邮件推送功能的api不对外公布。（阿里云25端口被封的死死的）

asiv文件夹下存放邮件订阅状态。
