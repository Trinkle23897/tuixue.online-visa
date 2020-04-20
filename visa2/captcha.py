import os
import tqdm
import torch
import argparse
import numpy as np
from torch import nn
from PIL import Image
import torch.nn.functional as F


avail_chars = np.array(' '.join('abcdfhijklmnopqrstuvwxy').split())
captcha_num = 5
captcha_size = (70, 200)
train_ratio = 0.8


class MovAvg(object):
    def __init__(self, size=10):
        self.size, self.cache = size, []

    def add(self, x):
        if x != np.inf:
            self.cache.append(x)
        if self.size > 0 and len(self.cache) > self.size:
            self.cache = self.cache[-self.size:]

    def get(self):
        return 0 if len(self.cache) == 0 else np.mean(self.cache)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, default='log')
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--epoch', type=int, default=1000)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--test_gif', type=str, default='')
    parser.add_argument(
        '--device', type=str,
        default='cuda' if torch.cuda.is_available() else 'cpu')
    args = parser.parse_known_args()[0]
    return args


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=(1, 1)),
            nn.MaxPool2d(2, 2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Conv2d(16, 64, 3, padding=(1, 1)),
            nn.MaxPool2d(2, 2),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 512, 3, padding=(1, 1)),
            nn.MaxPool2d(2, 2),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(512, 512, 3, padding=(1, 1)),
            nn.MaxPool2d(2, 2),
            nn.BatchNorm2d(512),
            nn.ReLU(),
        )
        self.fc = nn.Linear(24576, captcha_num * len(avail_chars))

    def forward(self, x):
        x = self.model(x)
        x = x.reshape([x.shape[0], -1])
        x = self.fc(x)
        return x


def str2np(s):
    assert len(s) == captcha_num
    r = np.zeros([captcha_num, len(avail_chars)])
    for i, j in enumerate(s):
        r[i][np.where(avail_chars == j)[0]] = 1
    return r.reshape(-1)


def np2str(r):
    if isinstance(r, torch.Tensor):
        r = r.detach().cpu().numpy()
    r = r.reshape([-1, captcha_num, len(avail_chars)])
    s = avail_chars[r.argmax(axis=2)]
    return np.array([''.join(i) for i in s])


def preprocess(fn):
    return 1. * (np.array(Image.open(fn)) != 15)


def data_argumentation(data, label, st):
    d, l, s = [], [], []
    for i in range(-10, 10):
        d.append(np.roll(data, i, axis=-1))
        l.append(label)
        s.append(st)
    d = np.concatenate(d)
    return d.shape[0], d, np.concatenate(l), np.concatenate(s)


def train(args):
    gifs = [i for i in os.listdir(args.dir) if '.gif' in i]
    n = len(gifs)
    data = np.zeros([n, 1, *captcha_size])
    label = np.zeros([n, captcha_num * len(avail_chars)])
    for i, f in enumerate(gifs):
        data[i] = preprocess(os.path.join(args.dir, f))
        gifs[i] = gifs[i][:captcha_num]
        label[i] = str2np(gifs[i])
        assert gifs[i] == np2str(label[i]), print(gifs[i], np2str(label[i]))
    gifs = np.array(gifs)
    train_num = int(n * train_ratio)
    test_num = n - train_num
    train_data, eval_data = data[:train_num], data[train_num:]
    train_label, eval_label = label[:train_num], label[train_num:]
    train_str, eval_str = gifs[:train_num], gifs[:train_num]
    train_num, train_data, train_label, train_str = data_argumentation(
        train_data, train_label, train_str)
    net = Net().to(args.device)
    optim = torch.optim.Adam(net.parameters(), lr=args.lr)
    train_acc = MovAvg()
    best_acc = 0
    for epoch in range(args.epoch):
        indices = np.random.permutation(np.arange(train_num))
        net.train()
        with tqdm.trange(0, train_num, args.batch_size,
                         desc='Epoch %d Train' % (epoch + 1)) as t:
            for _ in t:
                index = indices[_:_ + args.batch_size]
                data = torch.tensor(
                    train_data[index], dtype=torch.float, device=args.device)
                label = torch.tensor(
                    train_label[index], dtype=torch.float, device=args.device)
                label_str = train_str[index]
                pred = net(data)
                loss = F.binary_cross_entropy_with_logits(pred, label)
                optim.zero_grad()
                loss.backward()
                optim.step()
                pred_str = np2str(pred)
                train_acc.add((pred_str == label_str).mean())
                t.set_postfix(loss=loss.item(), acc=train_acc.get())
        acc_cnt = 0
        indices = np.arange(test_num)
        net.eval()
        with tqdm.trange(0, test_num, args.batch_size,
                         desc='Epoch %d Test' % (epoch + 1)) as t:
            for _ in t:
                index = indices[_:_ + args.batch_size]
                data = torch.tensor(
                    eval_data[index], dtype=torch.float, device=args.device)
                label = torch.tensor(
                    eval_label[index], dtype=torch.float, device=args.device)
                label_str = eval_str[index]
                pred = net(data)
                loss = F.binary_cross_entropy_with_logits(pred, label)
                pred_str = np2str(pred)
                acc_cnt += (pred_str == label_str).sum()
                t.set_postfix(acc_cnt='%d/%d' % (acc_cnt, test_num),
                              acc=acc_cnt / test_num,
                              loss=loss.item())
        if acc_cnt >= best_acc:
            best_acc = acc_cnt
            torch.save(net.state_dict(), os.path.join(args.dir, 'model.pth'))


def test(args):  # only on cpu
    net = Net()
    net.load_state_dict(torch.load(os.path.join(args.dir, 'model.pth'),
                                   map_location='cpu'))
    net.eval()
    data = preprocess(args.test_gif)
    data = torch.tensor(data.reshape([1, 1, *captcha_size]), dtype=torch.float)
    pred_str = np2str(net(data))[0]
    print(pred_str)


if __name__ == '__main__':
    args = get_args()
    if args.test_gif:
        test(args)
    else:
        train(args)
