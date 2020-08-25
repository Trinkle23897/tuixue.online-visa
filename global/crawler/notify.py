import os
import time
import json
import random
import base64
import argparse
import requests
import itertools
import subprocess
from datetime import datetime


detail = {'F': 'F1/J1', 'H': 'H1B', 'B': 'B1/B2', 'O': 'O1/O2/O3', 'L': 'L1/L2'}
translate = {'金边': 'Phnom Penh', '新加坡': 'Singapore', '首尔': 'Seoul', '墨尔本': 'Melbourne', '珀斯': 'Perth', '悉尼': 'Sydney', '伯尔尼': 'Bern',
             'Belfast': 'Belfast', 'London': 'London', 'Calgary': 'Calgary', 'Halifax': 'Halifax', 'Montreal': 'Montreal', 'Ottawa': 'Ottawa', 'Quebec City': 'Quebec City', 'Toronto': 'Toronto', 'Vancouver': 'Vancouver', 'Abu Dhabi': 'Abu Dhabi', 'Dubai': 'Dubai',
             'Ciudad Juarez': 'Ciudad Juarez', 'Guadalajara': 'Guadalajara', 'Hermosillo': 'Hermosillo', 'Matamoros': 'Matamoros', 'Merida': 'Merida', 'Mexico City': 'Mexico City', 'Monterrey': 'Monterrey', 'Nogales': 'Nogales', 'Nuevo Laredo': 'Nuevo Laredo', 'Tijuana': 'Tijuana'}
translate2chn = {'金边': '金边', '新加坡': '新加坡', '首尔': '首尔', '墨尔本': '墨尔本', '珀斯': '珀斯', '悉尼': '悉尼', '伯尔尼': '伯尔尼',
                 'Phnom Penh': '金边', 'Singapore': '新加坡', 'Seoul': '首尔', 'Melbourne': '墨尔本', 'Perth': '珀斯', 'Sydney': '悉尼', 'Bern': '伯尔尼',
                 'Belfast': '贝尔法斯特', 'London': '伦敦', 'Calgary': '卡尔加里', 'Halifax': '哈利法克斯', 'Montreal': '蒙特利尔', 'Ottawa': '渥太华', 'Quebec City': '魁北克城', 'Toronto': '多伦多', 'Vancouver': '温哥华', 'Abu Dhabi': '阿布扎比', 'Dubai': '迪拜',
                 'Ciudad Juarez': '华雷斯城', 'Guadalajara': '瓜达拉哈拉', 'Hermosillo': '埃莫西约', 'Matamoros': '马塔莫罗斯', 'Merida': '梅里达', 'Mexico City': '墨西哥城', 'Monterrey': '蒙特雷', 'Nogales': '诺加莱斯', 'Nuevo Laredo': '新拉雷多', 'Tijuana': '蒂华纳'}
short = {'金边': 'pp', '新加坡': 'sg', '首尔': 'sel', '墨尔本': 'mel', '珀斯': 'per', '悉尼': 'syd', '伯尔尼': 'brn',
         '贝尔法斯特': 'bfs', '伦敦': 'lcy', '卡尔加里': 'yyc', '哈利法克斯': 'yhz', '蒙特利尔': 'yul', '渥太华': 'yow', '魁北克城': 'yqb', '多伦多': 'yyz', '温哥华': 'yvr', '阿布扎比': 'auh', '迪拜': 'dxb',
         'Belfast': 'bfs', 'London': 'lcy', 'Calgary': 'yyc', 'Halifax': 'yhz', 'Montreal': 'yul', 'Ottawa': 'yow', 'Quebec City': 'yqb', 'Toronto': 'yyz', 'Vancouver': 'yvr', 'Abu Dhabi': 'auh', 'Dubai': 'dxb',
         '华雷斯城': 'cjs', '瓜达拉哈拉': 'gdl', '埃莫西约': 'hmo', '马塔莫罗斯': 'cvj', '梅里达': 'mid', '墨西哥城': 'mex', '蒙特雷': 'mty', '诺加莱斯': 'ols', '新拉雷多': 'nld', '蒂华纳': 'tij',
         'Ciudad Juarez': 'cjs', 'Guadalajara': 'gdl', 'Hermosillo': 'hmo', 'Matamoros': 'cvj', 'Merida': 'mid', 'Mexico City': 'mex', 'Monterrey': 'mty', 'Nogales': 'ols', 'Nuevo Laredo': 'nld', 'Tijuana': 'tij'}


