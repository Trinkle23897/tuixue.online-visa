# 爬虫 HTTP API

使用 Python Django 框架构建，配置文件为 `tuixue/setting.py`

## 0. 部署

安装环境

```bash
pip3 install uwsgi django selenium
# and install chrome-driver
```

运行：`./run.sh` 或者 `python3 manage.py runserver 0:8888`

## 1. 服务器连接检测

### 请求地址 

```
GET /
```

### 请求参数 

无

### 返回值

若连接成功，返回一个JSON Object.

|属性|类型|说明|
|----|----|----|
|code|int|状态码，若连接成功则为 0|
|msg|str|消息内容，若连接成功则为 "OK"|

### 示例代码

```
curl -XGET "http://www.example.com:8080/"
```
### 返回数据示例

```
{"code": 0, "msg": "OK"}
```

## 2. 获取一个新的 session

### 请求地址 

```
GET /register/
```

### 请求参数 

|属性|类型|必填|说明|
|----|----|----|----|
|type|str|是|需要选定的签证类型，有效的值为"F", "B", "H", "O", "L"|
|place|str|是|需要选定的地点，有效的值为"北京", "上海", "广州", "成都", "沈阳", "香港", "台北"|


### 返回值

若连接成功，返回一个JSON Object.

| 属性 | 类型 | 说明 |
|------|------|------|
|code|int|状态码，若成功获取则为 0|
|msg|str|错误信息，若成功获取到 session 则为最早可预约日期 |
|session|str|获取到的 session|

### 示例代码

```
curl -XGET "http://www.example.com:8080/register/?type=F&place=北京"
```
### 返回数据示例

```
{"code": 0, "msg": "2020-11-29", "session": "00DC0000000PhuP!ARwAQDxY1y7QP_9g_iho89dL7fTy4lzBTlcdaFnbpK3etTy6IDR36NmsiAewyUL4TtmWyN6KBRIBcAaDm.QreI4wPr_4i5cI"}
```

## 3. 使用 session 获取最早可预约日期

### 请求地址 

```
GET /refresh/
```

### 请求参数 

|属性|类型|必填|说明|
|----|----|----|----|
|session|str|是|需要使用的 session|


### 返回值

若连接成功，返回一个JSON Object.

| 属性 | 类型 | 说明 |
|------|------|------|
|code|int|状态码，若成功获取则为 0|
|msg|str|错误信息或最早可预约日期|

### 示例代码

```
curl -XGET "http://www.example.com:8080/refresh/?session=00DC0000000PhuP!ARwAQDxY1y7QP_9g_iho89dL7fTy4lzBTlcdaFnbpK3etTy6IDR36NmsiAewyUL4TtmWyN6KBRIBcAaDm.QreI4wPr_4i5cI"
```
### 返回数据示例

```
{"code": 0, "msg": "2020-11-29"}
```

## 4. 登陆 AIS，获取一个新的 session

### 请求地址 

```
GET ais/register/
```
* 注：账户需要在对应的地区手动完成注册

### 请求参数 

|属性|类型|必填|说明|
|----|----|----|----|
|code|str|是|AIS 中的国家码，例如 en-gb 代表英国|
|email|str|是|账户的电子邮件|
|pswd|str|是|账户密码|

### 返回值

若连接成功，返回一个JSON Object.

| 属性 | 类型 | 说明 |
|------|------|------|
|code|int|状态码，若成功获取则为 0|
|msg|str or dict|错误信息或最早可预约日期|
|id|str|预约 ID|

### 示例代码

```
curl -XGET "http://www.example.com:8080/ais/refresh/?code=en-gb&email=admin@test.com&pswd=123456"
```
### 返回数据示例

```
{"code": 0, "msg": [["Belfast", [2020, 8, 18]], ["London", [2020, 8, 19]]], "session": "STk4VkRENXd4Ykg2MUdzaXBrSmRsMktBMmZuYUMwTmQzMDVlcVJsOS93NmdJL2hUQXkxdUhHbkFJd1ExaFJuenRQZGV4clNyckNzVUlDWEp6TWtKeG5PTnhwU1owSEVSZEw1WjByc2NyMUp3TVdqTzlTbDQ5UGJLdUwxN3hVbnVuNlZpYnRSOFJzNVRXd3dvV01ZcnlnWU5kZ0drVFBZZ0UvWVp1SjdnMGpQN2FKNE5WNGVWQnRPQ3lEd1IwWldRY0tUZjRXRzN1dE05T3RjUXNYenNBa0pMcHVuSVpSUHpDVEE1dzdjNVlqU1REaG9ZeFF5UU0xblh4aVdLb3ltbC9ZbDNNQVE2Vy9RQnRtVmcwQ0dydm42WnQ2NDk4V2pER3hSQnRrTHFRRWFMdi8rWHMyRHhYL1NjOVl5MFBSb1BOMjQ5OUFsZDgxY2pWazJNd2NFTnRxVXcweXdaU0ZVRWVtUUoxaDY4SkM1L2ExN0REazQ5bDBnTy9Fc0NyVWZ0ZDZjZllKQ1BQVmNJTzhJUW53NU5RdTBlbEVERDZnblNicmJBeUNHR0laYTV4TDZaZWFweDQ4WXlOZ0FEUXNrdmFZeEUveCtwU2hZSy96djZwK1JLSEFKWGVGL0RORXRNYzJiSmdFSGpJWk09LS1XR0hXdmdwdkpFRElHNVpGZCtESjhRPT0%3D--a118fe85c973364d2ac0eb7750f12b847c276a25", "id": "31717795"}
```

