import os

a = open('../asiv/email/log').read().split('\n')[:-1]
for i in a:
    t, p = i.split()
    if '..' in p or '/visa2' not in p:
        continue
    p = '..' + p
    if os.path.exists(p):
        print(t + ' https://tuixue.online' + p[2:])
        g = input('captcha: ')
        if len(g) == 5:
            t = g
        elif g == 'n':
            continue
        print('mv %s ../visa2/log/%s.gif' % (p, t))
        os.system('mv %s ../visa2/log/%s.gif' % (p, t))
open('../asiv/email/log', 'w').write('')