def min_date(a, b):
    if a == '/':
        return b
    if b == '/':
        return a
    i0, i1, i2 = a.split('/')
    i0, i1, i2 = int(i0), int(i1), int(i2)
    j0, j1, j2 = b.split('/')
    j0, j1, j2 = int(j0), int(j1), int(j2)
    if i0 > j0 or i0 == j0 and (i1 > j1 or i1 == j1 and i2 >= j2):
        return b
    else:
        return a


def send(api, title, content, receivers,
         sendfrom='dean@tuixue.online', sendto='pending@tuixue.online'):
    data = {
        'content': content,
        'receivers': '@@@'.join(receivers),
        'title': title,
        'sendfrom': sendfrom,
        'sendto': sendto
    }
    r = requests.post(api, data=data).content.decode()
    print(r)


def send_extra_on_change(visa_type, title, content):
    if visa_type != "F" or not args.extra or len(content) == 0:
        return
    with open(args.extra, "r") as f:
        extra = json.load(f)
    bot_token = extra["tg_bot_token"]
    chat_id = extra["tg_chat_id"]
    proxies = dict(
        http='socks5h://127.0.0.1:' + args.proxy,
        https='socks5h://127.0.0.1:' + args.proxy
    ) if args.proxy else None

    year, month, day, msg_id = 0, 0, 0, 0
    if os.path.exists("msg_id.txt"):
        with open("msg_id.txt", "r") as f:
            year, month, day, msg_id = list(map(int, f.read().split()))
    now = datetime.now()
    cyear, cmonth, cday = now.year, now.month, now.day
    text = "%d/%d/%d 实时数据\n" % (cyear, cmonth, cday) + \
        "\n".join(content) + '\nhttps://tuixue.online/global/'
    if not (cyear == year and cmonth == month and cday == day):
        r = requests.get("https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" %
                         (bot_token, chat_id, text), proxies=proxies).json()
        msg_id = r["result"]["message_id"]
        with open("msg_id.txt", "w") as f:
            f.write("%d %d %d %d" % (cyear, cmonth, cday, msg_id))
        requests.get("https://api.telegram.org/bot%s/pinChatMessage?chat_id=%s&message_id=%s" %
                     (bot_token, chat_id, str(msg_id)), proxies=proxies)
    else:
        r = requests.get("https://api.telegram.org/bot%s/editMessageText?chat_id=%s&message_id=%s&text=%s" %
                         (bot_token, chat_id, str(msg_id), text), proxies=proxies)


def send_extra(visa_type, title, content):
    if visa_type != "F" or not args.extra or len(content) == 0:
        return
    content = "\n".join(content.values()).replace("<br>", "").replace(
        ' to ', ' -> ').replace(' changed from ', ': ').replace('.', '').replace(time.asctime()[-4:] + '/', '')
    for en, zh in translate2chn.items():
        content = content.replace(en, zh)
    subprocess.Popen(['python3', 'send_extra.py',
                      args.extra, content, args.proxy])
    return
    with open(args.extra, "r") as f:
        extra = json.load(f)
    # send to TG channel
    bot_token = extra["tg_bot_token"]
    chat_id = extra["tg_chat_id"]
    proxies = dict(
        http='socks5h://127.0.0.1:' + args.proxy,
        https='socks5h://127.0.0.1:' + args.proxy
    ) if args.proxy else None
    r = requests.get("https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" %
                     (bot_token, chat_id, content), proxies=proxies).json()

    content += '\n详情: https://tuixue.online/global/'
    # send to QQ group
    auth_key = extra["mirai_auth_key"]
    qq_num = extra["qq_num"]
    group_id = extra["qq_group_id"]
    base_uri = extra["mirai_base_uri"]
    r = requests.post(base_uri + "/auth",
                      data=json.dumps({"authKey": auth_key})).json()
    session = r["session"]
    requests.post(base_uri + "/verify",
                  data=json.dumps({"sessionKey": session, "qq": qq_num}))
    for g in group_id:
        requests.post(base_uri + "/sendGroupMessage", data=json.dumps(
            {"sessionKey": session, "target": g, "messageChain": [{"type": "Plain", "text": content}]}))
    requests.post(base_uri + "/release",
                  data=json.dumps({"sessionKey": session, "qq": qq_num}))


