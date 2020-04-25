import os
import time
import json
import argparse
import requests
import itertools


detail = {'F': 'F1/J1', 'H': 'H1B', 'B': 'B1/B2', 'O': 'O1/O2/O3'}
translate = {'北京': 'Beijing', '上海': 'Shanghai', '成都': 'Chengdu',
             '广州': 'Guangzhou', '沈阳': 'Shenyang', '香港': 'HongKong'}
full = {'bj': '北京', 'sh': '上海', 'cd': '成都', 'gz': '广州', 'sy': '沈阳', 'hk': '香港'}
short = {'北京': 'bj', '上海': 'sh', '成都': 'cd',
         '广州': 'gz', '沈阳': 'sy', '香港': 'hk'}


def min_date(a, b):
    if a == '/':
        return b
    if b == '/':
        return a
    i0, i1, i2 = a.split('/')
    i0, i1, i2 = int(i0), int(i1), int(i2)
    j0, j1, j2 = b.split('/')
    j0, j1, j2 = int(j0), int(j1), int(j2)
    if i0 > j0 or i0 == j0 and (i1 > j1 or i1 == j1 and i2 > j2):
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
    r = requests.post(api, data=data)
    print(r.content.decode())


def confirm(args):
    content = '''Dear %s:<br>
    <br>
    Welcome to tuixue.online! We are excited that you have
    chosen to join the Subscribtion Program. There are three action items to
    complete:<br><br>
    1. Whitelist *@tuixue.online, because your email provider may still
    randomly block the notification from tuixue.online.<br>
    2. Donate the tuition fee (not mandatory): this
    <a href="https://tuixue.online/visa/#code">link</a> provides some helpful
    information.<br>
    3. Share tuixue.online to your friends: many people need this website,
    and if you share our Subscribtion Program to them, they would be very
    grateful.<br>
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
        application. <br>Please review your decision by logging back into
        tuixue.online application status page at
        <a href="https://tuixue.online/asiv?liame=%s%s">this link</a>.<br>
    <br>
    Sincerely,<br>
    <br>
    tuixue.online Graduate Division<br>
    Diversity, Inclusion and Admissions<br>
    <br>
    Please note: This e-mail message was sent from a notification-only
    address that cannot accept incoming e-mail. Please do not reply to
    this message. Please save or print your decision letter and any
    related online documents immediately for your records.<br>
    ''' % (args.email.split('@')[0], args.email, args.subscribe)
    receivers = [args.email]
    open('../asiv/email/tmp/' + args.email, 'w').write(args.time)
    send(args.api, 'Your Application Decision from tuixue.online',
         content, receivers)


template = '''
<center><br>“最早”指在该地预约日期24h变化中最早的一天<br>
上一次更新时间：TIME</center><br><script type="text/javascript">
function chartTYPE() {
    var c = echarts.init(document.getElementById("chart"));
    var o = {
        title: {text: "TYPE"},
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
        series: [SERIES]
    };
    c.setOption(o);
}
</script>
<div class="table-responsive">
<table class="table table-hover table-striped table-bordered">
TABLE
</table>
</div>
'''


