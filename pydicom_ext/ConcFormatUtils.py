# -*- coding: utf-8:-*-
"""
    ConcFormatUtils

    Copyright (c) 2017 Tetsuya Shinaji

    This software is released under the MIT License.

    http://opensource.org/licenses/mit-license.php

"""
from collections import OrderedDict
import re


class AttrDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ConcFormatHeaderManager:

    def __init__(self, header_fname):
        """
        load header data
        :param header_fname: header filename
        """
        self.header_fname = header_fname
        self.basic_info, self.frame_info = self.__load()

    def __load(self):
        """
        load header
        :return: basic_info and frame_info
        """
        with open(self.header_fname) as f:
            lines = f.read().splitlines()
        raw_data = []
        data = []
        for line in lines:
            if line[0] == '#':
                data.append(("comment", line.replace('\t', ' ')))
                continue
            if line == 'end_of_header':
                data.append(("comment", line.replace('\t', ' ')))
                raw_data.append(data)
                data = []
            else:
                line.replace('\t', ' ')
                data.append(line.split(' '))

        basic_info = AttrDict()
        for idx, data in enumerate(raw_data[0]):
            n = len(data)
            if n == 2:
                try:
                    if type(data) is tuple:
                        basic_info[f'comment_{idx}'] = data[1]
                    elif data[1].find('.') >= 1:
                        basic_info[data[0]] = float(data[1])
                    else:
                        basic_info[data[0]] = int(data[1])
                except:
                    basic_info[data[0]] = data[1]
            else:
                try:
                    tmp = []
                    for i in range(1, n):
                        if data[i].find('.') >= 1:
                            tmp.append(float(data[i]))
                        else:
                            tmp.append(int(data[i]))
                    basic_info[data[0]] = tmp
                except:
                    basic_info[data[0]] = ' '.join(data[1:n])
        frame_info = []
        for idx in range(1, len(raw_data)):
            tmp_info = AttrDict()
            for text_idx, data in enumerate(raw_data[idx]):
                n = len(data)
                if n == 2:
                    if type(data) is tuple:
                        tmp_info[f'comment_{text_idx}'] = data[1]
                    elif data[1].find('.') >= 1:
                        tmp_info[data[0]] = float(data[1])
                    else:
                        tmp_info[data[0]] = int(data[1])
                else:
                    tmp = []
                    for i in range(1, n):
                        if len(data[i]) == 0:
                            continue
                        elif data[i].find('.') >= 1:
                            tmp.append(float(data[i]))
                        else:
                            tmp.append(int(data[i]))
                    if data[0] == 'singles':
                        tmp_info[data[0] + '_' + str(tmp[0])] = tmp[1::]
                    else:
                        tmp_info[data[0]] = tmp
            frame_info.append(tmp_info)
        return basic_info, frame_info

    def save_hdr(self, filename):
        new_hdr = ""
        for key in self.basic_info.keys():
            if len(re.findall("(comment_)", key)) > 0:
                new_hdr += f"{self.basic_info[key]}\n"
            else:
                new_hdr += f"{key} {self.basic_info[key]}\n".replace("[", ' ').replace("]", ' ').replace(",", '')
        for i in range(len(self.frame_info)):
            for key in self.frame_info[i].keys():
                if len(re.findall("(comment_)", key)) > 0:
                    new_hdr += f"{self.frame_info[i][key]}\n"
                elif len(re.findall("(singles_)", key)) > 0:
                    new_hdr += f"{key}{self.frame_info[i][key]}\n".replace("_", " ").replace("[", ' ').replace("]", ' ').replace(",", '')
                else:
                    new_hdr += f"{key} {self.frame_info[i][key]}\n".replace("[", ' ').replace("]", ' ').replace(",", '')
        new_hdr = new_hdr
        with open(filename, "wb") as f:
            f.write(new_hdr.replace(('\r'), '').encode('utf-8'))


if __name__ == '__main__':
    pass
