import io
import sys
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image

config = {
    "a": {
        "width": 21,
        "w_hist": [11, 15, 18, 20, 21, 21, 20, 21, 19, 17, 16, 16, 16, 22, 25, 26, 26, 26, 25, 23, 11],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 16, 17, 19, 20, 17, 16, 14, 11, 7, 8, 12, 16, 18, 19, 20, 17, 15, 15, 15, 21, 21, 21, 20, 18, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "b": {
        "width": 24,
        "w_hist": [4, 32, 37, 39, 40, 40, 39, 39, 22, 16, 13, 12, 13, 13, 14, 14, 16, 25, 26, 25, 22, 20, 15, 10],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 7, 8, 9, 10, 9, 9, 8, 8, 7, 7, 6, 12, 18, 19, 19, 20, 18, 14, 13, 14, 14, 13, 13, 13, 14, 14, 14, 14, 14, 14, 16, 19, 19, 22, 21, 21, 20, 18, 7, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "c": {
        "width": 22,
        "w_hist": [6, 14, 17, 19, 21, 23, 23, 21, 15, 11, 10, 10, 9, 8, 9, 14, 15, 16, 16, 13, 15, 16],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 11, 16, 18, 19, 16, 14, 15, 14, 14, 10, 8, 7, 8, 7, 8, 9, 9, 9, 10, 10, 11, 14, 16, 16, 13, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "d": {
        "width": 24,
        "w_hist": [4, 11, 15, 18, 20, 22, 23, 22, 16, 14, 11, 11, 9, 10, 13, 14, 22, 30, 36, 39, 39, 41, 40, 28],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 5, 8, 9, 10, 10, 10, 9, 7, 6, 6, 7, 7, 13, 15, 16, 18, 18, 14, 15, 13, 14, 13, 15, 16, 14, 14, 14, 14, 13, 12, 14, 13, 14, 15, 20, 20, 19, 18, 16, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "f": {
        "width": 15,
        "w_hist": [5, 10, 9, 30, 33, 34, 34, 35, 31, 27, 17, 15, 15, 14, 11],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 7, 9, 10, 11, 11, 5, 5, 5, 5, 6, 9, 14, 15, 14, 13, 12, 9, 7, 7, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 11, 15, 15, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "h": {
        "width": 23,
        "w_hist": [5, 17, 32, 37, 37, 38, 39, 38, 29, 9, 8, 4, 4, 6, 6, 8, 11, 19, 24, 24, 23, 19, 20],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 8, 9, 9, 9, 9, 8, 8, 6, 6, 7, 6, 5, 11, 14, 18, 21, 21, 19, 16, 15, 13, 13, 13, 13, 12, 12, 11, 11, 11, 11, 11, 12, 11, 14, 17, 20, 17, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "i": {
        "width": 11,
        "w_hist": [4, 10, 28, 31, 33, 35, 34, 34, 33, 23, 21],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 7, 9, 9, 9, 9, 7, 5, 1, 0, 0, 0, 0, 4, 7, 9, 11, 11, 11, 10, 9, 8, 6, 7, 7, 7, 7, 8, 9, 9, 9, 9, 9, 10, 10, 9, 10, 11, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "j": {
        "width": 15,
        "w_hist": [5, 7, 7, 8, 10, 12, 13, 36, 37, 39, 36, 34, 33, 32, 25],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 7, 8, 8, 8, 8, 7, 5, 0, 0, 0, 0, 0, 4, 7, 10, 11, 12, 11, 10, 8, 8, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 6, 5, 9, 11, 10, 10, 9, 8, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "k": {
        "width": 24,
        "w_hist": [9, 19, 29, 38, 38, 38, 39, 38, 24, 15, 10, 11, 10, 12, 18, 23, 22, 20, 19, 17, 16, 15, 14, 14],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 6, 8, 9, 9, 8, 7, 8, 8, 8, 7, 7, 7, 7, 16, 16, 17, 18, 16, 13, 12, 11, 13, 14, 15, 16, 17, 18, 20, 19, 18, 17, 17, 16, 18, 20, 21, 20, 8, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "l": {
        "width": 12,
        "w_hist": [4, 8, 9, 15, 37, 38, 39, 39, 40, 40, 38, 13],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 7, 9, 10, 11, 11, 10, 9, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 9, 9, 9, 9, 11, 12, 12, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "m": {
        "width": 38,
        "w_hist": [6, 14, 21, 24, 25, 26, 26, 26, 25, 20, 12, 11, 9, 8, 8, 10, 20, 24, 24, 25, 24, 23, 20, 12, 9, 9, 6, 6, 6, 7, 14, 27, 26, 25, 26, 26, 22, 16],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 22, 33, 36, 38, 38, 35, 31, 26, 24, 21, 22, 22, 22, 20, 21, 21, 21, 19, 20, 21, 24, 26, 33, 32, 29, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "n": {
        "width": 25,
        "w_hist": [5, 15, 23, 24, 25, 26, 26, 26, 24, 12, 10, 6, 6, 6, 8, 10, 11, 17, 26, 26, 26, 26, 27, 26, 16],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 14, 18, 20, 23, 24, 24, 22, 16, 13, 14, 15, 14, 13, 13, 14, 13, 15, 15, 16, 16, 16, 17, 21, 23, 23, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "o": {
        "width": 25,
        "w_hist": [6, 11, 15, 18, 20, 22, 23, 24, 16, 10, 9, 9, 9, 8, 9, 10, 11, 14, 24, 25, 23, 21, 19, 17, 13],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 7, 12, 14, 16, 13, 12, 12, 14, 13, 15, 15, 14, 15, 15, 15, 15, 15, 15, 15, 15, 16, 19, 20, 18, 16, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "p": {
        "width": 21,
        "w_hist": [18, 33, 33, 34, 34, 34, 34, 28, 14, 13, 11, 10, 8, 10, 10, 14, 26, 24, 22, 20, 17],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 12, 15, 18, 18, 15, 13, 13, 13, 14, 13, 13, 14, 13, 13, 13, 12, 12, 11, 11, 12, 12, 15, 19, 18, 17, 16, 11, 7, 7, 7, 10, 11, 11, 10, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "q": {
        "width": 24,
        "w_hist": [8, 14, 18, 20, 21, 22, 23, 16, 13, 11, 10, 8, 6, 11, 13, 15, 33, 34, 34, 34, 34, 35, 33, 24],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 17, 18, 20, 17, 15, 15, 15, 15, 13, 13, 14, 13, 13, 14, 14, 15, 15, 16, 17, 19, 19, 21, 21, 18, 14, 7, 7, 7, 7, 8, 8, 10, 11, 12, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "r": {
        "width": 19,
        "w_hist": [7, 20, 24, 24, 25, 25, 25, 24, 10, 9, 9, 8, 7, 7, 8, 8, 8, 8, 7],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 12, 16, 18, 19, 19, 19, 16, 7, 7, 7, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 10, 12, 12, 11, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "s": {
        "width": 17,
        "w_hist": [22, 22, 24, 22, 22, 19, 19, 20, 22, 23, 25, 26, 28, 26, 23, 17, 12],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 12, 11, 14, 16, 13, 11, 10, 9, 9, 12, 15, 16, 17, 17, 16, 14, 13, 11, 9, 10, 10, 16, 15, 15, 17, 17, 16, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "t": {
        "width": 16,
        "w_hist": [5, 5, 6, 13, 29, 31, 33, 34, 34, 34, 24, 12, 11, 12, 12, 12],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 5, 7, 7, 7, 7, 7, 8, 10, 14, 16, 16, 16, 9, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 11, 12, 12, 11, 10, 8, 7, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "u": {
        "width": 24,
        "w_hist": [8, 18, 22, 25, 26, 27, 27, 27, 11, 6, 4, 8, 10, 10, 11, 12, 23, 24, 27, 29, 29, 29, 28, 12],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 9, 13, 16, 21, 20, 20, 19, 18, 15, 14, 15, 14, 14, 14, 14, 14, 14, 14, 16, 16, 18, 21, 22, 22, 21, 17, 15, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "v": {
        "width": 25,
        "w_hist": [5, 6, 7, 9, 12, 13, 15, 22, 21, 21, 21, 17, 17, 16, 16, 17, 19, 19, 20, 19, 17, 12, 9, 6, 5],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 13, 16, 22, 20, 19, 14, 13, 13, 15, 13, 12, 13, 13, 13, 13, 12, 14, 13, 13, 12, 12, 10, 9, 8, 7, 7, 7, 5, 5, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "w": {
        "width": 33,
        "w_hist": [8, 10, 11, 16, 22, 26, 25, 21, 18, 17, 13, 13, 15, 16, 17, 17, 16, 17, 23, 24, 24, 21, 17, 13, 12, 15, 13, 14, 17, 15, 11, 10, 5],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 28, 29, 26, 25, 21, 20, 21, 21, 19, 19, 19, 18, 22, 23, 25, 24, 22, 19, 19, 19, 18, 16, 13, 13, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "x": {
        "width": 24,
        "w_hist": [10, 10, 12, 12, 13, 15, 20, 23, 24, 23, 21, 15, 9, 10, 16, 21, 20, 19, 19, 16, 14, 13, 13, 12],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 13, 22, 22, 19, 18, 16, 16, 13, 14, 10, 12, 11, 10, 9, 9, 11, 11, 13, 15, 18, 21, 21, 21, 18, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    },
    "y": {
        "width": 24,
        "w_hist": [11, 14, 17, 19, 21, 24, 24, 27, 28, 31, 27, 21, 17, 15, 22, 23, 20, 18, 15, 13, 9, 8, 7, 6],
        "h_hist": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 7, 11, 15, 20, 19, 20, 20, 19, 16, 14, 16, 14, 15, 14, 14, 15, 13, 12, 11, 10, 9, 8, 8, 7, 7, 6, 5, 6, 11, 12, 13, 12, 11, 10, 9, 5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 
    }
}

class Net(nn.Module):
    def __init__(self, in_channel=1, height=70, width=38, out_dim=23):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(in_channel, 8, 3, 1)
        self.conv2 = nn.Conv2d(8, 16, 3, 1)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(16 * (height // 2 - 2) * (width // 2 - 2), 128)
        self.fc2 = nn.Linear(128, out_dim)

    def forward(self, x):
        # Input x: [batch, channel, height, width]

        # out: [batch, 8, height - 2, width - 2]
        out = self.conv1(x)
        out = F.relu(out)

        # out: [batch, 16, height - 4, width - 4]
        out = self.conv2(out)
        out = F.relu(out)

        # out: [batch, 16, height / 2 - 2, width / 2 - 2]
        out = F.max_pool2d(out, 2)
        out = self.dropout1(out)

        # out: [batch, 16 * (height / 2 - 2) * (width / 2 - 2)]
        out = torch.flatten(out, 1)

        # out: [batch, 128]
        out = self.fc1(out)
        out = F.relu(out)
        out = self.dropout2(out)

        # out: [batch, out_dim]
        out = self.fc2(out)
        out = F.log_softmax(out, dim=1)
        return out

model = Net()
model.load_state_dict(torch.load("save.pth"))
model.eval()

all_letters = "abcdfhijklmnopqrstuvwxy"
white_pixel = 1
black_pixel = 0


def binarization():
    pixels[pixels != blank_pixel] = black_pixel
    pixels[pixels == blank_pixel] = white_pixel


def delete_curve():
    candidates = [[] for _ in range(width)]
    for j in range(width):
        cnt = 0
        for i in range(height):
            if pixels[i][j] == black_pixel:
                cnt += 1
            else:
                if cnt == 2 or cnt == 3:
                    candidates[j].append((i - cnt, i))
                cnt = 0

    for j in range(width):
        for up, down in candidates[j]:
            r = [(up, down)]
            k = j + 1
            while k < width:
                cur_up, cur_down = r[-1]
                if cur_down - cur_up == 2:
                    possible = [(cur_up, cur_down), (cur_up - 1, cur_down), (cur_up, cur_down + 1)]
                elif cur_down - cur_up == 3:
                    if len(r) <= 1:
                        possible = [(cur_up - 1, cur_down - 1), (cur_up + 1, cur_down + 1), (cur_up, cur_down - 1), (cur_up + 1, cur_down)]
                    else:
                        possible = [(cur_up - 1, cur_down - 1), (cur_up + 1, cur_down + 1)]
                        last_up, last_down = r[-2]
                        if last_down < cur_down:
                            possible.append((cur_up + 1, cur_down))
                        elif last_up > cur_up:
                            possible.append((cur_up, cur_down - 1))
                is_found = False
                for item in possible:
                    if item in candidates[k]:
                        is_found = True
                        r.append(item)
                        candidates[k].remove(item)
                        k += 1
                        break
                if not is_found or k == width - 1:
                    if len(r) > 5:
                        for p in range(j, j + len(r)):
                            cur_up, cur_down = r[p - j]
                            pixels[cur_up: cur_down, p] = white_pixel
                    break


def eliminate_noise():
    for j in range(0, 50):
        if (pixels[:, j] != white_pixel).sum() <= 3:
            pixels[:, j] = white_pixel
    for j in range(150, 200):
        if (pixels[:, j] != white_pixel).sum() <= 3:
            pixels[:, j] = white_pixel    


def bold():
    global filled
    filled = pixels.copy()
    for i in range(height):
        for j in range(width):
            if pixels[i][j] != white_pixel:
                if i - 1 >= 0:
                    filled[i - 1][j] = pixels[i][j]
                if i + 1 < height:
                    filled[i + 1][j] = pixels[i][j]
                if j - 1 >= 0:
                    filled[i][j - 1] = pixels[i][j]
                if j + 1 < width:
                    filled[i][j + 1] = pixels[i][j]


def position_adjust():
    letter_base = []
    for j in range(width):
        top, bottom = 0, 0
        for i in range(height):
            if filled[i][j] == black_pixel:
                bottom = i
                if top == 0:
                    top = i
        if bottom - top >= 24 and bottom - top <= 26:
            letter_base.append(bottom)
        else:
            letter_base.append(0)

    l, r = 0, 0
    while l < width:
        while r < width and letter_base[r] == 0:
            r += 1
        if l == 0:
            for p in range(l, r):
                letter_base[p] = letter_base[r]
        elif r >= width:
            for p in range(l, r):
                letter_base[p] = letter_base[l]
        elif r - l > 1:
            k = (letter_base[r] - letter_base[l]) / (r - l)
            if k <= 0.5:
                for p in range(l, r):
                    letter_base[p] = int(letter_base[l] + k * (p - l))
            else:
                for p in range(l, r + 1):
                    letter_base[p] = letter_base[l]
        l, r = r, r + 1

    for j in range(width):
        delta = letter_base[j] - 50
        if delta > 0:
            filled[:-delta, j] = filled[delta:, j]
            filled[-delta:, j] = white_pixel
        elif delta < 0:
            filled[-delta:, j] = filled[:delta, j]
            filled[:-delta, j] = white_pixel


def cosine_similarity(v1, v2, move=0):
    v1_abs = np.sqrt(np.sum(v1 * v1))
    v2_abs = np.sqrt(np.sum(v2 * v2))
    m = 0
    for d in range(-move, move + 1):
        v1_v2 = np.sum(v1 * np.roll(v2, d))
        if v1_v2 > m:
            m = v1_v2
    if m == 0:
        return 0
    return m / (v1_abs * v2_abs)


def inspect(img_data):
    global width, height, pixels, blank_pixel
    stream = io.BytesIO(img_data)
    im = Image.open(stream)
    width, height = im.size
    pixels = np.array(im)
    blank_pixel = pixels[0][0]
    binarization()
    delete_curve()
    eliminate_noise()
    bold()
    position_adjust()
    left = 0
    while np.sum(filled[:, left] == black_pixel) == 0:
        left += 1
    return check(left)


def check(left):
    result = ""
    for _ in range(5):
        matrix = filled[:, left: left + 38]
        input_m = np.ones((1, 1, 70, 38))
        input_m[0, 0, :, :matrix.shape[1]] = matrix
        input_tensor = torch.from_numpy(input_m).float()
        output_m = model(input_tensor).detach().numpy()
        letter_idx = np.argmax(output_m[0])
        letter = all_letters[letter_idx]
        result += letter

        ref, adjust_l = 0., left
        for w_l in range(left - 1, left + 4):
            width = config[letter]["width"]
            matrix = filled[:, w_l: w_l + width]
            w_hist = np.sum(matrix == black_pixel, axis=0)
            h_hist = np.sum(matrix == black_pixel, axis=1)
            w_conf = cosine_similarity(w_hist, np.array(config[letter]["w_hist"]))
            h_conf = cosine_similarity(h_hist, np.array(config[letter]["h_hist"]), move=2)
            confidence = (w_conf + h_conf) / 2
            if confidence > ref:
                ref = confidence
                adjust_l = w_l

        left = adjust_l + config[letter]["width"]
    print(result)
    return result


class Captcha:
    def __init__(self):
        pass

    def solve(self, img_data):
        return inspect(img_data)

    def wrong(self):
        print("Wrong!")


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as f:
        img_data = f.read()
    print(inspect(img_data))