def refresh_homepage():
    html = open('../visa/template.php').read()
    cur = time.strftime('%Y/%m/%d', time.localtime())
    yy, mm, dd = cur.split('/')
    for tp in "FBHO":
        p = '' if tp == 'F' else ('-' + tp.lower())
        js = json.loads(open('../visa/visa%s.json' % p).read())
        result = template.replace("TYPE", tp).replace('TIME', js['time'])
        info = {}
        x = []
        for city in translate:
            p = '%s/%s/%s' % (tp, city, cur)
            if os.path.exists(p):
                info[city] = {}
                raw = open(p).read().split('\n')[:-1]
                for i in raw:
                    k, v = i.split()
                    x.append(k)
                    info[city][k] = v
            else:
                info[city] = {}
        x = sorted(list(set(x)))
        # chart
        if tp == 'H':
            legend = '"北京","广州","上海","香港"'
        else:
            legend = '"北京","成都","广州","上海","沈阳","香港"'
        result = result.replace('LEGEND', legend)
        xaxis = ""
        for i in x:
            xaxis += '"' + i + '",'
        result = result.replace('XAXIS', xaxis)
        series = ''
        legend = ["北京", "成都", "广州", "上海", "沈阳", "香港"]
        for city in legend:
            series += '{name: "%s", type: "line", data: [' % city
            for t in x:
                if info.get(city, None) is not None \
                        and info[city].get(t, None) is not None:
                    series += '"' + info[city][t] + '",'
                else:
                    series += 'null,'
            series += ']},\n'
        result = result.replace('SERIES', series)
        # table
        if tp == 'H':
            legend = ["北京", "广州", "上海", "香港"]
        else:
            legend = ["北京", "成都", "广州", "上海", "沈阳", "香港"]
        table = '<thead><tr><th>地点</th>'
        for i in legend:
            table += '<th colspan="2">' + i + '</th>'
        table += '</tr><tr><th>时间</th>'
        for i in legend:
            table += '<th>当前</th><th>最早</th>'
        table += '</tr></thead><tbody>'
        for index in js['index']:
            yy, mm, dd = index.split('/')
            line = '<tr><td><a href="/visa2/view/' + \
                '?y=%s&m=%s&d=%s&t=%s">%s/%s</a></td>' % (
                    yy, mm, dd, tp, mm, dd)
            for c in legend:
                r = js.get(c + '-' + index, '')
                if len(r) > 1:
                    r = r[5:]
                line += '<td>' + r + '</td>'
                r = js.get(c + '2-' + index, '')
                if len(r) > 1:
                    r = r[5:]
                line += '<td>' + r + '</td>'
            table += line + '</tr>'
        table += '</tbody>'
        result = result.replace('TABLE', table)
        source_place = 'TBD_' + tp
        html = html.replace(source_place, result)
    open('../visa/index.php', 'w').write(html)


def main(args):
    refresh_homepage()
    if args.type == 'F':
        js = json.loads(open('../visa/visa.json').read())
        last_js = json.loads(open('../visa/visa-last.json').read())
    else:
        js = json.loads(open(
            '../visa/visa-%s.json' % args.type.lower()).read())
        last_js = json.loads(open(
            '../visa/visa-%s-last.json' % args.type.lower()).read())
    now_time, last_time = js['time'].split()[0], last_js['time'].split()[0]
    if now_time != last_time:
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
        return
    content = {}
    upd_time = {}
    for k in js:
        if '2-' not in k and now_time in k:
            last = last_js.get(k, '/')
            if js[k] != last and min_date(js[k], last) == js[k]:
                content[short[k.split('-')[0]]] = \
                    translate[k.split('-')[0]] + \
                    ' changes from ' + last + ' to ' + js[k] + '.<br>'
                upd_time[short[k.split('-')[0]]] = js[k]
    if len(list(content.keys())) > 0:
        keys = sorted(list(content.keys()))
        masks = list(itertools.product([0, 1], repeat=len(keys)))[1:]
        users = {}
        alluser = []
        for k in keys:
            users[k] = os.listdir(
                '../asiv/email/' + args.type.lower() + '/' + k)
            alluser += users[k]
        alluser = list(set(alluser))
        mask_stat = {}
        for u in alluser:
            tu = open('../asiv/email/tmp/' + u).read()
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
                <a href="https://tuixue.online/visa/#%s">
                https://tuixue.online/visa/#%s</a> for more detail.
                ''' % (args.type, args.type)
            c += '''<br><br>If you want to change your subscribe option, please re-submit
                a request over <a href="https://tuixue.online/visa/#email">
                https://tuixue.online/visa/#email</a>.'''
            send(
                args.api,
                detail[args.type] + ' Visa Status Changed',
                c,
                pending,
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str, choices=[
        'F', 'B', 'H', 'O', 'test', 'confirm'])
    parser.add_argument('--email', type=str, default='')
    parser.add_argument('--subscribe', type=str, default='')
    parser.add_argument('--secret', type=str, default='/var/www/mail')
    parser.add_argument('--time', type=str, default='')
    args = parser.parse_args()
    args.api = open(args.secret).read()
    args.subscribe = args.subscribe.split(',')
    if args.type == 'confirm':
        confirm(args)
    elif args.type == 'test':
        test(args)
    else:
        main(args)
