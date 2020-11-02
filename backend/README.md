# Backend API

## Intro

This folder contains the code that:

1. Fetch and udpate available visa appointment date for both domestic and global embassy/consulate from crawler servers.
2. Send notification to the users who subscribe via email and other social media platforms
3. Expose RESTful api to provide data for tuixue global frontend views and other dope developers (a.k.a desperate CS students)

~~This api server should be designed to *be extensible to serve as domestic api with another set of secret files*. Please review the PR based on this principle :)~~

## Deployment and Dependency

### Deployment

> This section is for setting up the RESTful api server and exposing the routes through NGINX to perform stress test.
>
> It's noteworthy that it's _NOT_ what the backend api server orignally designed to run. **In the production the api server and React frontend will be deployed in the same machine and the api server will _NOT_ be exposed to the public until further decision is made.**

**This code base is developed with Python >= 3.6**

#### Python dependency

```bash
pip3 install -r requirements.txt
```

##### A detail caveat in the code

In the `notifier.py`, I specify a global variable `SECRET` which is a dictionary containing the email server url and other social media secret like Telegram bot tokens. The dictionary is read from a JSON file in the path `./config/secret.json`. The `config` folder was manuanlly created to store the secret files used to access crawler node. In this circumstances, only the `./config/secret.json` to have the backend api server to run. (This file path should be written in a more configurable way in the future commits.)

#### MongoDB

