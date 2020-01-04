#!/usr/bin/env python3
# u_global_values.py
import json
import os
import pprint
import shutil



p5_all_products_to_be_processed_set = None

p6_lbl_dir = None  # currently working label directory
p6_lbl_sel = None  # current label

p7_label_info_d = {}  # info on label currently being edited
p7_label_info_f = None  # info on label currently being edited


def display_p7_label_info_d():
    global p7_label_info_d
    print('~~~ Reading label-info global value ~~~')
    pprint.pprint(p7_label_info_d)
    print(p7_label_info_d)
    print('~~~ Finished reading label-info global value ~~~')


def display_p7_label_info_f():
    global p7_label_info_f

    if p7_label_info_d:
        if os.path.isfile(p7_label_info_f):
            print('~~~ Reading label-info.json file contents ~~~')
            with open(p7_label_info_f) as f:
                pprint.pprint(f.read())
            print('~~~ File label-info.json closed ~~~')
    else:
        print(f'\nFile {p7_label_info_f} not built yet\n')


def chdir_n_p7_read():
    global p6_lbl_dir
    global p6_lbl_sel
    global p7_label_info_f
    global p7_label_info_d

    p4_read()
    #    p6_lbl_dir = p2_labels_info_d['p6_lbl_dir']
    #    p6_lbl_sel = p2_labels_info_d['p6_lbl_sel']
    os.chdir(p6_lbl_dir)

    p7_label_info_f = os.path.join(p6_lbl_dir, 'label-info.json')
    if os.path.isfile(p7_label_info_f):
        with open(p7_label_info_f) as f:
            p7_label_info_d = json.load(f)
            if p7_label_info_d:
                return True
    return False




header_height = 7
page_view_box_w = 170
page_view_box_h = 257
