#!/usr/bin/env python3
import os
import shutil

if not os.path.exists('regular_expressions_local.json'):
    shutil.copy('regular_expressions_common.json', 'regular_expressions_local.json')

with open('regular_expressions_local.json', 'r+', encoding='utf8') as fw:
    contents = fw.readlines()
    my_str = contents[len(contents) -2]
    contents[len(contents) - 2] = my_str[:-1] + ',\n'
    contents.insert(len(contents)-1, '  { "what": "color_zh", "how": "\\\\w(?=\\\\颜色)" }\n')
    fw.seek(0)
    fw.writelines(contents)
