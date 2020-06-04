import sys
import json
import requests


def send_extra(js, content, proxy=None):
    with open(js, "r") as f:
        extra = json.load(f)
    # send to TG channel
    bot_token = extra["tg_bot_token"]
    chat_id = extra["tg_chat_id"]
    proxies=dict(
        http='socks5h://127.0.0.1:' + str(proxy),
        https='socks5h://127.0.0.1:' + str(proxy)
    ) if proxy else None
    r = requests.get("https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (bot_token, chat_id, content), proxies=proxies).json()

    content += '\n详情: https://tuixue.online/visa/'
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


if __name__ == '__main__':
    send_extra(sys.argv[-3], sys.argv[-2], sys.argv[-1])
