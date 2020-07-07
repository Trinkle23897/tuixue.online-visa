# 爬虫 HTTP API

使用 Python Django 框架构建，配置文件为 `tuixue/setting.py`

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
