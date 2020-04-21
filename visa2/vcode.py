import json
import time
import hashlib
import requests
import numpy as np


class Captcha:
    def __init__(self, secret, proxy=1080):
        f = np.array(open(secret).read().split())
        self.pd_id, self.pd_key = f[::2], f[1::2]
        self.host = "http://pred.fateadm.com"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.sess = requests.session()
        self.proxy = proxy

    def sign(self, pd_id, passwd, timestamp):
        md5 = hashlib.md5()
        md5.update((timestamp + passwd).encode())
        csign = md5.hexdigest()

        md5 = hashlib.md5()
        md5.update((pd_id + timestamp + csign).encode())
        csign = md5.hexdigest()
        return csign

    def solve(self, img_data, pred_type='20500'):
        next_id = [i for i in self.pd_id]
        next_key = [i for i in self.pd_key]
        index = np.random.permutation(len(self.pd_id))
        for id, key in zip(self.pd_id[index], self.pd_key[index]):
            tm = str(int(time.time()))
            data = {
                "user_id": id,
                "timestamp": tm,
                "sign": self.sign(id, key, tm),
                "predict_type": pred_type,
                "up_type": "mt"
            }

            url = self.host + "/api/capreg"
            f = {'img_data': ('img_data', img_data)}
            proxy = {
                "http": "socks5://127.0.0.1:%d" % self.proxy
            } if self.proxy else None
            r = requests.post(
                url,
                data=data,
                files=f,
                headers=self.headers,
                proxies=proxy
            )

            res = r.json()
            print(res)

            if res["RetCode"] != "0":
                if res["RetCode"] == "4003":
                    print(id, "账户余额不足")
                    next_id.remove(id)
                    next_key.remove(key)
                else:
                    print("Error: 验证码识别异常", res["RetCode"])
            else:
                self.pd_id, self.pd_key = np.array(next_id), np.array(next_key)
                return json.loads(res["RspData"])["result"]
        self.pd_id, self.pd_key = np.array(next_id), np.array(next_key)
        return ''

    def query(self):
        for id, key in zip(self.pd_id, self.pd_key):
            tm = str(int(time.time()))
            data = {
                "user_id": id,
                "timestamp": tm,
                "sign": self.sign(id, key, tm),
            }
            url = self.host + '/api/custval'
            res = requests.post(url, data=data, headers=self.headers).json()
            if res["RetCode"] != "0":
                print("Error: 查询账户余额异常", res["RetCode"])
            else:
                print(id, json.loads(res['RspData'])['cust_val'])


if __name__ == '__main__':
    v = Captcha('/root/secret', 1080)
    v.query()
    img_data = open("try/9c603bba-8334-11ea-afd7-00163e08c5e0.gif", "rb").read()
    print(v.solve(img_data))