def confirm(args):
    content = '''Dear %s:<br>
    <br>
    Welcome to tuixue.online! We are excited that you have
    chosen to join the Subscribtion Program. There are three action items to
    complete:<br><br>
    1. <b>Whitelist *@tuixue.online</b>: your email provider may still
    randomly block the notification from tuixue.online.<br>
    2. <b>Share tuixue.online to your friends</b>: many people need this website,
    and if you share our Subscribtion Program to them, they would be very
    grateful.<br>
    3. <b>Donate the tuition fee</b> (not mandatory): this
    <a href="https://tuixue.online/global/#code">link</a> provides some helpful
    information.<br>
    <br>
    Again, congratulations on your admission!<br>
    <br>
    Best Regards<br>
    Dean of tuixue.online<br>''' % (args.email.split('@')[0])
    receivers = [args.email]
    send(args.api, 'Welcome to tuixue.online', content, receivers)


def test(args):
    args.subscribe = [''] + args.subscribe
    args.subscribe = '&visa[]='.join(args.subscribe)
    content = '''
    Dear %s:<br>
    <br>
        A faculty committee at tuixue.online has made a decision on your
        application. <br>
        Please review your decision by logging back into tuixue.online 
        application status page at
        <a href="https://tuixue.online/asiv?liame=%s%s">this link</a>.<br>
    <br>
    Sincerely,<br>
    <br>
    tuixue.online Graduate Division<br>
    Diversity, Inclusion and Admissions<br>
    <br>
    Please note: This e-mail message was sent from a notification-only<br>
    address that cannot accept incoming e-mail. Please do not reply to<br>
    this message. Please save or print your decision letter and any<br>
    related online documents immediately for your records.<br>
    ''' % (args.email.split('@')[0], args.email, args.subscribe)
    receivers = [args.email]
    open('../asiv/email/tmp/' + args.email, 'w').write(args.time)
    send(args.api, 'Your Application Decision from tuixue.online',
         content, receivers)


template = '''
<div role="tabpanel" class="tab-pane fade IS_F" id="TYPE" aria-labelledby="TYPE-tab">
<center><br>“最早”指在该地预约日期24h变化中最早的一天<br>
上一次更新时间：TIME</center><br><script type="text/javascript">
function chartTYPE() {
    var c = echarts.init(document.getElementById("chart"));
    var o = {
        title: {text: "TYPE_TEXT"},
        tooltip: {
            trigger: "axis",
            formatter: function(data) {
                var result = data[0].name + "<br/>";
                for (var i = 0, length = data.length; i < length; ++i)
                    result += data[i].marker + data[i].seriesName + ": " + data[i].data + "<br>";
                return result;
            }
        },
        legend: {data: [LEGEND]},
        xAxis: {type: "category", boundaryGap: false, data: [XAXIS]},
        yAxis: {type: "time"},
    dataZoom: [{
        type: "slider",
        height: 8,
        bottom: 20,
        borderColor: "transparent",
        backgroundColor: "#e2e2e2",
        handleIcon: "M10.7,11.9H9.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4h1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7v-1.2h6.6z M13.3,22H6.7v-1.2h6.6z M13.3,19.6H6.7v-1.2h6.6z", // jshint ignore:line
        handleSize: 20,
        handleStyle: {
            shadowBlur: 6,
            shadowOffsetX: 1,
            shadowOffsetY: 2,
            shadowColor: "#aaa"
        }
    }, {
        type: "inside"
    }],
        series: [SERIES]
    };
    c.setOption(o);
}
</script>
<div class="table-responsive">
<table class="table table-hover table-striped table-bordered">
<!-- 如果要爬取这个table，有更方便的方式（可一秒一次）：F签Json(https://tuixue.online/global/visa-f.json)，B签Json(https://tuixue.online/global/visa-b.json)，H签Json(https://tuixue.online/global/visa-h.json)，O签Json(https://tuixue.online/global/visa-o.json) ，L签Json(https://tuixue.online/global/visa-l.json)-->
TABLE
</table>
</div>
</div>
'''


