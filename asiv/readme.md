# 邮件系统

主要逻辑位于 `index.php` 和 `notify.py` 中。

## 文件存储结构

```bash
$  tree asiv/email        
asiv/email
├── b
│   ├── bj
│   ├── cd
│   ├── gd
│   ├── hk
│   ├── sh
│   └── sy
│       └── trinkle23897@gmail.com
├── f
│   ├── bj
│   ├── cd
│   ├── dxb
│   │   └── trinkle23897@gmail.com
│   ├── gd
│   ├── hk
│   ├── pp
│   │   └── trinkle23897@gmail.com
│   ├── sh
│   └── sy
...
└── tmp
    ├── trinkle23897@gmail.com
...
```

email文件夹下有 `b`、`f`、`o`、`h`、`l`和`tmp`一共6个文件夹。前五个称之为type，最后一个 `tmp` 是用于记录邮箱的信息，文件名为邮箱，内容为订阅过期时间（订阅早于并包含xxx的变动时间）

形式化一下就是有两种类型的路径：

1. `/asiv/email/tmp/{email}` 存放了订阅日期；
2. `/asiv/email/{type}/{code}/{email}` 存放了用户的订阅选项。这个路径下的所有文件都是空文件。

此处的 `code` 是每个地方的代码。国内版使用拼音，国际版使用airport code，如下表所示：

| code            | location        | 备注             |
| --------------- | --------------- | ---------------- |
| bj              | 北京            |                  |
| cd              | 成都            |                  |
| gz              | 广州            |                  |
| sh              | 上海            |                  |
| sy              | 沈阳            |                  |
| hk              | 香港            |                  |
| tp              | 台北            |                  |
| pp              | 金边            | 不是airport code |
| sg              | 新加坡          | 不是airport code |
| 其他ais/cgi地点 | 其他ais/cgi地点 | 均为airport code |

## 订阅邮件接口

main uri为 `/asiv/`，请求分为两次，一次是校验邮件，用于确认邮箱是否能收到邮件，同时避免一些垃圾用户注册（比如写个python疯狂request这个接口之类的）；第二次是确认邮件

第一次邮件：

| Query   | Type    | Required | Explanation                                                  |
| ------- | ------- | -------- | ------------------------------------------------------------ |
| glob    | string  | False    | 如果不为空，则表示是国际版过来的请求，否则是国内版的请求     |
| email   | string  | True    | 邮箱                                                       |
| time   | string  | True    | 订阅过期时间，格式为 `YYYY-MM-DD`，如果日期为空的话则默认为无限长的订阅时间 |
| visa[]  | string+ | True     | 可以为多个，每个的值为 `{type}{code}`，比如 `visa[]=bgz&visa[]=hbj` 表示订阅广州的b签和北京的h签信息 |
| captcha | string  | True     | 验证码信息                                                   |
| orig    | string  | True     | 校验码，我也忘了是怎么来的，看看代码                         |

第二次邮件：

| Query   | Type    | Required | Explanation                                                  |
| ------- | ------- | -------- | ------------------------------------------------------------ |
| glob    | string  | False    | 如果不为空，则表示是国际版过来的请求，否则是国内版的请求     |
| liame | string  | True    | 邮箱                                                       |
| visa[]  | string+ | True     | 可以为多个，每个的值为 `{type}{code}`，比如 `visa[]=bgz&visa[]=hbj` 表示订阅广州的b签和北京的h签信息 |

## 发送邮件逻辑

写在了 `notify.py` 里面，大概意思是如果发现了时间的变动，则查找并匹配当前一共有多少用户需要通知，然后合在一起发送。

发送邮件一次性限定为512个邮箱，如果大于1000的话好像会发不出去。然后能一起发（指内容一样）就一起发，会比一个个发快不少。

发送邮件采取（我自己搭的）第三方服务，只需要http post到一个api链接即可，参数为：

| Query     | Type   | Required | Explanation                                                  |
| --------- | ------ | -------- | ------------------------------------------------------------ |
| content   | string | True     | 邮件内容                                                     |
| receivers | string | True     | 邮箱列表，不同邮箱由 `@@@` 拼接起来，比如 `a@gmail.com@@@b@qq.com` |
| title     | string | True     | 邮件标题                                                     |
| sendfrom  | string | True     | 邮件中显示的发件人                                           |
| sendto    | string | True     | 邮件中显示的收件人                                           |