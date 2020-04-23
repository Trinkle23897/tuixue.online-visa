import os
import json
import argparse
import requests
import itertools


detail = {'F': 'F1/J1', 'H': 'H1B', 'B': 'B1/B2'}
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
    chosen to join the Subscribtion Program. There are two action items to
    complete:<br><br>
    1. Whitelist *@tuixue.online, because your email provider may still
    randomly block the notification from tuixue.online.<br>
    2. Donate the tuition fee (not necessary): this
    <a href="https://tuixue.online/visa/#code">link</a> provides some helpful
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
    open('../asiv/email/tmp/' + args.email, 'w').write('')
    send(args.api, 'Your Application Decision from tuixue.online',
         content, receivers)


def main(args):
    if args.type == 'F':
        js = json.loads(open('../visa/visa.json').read())
        last_js = json.loads(open('../visa/visa-last.json').read())
    elif args.type == 'B':
        js = json.loads(open('../visa/visa-b.json').read())
        last_js = json.loads(open('../visa/visa-b-last.json').read())
    elif args.type == 'H':
        js = json.loads(open('../visa/visa-h.json').read())
        last_js = json.loads(open('../visa/visa-h-last.json').read())
    now_time, last_time = js['time'].split()[0], last_js['time'].split()[0]
    if now_time != last_time:
        users = [os.listdir('../asiv/email/' + args.type.lower() + '/' + i)
                 for i in full]
        users = list(set(users))
        a, b, c = last_time.split('/')
        url = 'https://tuixue.online/visa2/view/?y=%s&m=%s&d=%s&t=%s' % (
            a, b, c, args.type)
        send(
            args.api,
            'Daily Stats for ' + detail[args.type] + ' Visa, ' + last_time,
            'This is yesterday\'s visa status: <a href="%s">%s</a>' % (
                url, url),
            users,
        )
        return
    content = {}
    for k in js:
        if '2-' not in k and now_time in k:
            last = last_js.get(k, '/')
            if js[k] != last and min_date(js[k], last) == js[k]:
                content[short[k.split('-')[0]]] = \
                    translate[k.split('-')[0]] + \
                    ' changes from ' + last + ' to ' + js[k] + '.<br>'
    if len(list(content.keys())) > 0:
        keys = sorted(list(content.keys()))
        masks = list(itertools.product([0, 1], repeat=len(keys)))
        users = {}
        alluser = []
        for k in keys:
            users[k] = os.listdir(
                '../asiv/email/' + args.type.lower() + '/' + k)
            alluser += users[k]
        alluser = list(set(alluser))
        mask_stat = {}
        for u in alluser:
            mask_stat[u] = [u in users[k] for k in keys]
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
        'F', 'B', 'H', 'test', 'confirm'])
    parser.add_argument('--email', type=str, default='')
    parser.add_argument('--subscribe', type=str, default='')
    parser.add_argument('--secret', type=str, default='/var/www/mail')
    args = parser.parse_args()
    args.api = open(args.secret).read()
    args.subscribe = args.subscribe.split(',')
    if args.type == 'confirm':
        confirm(args)
    elif args.type == 'test':
        test(args)
    else:
        main(args)
