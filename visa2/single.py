import json, requests

def send(extra, content, proxy):
    with open(extra, "r") as f:
        extra = json.load(f)

    # send to TG channel
    bot_token = extra["tg_bot_token"]
    chat_id = extra["tg_chat_id"]
    proxies=dict(
        http='socks5h://127.0.0.1:' + proxy,
        https='socks5h://127.0.0.1:' + proxy
    )
    r = requests.get("https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (bot_token, chat_id, content), proxies=proxies).json()

    # send to QQ group
    auth_key = extra["mirai_auth_key"]
    qq_num = extra["qq_num"]
    group_id = extra["qq_group_id"]
    base_uri = extra["mirai_base_uri"]
    r = requests.post(base_uri + "/auth", data=json.dumps({"authKey": auth_key})).json()
    session = r["session"]
    requests.post(base_uri + "/verify", data=json.dumps({"sessionKey": session, "qq": qq_num}))
    for g in group_id:
        requests.post(base_uri + "/sendGroupMessage", data=json.dumps({"sessionKey": session, "target": g, "messageChain": [{"type": "Plain", "text": content}]}))
    requests.post(base_uri + "/release", data=json.dumps({"sessionKey": session, "qq": qq_num}))

content = '沈阳7月8月所有周三的面谈被取消 15:43'

send('/root/extra.json', content, '1083')
