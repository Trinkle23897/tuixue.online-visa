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
raw_info = raw = [
    ('金边', 'Phnom Penh', 'pp', 'cgi'),
    ('新加坡', 'Singapore', 'sg', 'cgi'),
    ('首尔', 'Seoul', 'sel', 'cgi'),
    ('墨尔本', 'Melbourne', 'mel', 'cgi'),
    ('珀斯', 'Perth', 'per', 'cgi'),
    ('悉尼', 'Sydney', 'syd', 'cgi'),
    ('伯尔尼', 'Bern', 'brn', 'cgi'),
    ('福冈', 'Fukuoka', 'fuk', 'cgi'),
    ('大坂', 'Osaka', 'itm', 'cgi'),
    ('那霸', 'Naha', 'oka', 'cgi'),
    ('札幌', 'Sapporo', 'cts', 'cgi'),
    ('东京', 'Tokyo', 'hnd', 'cgi'),
    ('加德满都', 'Kathmandu', 'ktm', 'cgi'),
    ('曼谷', 'Bangkok', 'bkk', 'cgi'),
    ('清迈', 'Chiang Mai', 'cnx', 'cgi'),
    ('贝尔法斯特', 'Belfast', 'bfs', 'ais'),
    ('伦敦', 'London', 'lcy', 'ais'),
    ('卡尔加里', 'Calgary', 'yyc', 'ais'),
    ('哈利法克斯', 'Halifax', 'yhz', 'ais'),
    ('蒙特利尔', 'Montreal', 'yul', 'ais'),
    ('渥太华', 'Ottawa', 'yow', 'ais'),
    ('魁北克城', 'Quebec City', 'yqb', 'ais'),
    ('多伦多', 'Toronto', 'yyz', 'ais'),
    ('温哥华', 'Vancouver', 'yvr', 'ais'),
    ('阿布扎比', 'Abu Dhabi', 'auh', 'ais'),
    ('迪拜', 'Dubai', 'dxb', 'ais'),
    ('贝尔格莱德', 'Belgrade', 'beg', 'ais'),
    ('巴黎', 'Paris', 'cdg', 'ais'),
    ('瓜亚基尔', 'Guayaquil', 'gye', 'ais'),
    ('基多', 'Quito', 'uio', 'ais'),
    ('安卡拉', 'Ankara', 'esb', 'ais'),
    ('伊斯坦布尔', 'Istanbul', 'ist', 'ais'),
    ('雅典', 'Athens', 'ath', 'ais'),
    ('波哥大', 'Bogota', 'bog', 'ais'),
    ('布里奇顿', 'Bridgetown', 'bgi', 'ais'),
    ('华雷斯城', 'Ciudad Juarez', 'cjs', 'ais'),
    ('瓜达拉哈拉', 'Guadalajara', 'gdl', 'ais'),
    ('埃莫西约', 'Hermosillo', 'hmo', 'ais'),
    ('马塔莫罗斯', 'Matamoros', 'cvj', 'ais'),
    ('梅里达', 'Merida', 'mid', 'ais'),
    ('墨西哥城', 'Mexico City', 'mex', 'ais'),
    ('蒙特雷', 'Monterrey', 'mty', 'ais'),
    ('诺加莱斯', 'Nogales', 'ols', 'ais'),
    ('新拉雷多', 'Nuevo Laredo', 'nld', 'ais'),
    ('蒂华纳', 'Tijuana', 'tij', 'ais'),
]
translate = {(i[1] if i[-1] == 'ais' else i[0]): i[1] for i in raw}
translate2chn = {i[1]: i[0] for i in raw}
translate2chn.update({i[0]: i[0] for i in raw if i[-1] == 'cgi'})
short = {i[0]: i[2] for i in raw}
short.update({i[1]: i[2] for i in raw if i[-1] == 'ais'})
legend_cgi = [i[0] for i in raw if i[-1] == 'cgi']
legend_ais = [i[1] for i in raw[:-10] if i[-1] == 'ais']
legend_mx = [i[1] for i in raw[-10:]]


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
            legend = legend_ais
        elif 'mx' in tp:
            legend = legend_mx
        else:
            legend = legend_cgi
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
        legend = '"' + '","'.join([translate2chn[i] for i in legend]) + '"'
        result = result.replace('LEGEND', legend)
        xaxis = ""
        for i in x:
            xaxis += '"' + i + '",'
        result = result.replace('XAXIS', xaxis)
        series = ''
        if 'ais' in tp:
            legend = legend_ais
        elif 'mx' in tp:
            legend = legend_mx
        else:
            legend = legend_cgi
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
            line = '<tr><td><a href="crawler/view/' + ('' if len(tp) == 1 else 'ais.php') + \
                '?y=%s&m=%s&d=%s&t=%s">%s/%s</a></td>' % (
                    yy, mm, dd, tp[0], mm, dd)
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
    email_info = ''
    for i in raw_info:
        email_info += '<tr><td align="right">%s：</td><td><label class="checkbox-inline"><input type="checkbox" name="visa[]" value="f%s"> F1/J1</label><label class="checkbox-inline"><input type="checkbox" name="visa[]" value="b%s"> B1/B2</label><label class="checkbox-inline"><input type="checkbox" name="visa[]" value="h%s"> H1B</label><label class="checkbox-inline"><input type="checkbox" name="visa[]" value="o%s"> O1/O2/O3</label><label class="checkbox-inline"><input type="checkbox" name="visa[]" value="l%s"> L1/L2</label></td></tr>\n' % (i[0], i[2], i[2], i[2], i[2], i[2])
    html = html.replace('TBD_EMAIL_INFO', email_info)
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
        if '2-' not in k and now_time in k and k in last_js:
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