The newly developed backend uses [MongoDB Communitry Edition v4.4](https://docs.mongodb.com/manual/introduction/) for the database solution. To install the MongoDB in Ubuntu (or other Linux distro, including Amazon Linux 2), see the thorough offical documentation here:

- For Ubuntu: [Install MongoDB on Ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
- For other OS: [Install MongoDB Community Edition](https://docs.mongodb.com/manual/installation/#mongodb-community-edition-installation-tutorials)

> **P.S.** MongoDB runs on port **27017** by default. Seal this port in production server.

#### MongoDB data migration

Previously, all the fetched data are stored in a folder structured as follow:

```sh
- backend
    |-data
        |-{visa_type}
            |-{location}
                |-{YYYY}
                    |-{MM}
                        |-{DD}  # this is a file
```

Where `visa_type` is as specified in the `global_var.py` with the string `VISA_TYPES`. And `location` are the Chinese name of a embassy/consulate for cgi system and English name of a embassy/consulate for ais system. `YYYY` stands for year, `MM` stands for month and `DD` stands for day.

To migrate the fetched data from files into the MongoDB, I wrote a script, `sync_data.py`, to write the data into database. It was originally written for fetching the historic data from production server to local machine for development, so it contains a simple CLI.

```sh
$ python3 sync_data.py --help
usage: sync_data.py [-h] --operation {fetch,write} [--since SINCE]

optional arguments:
  -h, --help            show this help message and exit
  --operation {fetch,write}, -o {fetch,write}
                        Choose what function to run
  --since SINCE, -s SINCE
                        Date string indicating the start date of fetching data
```

To write the data into MongoDB, run

```sh
python3 sync_data.py -o write -s 2020/4/8  # or any other date after the start date
```

It will write all the data fetched after the given `since` date till yesterday.

**P.S.**: You will need to move the data from other places to ./data folder. Or change the value of `DATA_PATH` variable in `global_var.py`

#### Nginx proxy and run the api server with `uvicorn`

The api server is developed with [FastAPI](https://fastapi.tiangolo.com/), which is said to be one of the most performant api framework in Python, better than Flask and Django. Personally I find it more pythonic (than Django) and better documented (than Flask).

The FastAPI use the [uvicorn](https://www.uvicorn.org/) as ASGI server. But first let's look at Nginx.

With the help of [official documentation](https://www.uvicorn.org/deployment/#running-behind-nginx), I inserts the following block in my `http` context in `nginx.conf`

```nginx
    server {
        listen       443 ssl http2;
        listen       [::]:443 ssl http2;
        server_name  api.tuixue.online 127.0.0.1; # managed by Certbot


        ssl_certificate /etc/letsencrypt/live/api.tuixue.online/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/api.tuixue.online/privkey.pem; # managed by Certbot
        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout  10m;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;


        location / {
          proxy_set_header Host $http_host;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_redirect off;
          proxy_buffering off;
          proxy_pass http://uvicorn;
        }
    }

    upstream uvicorn {
        server unix:/tmp/uvicorn.sock;
    }
```

After update the Nginx configuration file, reload the Nginx

```shell
sudo nginx -s reload
```

And run the uvicorn in a tmux window (didn't use the process manager or anything, just make it run then detach the session) with following option:

```shell
uvicorn api:app --uds /tmp/uvicorn.sock --proxy-headers --forwarded-allow-ips '*'
```

### Configuration Files

The necessary configuration files for accessing the crawler servers and scrape data from the embassy/consulate website is held privately by the developers. For detail on HOWTO please contact us.

## API Reference

### Handshake - test connection

```sh
GET /
```

#### Parameters

No Parameter

#### Responses

```sh
HTTP/1.1 200 OK
```

```json
{
    "statusCode": 200,
    "msg": "OK"
}
```

### Visa Status Metadata

```sh
GET /visastatus/meta
```

This endpoint serve the metadata including filtering methods and embassy attributes to the frontend for building filtering of display of visa status. Frontend doesn't hold and global/static variable storing this data, so that it's kept up to date with the backend.

#### Parameters

No Parameter

#### Responses

```sh
HTTP/1.1 200 OK
```

```json
{
    "region": [
        {"region": "DOMESTIC", "embassy_code_lst": ["bj", "sh", "cd", "gz", "sy", "hk", "tp"]}
    ],
    "embassy": [
        ["北京", "Beijing", "bj", "cgi"]
    ]
}
```

### Get overview of Visa appointment date

```sh
GET /visastatus/overview
```

Return the overview: earliest and latest available appointment date for any given date of a visa type and embassy/consulate. The endpoint will return the earliest dates of given `(visa_type, embassy_code)` permutation grouped by write date. Note that all `(visa_type, embassy_code)` combo results, if exist, will be mixed together by write date. It's frontend's job to decide how to use them.

#### Parameters

| Param | Type | Description |
|---|---|---|---|
|`visa_type`|`list`|Required. List of types of visa for the returning visa status. One of `['B', 'F', 'H', 'O', 'L']`.|
|`embassy_code`|`list`|Required. List of codes of embassy/consulate for returning visa status. One of `['bj', 'sh', 'cd', 'gz', 'sy', 'hk', 'tp', 'pp', 'sg', 'sel', 'mel', 'per', 'syd', 'brn', 'fuk', 'itm', 'oka', 'cts', 'hnd', 'ktm', 'bkk', 'cnx', 'bfs', 'lcy', 'yyc', 'yhz', 'yul', 'yow', 'yqb', 'yyz', 'yvr', 'auh', 'dxb', 'beg', 'cdg', 'gye', 'uio', 'esb', 'ist', 'ath', 'bog', 'bgi', 'cjs', 'gdl', 'hmo', 'cvj', 'mex', 'mty', 'ols', 'nld', 'tij']`|
|`since`|`string`|Default to 15 days before today. The endpoint will return the data after `since` date. The string **MUST** in the format of a UTC time string, e.g. `2020-10-17T22:13:54.617098`.|
|`to`|`string`|Default to today. The endpoint will return the data before `to` date. The string **MUST** in the format of a UTC time string, e.g. `2020-11-01T22:13:54.617110`.|

#### Responses

**Success**:

```sh
HTTP/1.1 200 OK
```

```json
{
    "visa_type": ["F", "H"],
    "embassy_code": ["pp", "bkk"],
    "since": "2020-10-17T00:00:00",
    "to": "2020-11-01T00:00:00",
    "visa_status": [
        {
            "date": "YYYY-MM-DDT00:00:00",
            "overview": [
                {"visa_type": "F", "embassy_code": "pp", "earliest_date": "YYYY-MM-DDT00:00:00", "latest_date": "YYYY-MM-DDT00:00:00"},
                {"visa_type": "H", "embassy_code": "bkk", "earliest_date": "YYYY-MM-DDT00:00:00", "latest_date": "YYYY-MM-DDT00:00:00"},
            ]
        },
    ]
}
```

### Get latest fetched visa status record

```sh
GET /visastatus/latest
```

Return the latest fetch record of all given Visa types and embassy codes. Return the `(visa_type, embassy_code)` pair's latest fetched result, _including the failed fetch_.

#### Parameters

| Param | Type | Description |
|---|---|---|---|
|`visa_type`|`list`|Required. List of types of visa for the returning visa status. One of `['B', 'F', 'H', 'O', 'L']`.|
|`embassy_code`|`list`|Required. List of codes of embassy/consulate for returning visa status. One of `['bj', 'sh', 'cd', 'gz', 'sy', 'hk', 'tp', 'pp', 'sg', 'sel', 'mel', 'per', 'syd', 'brn', 'fuk', 'itm', 'oka', 'cts', 'hnd', 'ktm', 'bkk', 'cnx', 'bfs', 'lcy', 'yyc', 'yhz', 'yul', 'yow', 'yqb', 'yyz', 'yvr', 'auh', 'dxb', 'beg', 'cdg', 'gye', 'uio', 'esb', 'ist', 'ath', 'bog', 'bgi', 'cjs', 'gdl', 'hmo', 'cvj', 'mex', 'mty', 'ols', 'nld', 'tij']`|

#### Responses

**Success**:

```sh
HTTP/1.1 200 OK
```

```json
[
    {"visa_type": "F", "embassy_code": "pp", "write_time": "YYYY-MM-DDTHH:MM:SS", "available_date": null},
    {"visa_type": "F", "embassy_code": "bj", "write_time": "YYYY-MM-DDTHH:MM:SS", "available_date": "YYYY-MM-DDT00:00:00"}
]
```

### Email Subscription

```sh
POST /subscribe/email/{rep}
```

Post email subscription data to the backend. This endpoint is supposed to be pinged twice for a successful subscription. The endpoint is still in the middle of develoment.
