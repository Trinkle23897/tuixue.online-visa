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

**This code base is developed with Python >= 3.7**

#### Python dependency

```bash
pip3 install -r requirements.txt
```

#### Visa Status Fetcher

`visa_status_fetcher.py` is the script for fetching new available visa appointment date from the crawler backend. This script is design to run separated from FastAPI so that the request load of crawler server is controlled under a resasonable level. It comes with a simple command line interface.

```sh
$ python3 visa_status_fetcher.py --help
usage: visa_status_fetcher.py [-h] --target {ais,cgi} [--proxy PROXY]
                              [--crawler CRAWLER] [--ais AIS]
                              [--log_dir LOG_DIR] [--log_name LOG_NAME]
                              [--debug]

optional arguments:
  -h, --help           show this help message and exit
  --target {ais,cgi}   targeting system
  --proxy PROXY        local proxy port
  --crawler CRAWLER    crawler api list
  --ais AIS            ais account in json format
  --log_dir LOG_DIR    directory to save logs
  --log_name LOG_NAME  name of log file
  --debug              log debug information
```

`--target` specifies the system used by a U.S. embassy/consulate. In order to fetch both AIS and CGI system, one should run two processes of this script separately.

`--proxy` is a legacy argument from previous version of the fetcher. The functionality and mechanism remains unchanged.

`--cralwer` requires a text file that contains the address of crawler servers.

`--ais` requires a JSON file containing the user names and passwords of users in AIS systems. It's needed for crawler server to obtain available Visa appointment date.

`--log_dir` and `--log_name` are optional parameters which allow you to specify where to store the log files. It's default to log files `./logs/{target}_visa_fetcher` where `target` is sepcified by `--target` argument.

`--debug` is a flag that provides a richer content of logging for development.

**Run following command for fetching the CGI system:**

```sh
python3 visa_status_fetch.py --target cgi --crawler path/to/crawler_file
```

**Run following command for fetching the AIS system:**

```sh
python3 visa_status_fetch.py --target ais --crawler path/to/crawler_file --ais path/to/ais.json
```

#### MongoDB

The newly developed backend uses [MongoDB Communitry Edition v4.4](https://docs.mongodb.com/manual/introduction/) for the database solution. To install the MongoDB in Ubuntu (or other Linux distro, including Amazon Linux 2), see the thorough offical documentation here:

- For Ubuntu: [Install MongoDB on Ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
- For other OS: [Install MongoDB Community Edition](https://docs.mongodb.com/manual/installation/#mongodb-community-edition-installation-tutorials)

> **P.S.** MongoDB runs on port **27017** by default. Seal this port in production server.

#### MongoDB data migration

##### Write from scratch with file-based data

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

##### Use `mongodump` and `mongorestore` for database backup

> Both `mongodump` and `mongorestore` are installed when we install MongoDB

**Backup `tuixue.visa_status`**

The dev server has been running for a while, the data fetched by `visa_status_fetcher.py` is proved to be trusted and has a different granularity to microseconds. Therefore a new database initialization method has been written to use with combination of `mongodump` and `mongorestore` utilities.

Logically speaking, the only data worth for backing up is the successful fetched result of visa status, namely the MongoDB collection `tuixue.visa_status`, the other collection `tuixue.overview` is essentially computed from the data in `tuixue.visa_status`. To dump the data from database into a BSON file, run the following command.

```sh
mongodump --db tuixue --collection visa_status --out path/to/empty/dir
```

This command will export all the data in `tuixue.visa_status` collection to the **empty** directory given in the option `--out`.

To restore the data from dumped directory into the database. We can use `mongorestore` command as follow:

```sh
mongorestore --db tuixue path/to/empty/dir/tuixue --drop
```

This command restore the database `tuixue` from the backup.

> _P.S: `path/to/empty/dir` needs to be empty. In the dev server the `path/to/empty/dir` is set to `/root/mongodb_backup`_

**Restore `tuixue.overview`**

A new class method, `restore_overview`, is added into the class `tuixue_mongodb.VisaStatus`. **After restoring the `tuixue.visa_status` as instructed above**, run a single line of python command:

```sh
python3 -c "import tuixue_mongodb as DB; DB.VisaStatus.restore_overview();"
```

And it will read and compute the `tuixue.overview` collection (with a bunch of printed info on the screen ;-)

#### Nginx proxy and run the api server with `uvicorn`

The api server is developed with [FastAPI](https://fastapi.tiangolo.com/), which is said to be one of the most performant api framework in Python, better than Flask and Django. Personally I find it more pythonic (than Django) and better documented (than Flask).

The FastAPI use the [uvicorn](https://www.uvicorn.org/) as ASGI server. But first let's look at Nginx.

With the help of [official documentation](https://www.uvicorn.org/deployment/#running-behind-nginx), I inserts the following block in my `http` context in `nginx.conf`

```nginx
server {
        listen       80 default_server;
        listen       [::]:80 default_server;
        server_name  _ 127.0.0.1;

        location = /status {
                stub_status on;
        }

        location /ws/ {  # The trailing slash MATTERS!!
                proxy_http_version 1.1;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "Upgrade";
                proxy_set_header Host $host;
                proxy_buffering off;
                proxy_pass http://uvicorn_ws/;  # The trailing slash MATTERS!!
        }

        location / {
                proxy_set_header Host $http_host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_redirect off;
                proxy_buffering off;
                proxy_pass http://uvicorn_http;
        }
}

upstream uvicorn_ws {
        server unix:/tmp/uvicorn_ws.sock;
}

upstream uvicorn_http {
        server unix:/tmp/uvicorn_http.sock;
}
```

**Important Note**: You must notice here we have two `upstream` block which essentially are two Uvicorn server running two FastAPI, **One for HTTP RESTful API and another one for WebSocket connection.**. And the location `/` and `/ws/` proxy the requests to these two servers accordingly. This is because mixing the code of RESTful API and WebSocket and proxying on in route doesn't work in FastAPI, the request headers setting for HTTP and WS protocol are different and will result in malfunction of the server.

After update the Nginx configuration file, reload the Nginx

```shell
sudo nginx -s reload
```

And run the uvicorn in two tmux windows (didn't use the process manager or anything, just make it run then detach the session) with following commands:

- HTTP server

    ```shell
    python3 -m uvicorn api_http:app --uds /tmp/uvicorn_http.sock --proxy-headers --forwarded-allow-ips '*'
    ```

- WebSocket server

    ```shell
    python3 -m uvicorn api_websocket:app --uds /tmp/uvicorn_ws.sock --proxy-headers --forwarded-allow-ips '*' --ws websockets
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
        {"region": "DOMESTIC", "embassy_code_lst": ["bj", "sh", "cd", "gz", "sy", "hk", "tp"]},
        {"region":"SOUTH_EAST_ASIA","embassy_code_lst":["pp","sg","ktm","bkk","cnx"]}
    ],
    "embassy": [
        ["北京", "Beijing", "bj", "cgi", "DOMESTIC", "ASIA", "CHN"],
        ["金边", "Phnom Penh", "pp", "cgi", "SOUTH_EAST_ASIA", "ASIA", "KHM"],
        ["伦敦", "London", "lcy", "ais", "WEST_EUROPE", "EUROPE", "GBR"]
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
|---|---|---|
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
|---|---|---|
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
POST /subscribe/email/{step}
```

Post email subscription data to the backend. This endpoint is supposed to be pinged twice for a successful subscription. The endpoint is still in the middle of develoment.