def refresh_homepage():
    html = open('../template.php').read()
    cur = time.strftime('%Y/%m/%d', time.localtime())
    yy, mm, dd = cur.split('/')
    alltype = {'F': '', 'B': '', 'H': '', 'O': '', 'L': '',
               'Fais': '', 'Bais': '', 'Hais': '', 'Oais': '', 'Lais': '',
               'Fmx': '', 'Bmx': '', 'Hmx': '', 'Omx': '', 'Lmx': ''}
    for tp in alltype:
        try:
            js = json.loads(open('../visa-%s.json' % tp[0].lower()).read())
        except:
            print('err on homepage:', tp[0])
            return
        tptext = 'F/J' if tp[0] == 'F' else tp[0]
        result = template.replace('TYPE_TEXT', tptext).replace(
            "TYPE", tp).replace('TIME', js['time'])
        result = result.replace('IS_F', 'active in' if tp == 'F' else '')
        info = {}
        x = []
        if 'ais' in tp:
            legend = ["Belfast", "London", "Calgary", "Halifax", "Montreal",
                      "Ottawa", "Quebec City", "Toronto", "Vancouver", "Abu Dhabi", "Dubai"]
        elif 'mx' in tp:
            legend = ["Ciudad Juarez", "Guadalajara", "Hermosillo", "Matamoros", "Merida", "Mexico City", "Monterrey", "Nogales", "Nuevo Laredo", "Tijuana"]
        else:
            legend = ["金边", "新加坡", "首尔", "墨尔本", "珀斯", "悉尼", "伯尔尼"]
        for city in legend:
            p = '%s/%s/%s' % (tp[0], city, cur)
            if os.path.exists(p):
                info[city] = {}
                raw = open(p).read().split('\n')[:-1]
                for i in raw:
                    k, v = i.split()
                    x.append(k)
                    info[city][k] = min_date(v, info[city].get(k, '/'))
            else:
                info[city] = {}
        x = sorted(list(set(x)))
        # chart
        if 'ais' in tp:
            legend = ["Belfast", "London", "Calgary", "Halifax", "Montreal",
                      "Ottawa", "Quebec City", "Toronto", "Vancouver", "Abu Dhabi", "Dubai"]
        elif 'mx' in tp:
            legend = ["Ciudad Juarez", "Guadalajara", "Hermosillo", "Matamoros", "Merida", "Mexico City", "Monterrey", "Nogales", "Nuevo Laredo", "Tijuana"]
        else:
            legend = ["金边", "新加坡", "首尔", "墨尔本", "珀斯", "悉尼", "伯尔尼"]
        legend = '"' + '","'.join([translate2chn[i] for i in legend]) + '"'
        result = result.replace('LEGEND', legend)
        xaxis = ""
        for i in x:
            xaxis += '"' + i + '",'
        result = result.replace('XAXIS', xaxis)
        series = ''
        if 'ais' in tp:
            legend = ["Belfast", "London", "Calgary", "Halifax", "Montreal",
                      "Ottawa", "Quebec City", "Toronto", "Vancouver", "Abu Dhabi", "Dubai"]
        elif 'mx' in tp:
            legend = ["Ciudad Juarez", "Guadalajara", "Hermosillo", "Matamoros", "Merida", "Mexico City", "Monterrey", "Nogales", "Nuevo Laredo", "Tijuana"]
        else:
            legend = ["金边", "新加坡", "首尔", "墨尔本", "珀斯", "悉尼", "伯尔尼"]
        for city in legend:
            series += '{name: "%s", type: "line", data: [' % translate2chn[city]
            for t in x:
                if info.get(city, None) is not None \
                        and info[city].get(t, None) is not None:
                    series += '"' + info[city][t] + '",'
                else:
                    series += 'null,'
            series += ']},\n'
        result = result.replace('SERIES', series)
        # table
        if 'ais' in tp:
            legend = ["Belfast", "London", "Calgary", "Halifax", "Montreal",
                      "Ottawa", "Quebec City", "Toronto", "Vancouver", "Abu Dhabi", "Dubai"]
        elif 'mx' in tp:
            legend = ["Ciudad Juarez", "Guadalajara", "Hermosillo", "Matamoros", "Merida", "Mexico City", "Monterrey", "Nogales", "Nuevo Laredo", "Tijuana"]
        else:
            legend = ["金边", "新加坡", "首尔", "墨尔本", "珀斯", "悉尼", "伯尔尼"]
        table = '<thead><tr><th>地点</th>'
        for i in legend:
            table += '<th colspan="2"><a href="/global/crawler/' + \
                tp[0] + '/' + i + '/' + cur + '">' + translate2chn[i] + '</a></th>'
        table += '</tr><tr><th>时间</th>'
        for i in legend:
            table += '<th>当前</th><th>最早</th>'
        table += '</tr></thead><tbody>'
        for index in js['index']:
            yy, mm, dd = index.split('/')
            line = '<tr><td><a href="crawler/view/' + ('ais.php' if 'ais' in tp else '') + \
                '?y=%s&m=%s&d=%s&t=%s">%s/%s</a></td>' % (
                    yy, mm, dd, tp, mm, dd)
            flag = False
            for c in legend:
                r = js.get(c + '-' + index, '')
                if len(r) > 1:
                    r = r[5:]
                    flag = True
                line += '<td>' + r + '</td>'
                r = js.get(c + '2-' + index, '')
                if len(r) > 1:
                    r = r[5:]
                    flag = True
                line += '<td>' + r + '</td>'
            if flag:
                table += line + '</tr>'
        table += '</tbody>'
        result = result.replace('TABLE', table)
        alltype[tp] = result
    summary = ''
    keys = list(alltype.keys())
    random.shuffle(keys)
    for i in keys:
        summary += alltype[i]
    if random.random() < 0.1:
        captcha_list = ['/visa2/log/' +
                        i for i in os.listdir('../../visa2/log')]
    else:
        captcha_list = ['/visa2/fail/' +
                        i for i in os.listdir('../../visa2/fail')]
    captcha = random.sample(captcha_list, 1)[0]
    captcha = '<input type="text" name="orig" style="display: none" value="%s"><img src="%s">' % (
        base64.b64encode(captcha.encode()).decode(), captcha)
    open('../index.php', 'w').write(html.replace('TBD_PANE',
                                                 summary).replace('TBD_CAPTCHA', captcha))


