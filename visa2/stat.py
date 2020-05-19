#!/usr/bin/env python3
import os

print('Captcha :', len(os.listdir('log')))
print('Email   :', len(os.listdir('../asiv/email/tmp')))
s = [] 
for i in 'bfohl': 
    for j in ['bj', 'gz', 'sh', 'sy', 'hk', 'cd']: 
        s += os.listdir('../asiv/email/%s/%s' % (i, j)) 
print('Valid   :', len(set(s)))
