import os
import time
import json
import argparse
import requests

from visa import min_date


detail = {'F': 'F1/J1', 'H': 'H1B', 'B': 'B1/B2'}
translate = {'北京': 'Beijing', '上海': 'Shanghai', '成都': 'Chengdu',
             '广州': 'Guangzhou', '沈阳': 'Shenyang', '香港': 'HongKong'}


def send(api, title, content, receivers,
         sendfrom='dean@tuixue.online', sendto='pending@tuixue.online'):
    # print(content)
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
    content = '''This is to confirm that your email %s has already in
    <a href="mailto:pending@tuixue.online">pending@tuixue.online</a>
    email list.<br> If you want to cancel the subscription, please visit
    <a href="https://tuixue.online/visa/#email">here</a> and submit an
    empty choice.
    ''' % args.email
    receivers = [args.email]
    send(args.api, 'Confirm', content, receivers)


def test(args):
    content = '''This email is to test whether you can receive email from
    <a href="https://tuixue.online/visa">tuixue.online</a>.<br>
    Your email <a href="mailto:%s">%s</a> is going to subscribing
    <a href="mailto:pending@tuixue.online">pending@tuixue.online</a>.<br>
    Your email address hasn\'t been validated by our system, please click
    <a href="https://tuixue.online/asiv?liame=%s&s=%s">this link</a> for
    the final confirmation.
    ''' % (args.email, args.email, args.email, args.subscribe)
    receivers = [args.email]
    open('../asiv/email/tmp/' + args.email, 'w').write('')
    send(args.api, 'Waiting List', content, receivers)


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
        users = os.listdir('../asiv/email/' + args.type.lower())
        a, b, c = now_time.split('/')
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
    content = ''
    for k in js:
        if '2-' not in k and now_time in k:
            last = last_js.get(k, '/')
            if js[k] != last and min_date(js[k], last) == js[k]:
                content += translate[k.split('-')[0]] + \
                    ' changes from ' + last + ' to ' + js[k] + '.<br>'
    if len(content) > 0:
        content = js['time'] + '<br>' + content
        users = os.listdir('../asiv/email/' + args.type.lower())
        send(
            args.api,
            detail[args.type] + ' Visa Status Changed',
            content,
            users
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
    if args.type == 'confirm':
        confirm(args)
    elif args.type == 'test':
        test(args)
    else:
        main(args)

