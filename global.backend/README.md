# Global Backend API

This folder contains the code that:

1. Fetch and udpate available visa appointment time data from crawler servers.
2. Send notification to the users who subscribe via email and other social media platforms
3. Expose RESTful api to provide data for tuixue global frontend views and other dope developers(a.k.a desperate CS students)

This api server should be designed to *be extensible to serve as domestic api with another set of secret files*. Please review the PR based on this principle :)

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

### Get *GLOBAL* latest update and earliest Visa appointment date

```sh
GET /backend/global
```

Return the tabular date for rendering the **global** visa appointment date availability table. The row is indexed by date and the column by location. If there is no available earliest or latest date for a location, a `null` value will be returned for the location.

#### Parameters

| Param | Type | Description |
|---|---|---|
|`visa_type`|`string`|Type of visa for the returning visa status. One of `['B', 'F', 'H', 'O', 'L']`. Default to `'F'`|
|`sys`|`string`|The system used by the U.S. embassies/consulates. One of `['cgi', 'ais']`. Default to `'cgi'`|
|`region`|`string`|Region where the U.S. embassies/consulates locate in. One of `['SOUTH_EAST_ASIA', 'EAST_ASIA', 'WEST_ASIA', 'SOUTH_ASIA', 'OCEANIA', 'WEST_EUROPE', 'EAST_EUROPE', 'NOTRH_AMERICA', 'SOUTH_AMERICA']`. Default to `null`|
|`exclude_demostic`|`boolean`|Whether or not exclude the embassy/consulate in China, default to `true`. _P.S.: This field is set for possible feature extension in the future, we have a API specifically serve data of demostic embassy/consulates._|
|`skip`|`int`|Number of dates to skip for returning data. Default to `0`, use with `take` for pagination (if needed)|
|`take`|`int`|Number of dates to take for returning data. Default to `15`, use with `skip` for pagination (if needed)|

#### Responses

**Success**:

```sh
HTTP/1.1 200 OK
```

```json
{
    "visa_type": "F",
    "region": "SOUTH_EAST_ASIA",
    "sys": "cgi",
    "visa_status": [
        {
            "date": "YY/MM/DD",
            "availability": [
                {"location": "pp", "earliest": "YY/MM/DD", "latest": "YY/MM/DD"},
                {"location": "bkk", "earliest": "YY/MM/DD", "latest": "YY/MM/DD"},
                ...
            ]
        },
        ...
    ]
}
```

### Get *DOMESTIC* latest update and earliest Visa appointment date

```sh
GET /backend/domestic
```

Return the tabular date for rendering the **domestic** visa appointment date availability table. The row is indexed by date and the column by location. If there is no available earliest or latest date for a location, a `null` value will be returned for the location.

#### Parameters

| Param | Type | Description |
|---|---|---|
|`visa_type`|`string`|Type of visa for the returning visa status. One of `['B', 'F', 'H', 'O', 'L']`. Default to `'F'`|
|`skip`|`int`|Number of dates to skip for returning data. Default to `0`, use with `take` for pagination (if needed)|
|`take`|`int`|Number of dates to take for returning data. Default to `15`, use with `skip` for pagination (if needed)|

### Response

**Success**:

```sh
HTTP/1.1 200 OK
```

```json
{
    "visa_type": "F",
    "visa_status": [
        {
            "date": "YY/MM/DD",
            "availability": [
                {"location": "pp", "earliest": "YY/MM/DD", "latest": "YY/MM/DD"},
                {"location": "bkk", "earliest": "YY/MM/DD", "latest": "YY/MM/DD"},
                ...
            ]
        },
        ...
    ]
}
```