## 5. 使用 AIS session 获取最早可预约日期

### 请求地址 

```
GET ais/refresh/
```

### 请求参数 

|属性|类型|必填|说明|
|----|----|----|----|
|code|str|是|AIS 中的国家码，例如 en-gb 代表英国|
|id|str|是|AIS 中显示的预约 ID|
|session|str|是|需要使用的 session|

### 返回值

若连接成功，返回一个JSON Object.

| 属性 | 类型 | 说明 |
|------|------|------|
|code|int|状态码，若成功获取则为 0|
|msg|str or dict|错误信息或最早可预约日期|
|session|str|新的 session|

* 注：在请求完成后，旧 session 立即失效，请记录下新的 session 以便下次使用。

### 示例代码

```
curl -XGET "http://www.example.com:8080/ais/refresh/?code=en-gb&id=31717795&session=STk4VkRENXd4Ykg2MUdzaXBrSmRsMktBMmZuYUMwTmQzMDVlcVJsOS93NmdJL2hUQXkxdUhHbkFJd1ExaFJuenRQZGV4clNyckNzVUlDWEp6TWtKeG5PTnhwU1owSEVSZEw1WjByc2NyMUp3TVdqTzlTbDQ5UGJLdUwxN3hVbnVuNlZpYnRSOFJzNVRXd3dvV01ZcnlnWU5kZ0drVFBZZ0UvWVp1SjdnMGpQN2FKNE5WNGVWQnRPQ3lEd1IwWldRY0tUZjRXRzN1dE05T3RjUXNYenNBa0pMcHVuSVpSUHpDVEE1dzdjNVlqU1REaG9ZeFF5UU0xblh4aVdLb3ltbC9ZbDNNQVE2Vy9RQnRtVmcwQ0dydm42WnQ2NDk4V2pER3hSQnRrTHFRRWFMdi8rWHMyRHhYL1NjOVl5MFBSb1BOMjQ5OUFsZDgxY2pWazJNd2NFTnRxVXcweXdaU0ZVRWVtUUoxaDY4SkM1L2ExN0REazQ5bDBnTy9Fc0NyVWZ0ZDZjZllKQ1BQVmNJTzhJUW53NU5RdTBlbEVERDZnblNicmJBeUNHR0laYTV4TDZaZWFweDQ4WXlOZ0FEUXNrdmFZeEUveCtwU2hZSy96djZwK1JLSEFKWGVGL0RORXRNYzJiSmdFSGpJWk09LS1XR0hXdmdwdkpFRElHNVpGZCtESjhRPT0%3D--a118fe85c973364d2ac0eb7750f12b847c276a25"
```
### 返回数据示例

```
{"code": 0, "msg": [["Belfast", [2020, 8, 18]], ["London", [2020, 8, 19]]], "session": "VWdGZ2lWcExsU1ltcWx3SWZzc25NY3prRk9qWGxMUGJhTUVxOUdqOEpzTWRydjFNTzFxQzNRejJLeVpZd2VaN0h4QnlIYUxCUDgvYURiNnA3dm9VeVVFQ1Z4RVpGRVVpOHoyaEZZTzErOGJSbDJlQ1dIZTNyQnhZMkR1S3NtTFpWcndXVXp0UlFCTmRjd3N3bDQ5VnQ3R2FsbmY2bXd0c1dBK1VxZjlYcUZ3am9iSFhOb3NRSWNtbTFGZE5ncXBBaDQxKzZ5UHYzSmZ5RnNqc292NlVBdnNCMGYzdVFKUERUNFl0Y2lnQjFEVjNqMjhSem5FT2RERk9GYW1EQ21zUm15MFZWby92YUJVaDFpVFBZLzlzV05UQXRSZmV6NGFZUXNUdlBSWUFsZFA1WThFWVhCUzNRV3ZnMVg3SVB2TXB1dnNTU0NEc0pySnlEbm1JMC9sa213aldQbmZWUzM4bDNaa1paYWxIMy80QXcyaEp2bHJxTVhBNzhUOWpoY2tWNFdJYVlSUEVsSEc3QjJzbG9ySjVtVDUvTmh1b21Pby95NE9XbW5LQVEwMGxXODNrektYY1NZSXBQaitBL0ZZdEo4cTA4bkJ2eW5Md0pubHIrcnI5NVR6TE5TWWJNeU5FQURPd2ZVV05QSmM9LS2Mai9XTDF2SW50Y3QwYXpyUEVYUTR3PT0%3D--6244b7f52393029b4958c27f545af548dc85f43d"}
```