def main(args):
    if len(args.js) > 0:
        last_js, js = json.loads(args.last_js), json.loads(args.js)
    else:
        last_js = json.loads(open(
            '../visa-%s-last.json' % args.type.lower()).read())
        try:
            js = json.loads(open(
                '../visa-%s.json' % args.type.lower()).read())
        except:
            js = last_js
    refresh_homepage()
    now_time, last_time = js['time'].split()[0], last_js['time'].split()[0]
    if now_time != last_time:
        return
        # users = [
        #     j for i in full
        #     for j in os.listdir('../asiv/email/' + args.type.lower() + '/' + i)]
        # users = list(set(users))
        # a, b, c = last_time.split('/')
        # url = 'https://tuixue.online/visa2/view/?y=%s&m=%s&d=%s&t=%s' % (
        #     a, b, c, args.type)
        # send(
        #     args.api,
        #     'Daily Stats for ' + detail[args.type] + ' Visa',
        #     '%s<br>This is yesterday\'s visa status: <a href="%s">%s</a>' % (
        #         last_time, url, url),
        #     users,
        # )
    # change english to chinese
    content = sorted([translate2chn[k.split('-')[0]] + ': ' + js[k]
                      for k in js if now_time in k and '2-' not in k])
    content_last = sorted([translate2chn[k.split('-')[0]] + ': ' + last_js[k]
                           for k in last_js if last_time in k and '2-' not in k])
    if content != content_last:
        try:
            send_extra_on_change(args.type, 'Summary of ' +
                                 detail[args.type] + ' Visa, ' + now_time, content)
        except Exception as e:
            print(e)
    content = {}
    upd_time = {}
    for k in js:
        if '2-' not in k and now_time in k:
            last = last_js.get(k, '/')
            if js[k] != last and min_date(js[k], last) == js[k]:
                content[short[k.split('-')[0]]] = \
                    translate[k.split('-')[0]] + \
                    ' changed from ' + last + ' to ' + js[k] + '.<br>'
                upd_time[short[k.split('-')[0]]] = js[k]
    title = detail[args.type] + ' Visa Status Changed'
    try:
        send_extra(args.type, title, content)
    except Exception as e:
        print(e)
    if len(list(content.keys())) > 0:
        keys = sorted(list(content.keys()))
        masks = list(itertools.product([0, 1], repeat=len(keys)))[1:]
        users = {}
        alluser = []
        for k in keys:
            users[k] = os.listdir(
                '../../asiv/email/' + args.type.lower() + '/' + k)
            alluser += users[k]
        alluser = list(set(alluser))
        mask_stat = {}
        for u in alluser:
            tu = open('../../asiv/email/tmp/' + u).read()
            if '/' not in tu:
                tu = '/'
            mask_stat[u] = [
                u in users[k] and min_date(tu, upd_time[k]) == upd_time[k]
                for k in keys]
        for mask in masks:
            mask = list(mask)
            pending = [u for u in alluser if mask_stat[u] == mask]
            if len(pending) == 0:
                continue
            c = ''.join([content[k] for i, k in enumerate(keys) if mask[i]])
            c = js['time'] + '<br>' + c + '''<br>See
                <a href="https://tuixue.online/global/#%s">
                https://tuixue.online/global/#%s</a> for more detail.
                ''' % (args.type, args.type)
            c += '''<br>If you want to change your subscribe option, please re-submit
                a request over <a href="https://tuixue.online/global/#email">
                https://tuixue.online/global/#email</a>.'''
            send(
                args.api,
                detail[args.type] + ' Visa Status Changed',
                c,
                pending,
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str, choices=[
        'F', 'B', 'H', 'O', 'L', 'test', 'confirm'])
    parser.add_argument('--email', type=str, default='')
    parser.add_argument('--subscribe', type=str, default='')
    parser.add_argument('--secret', type=str, default='/var/www/mail')
    parser.add_argument('--time', type=str, default='')
    parser.add_argument('--proxy', type=str, default="1083")
    parser.add_argument('--extra', type=str, default="/root/extra-global.json")
    parser.add_argument('--js', type=str, default='')
    parser.add_argument('--last_js', type=str, default='')
    args = parser.parse_args()
    args.api = open(args.secret).read()
    args.subscribe = args.subscribe.split(',')
    if args.type == 'confirm':
        confirm(args)
    elif args.type == 'test':
        test(args)
    else:
        main(args)
