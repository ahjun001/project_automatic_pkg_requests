#!/usr/bin/env python3
# u_global_values.py
import json
import os
import pprint
import shutil

# import py_menus as p
# import u_menus as m

p1_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located
# directory containing information on last run and progress in building the label set
p1_program_info_d = {}
p1_program_info_f = None
p1_initial_xls_contract_file = None
p1_full_path_source_file_xls = None  # full path of source xls file
p1_contract_nr = None  # prefix of the contract xls source file
p1_contract_dir = None  # directory where a copy of the xls contract file and contract extracted data is
# local path to labels-info.json file
p2_labels_info_d = {}
p2_labels_info_f = None


def p1_read():
    global p1_program_info_f
    global p1_program_info_d
    global p1_contract_nr
    global p1_full_path_source_file_xls
    global p1_contract_dir

    if p1_program_info_d:
        if p1_program_info_d['p1_contract_nr']:
            if p1_program_info_d['p1_full_path_source_file_xls']:
                return True
    else:
        p1_program_info_f = os.path.join(p1_root_dir, 'program-info.json')
        if os.path.isfile(p1_program_info_f):
            with open(p1_program_info_f) as f:
                p1_program_info_d = json.load(f)
                if p1_program_info_d:
                    p1_contract_nr = p1_program_info_d['p1_contract_nr']
                    p1_full_path_source_file_xls = p1_program_info_d['p1_full_path_source_file_xls']
                    p1_contract_dir = p1_root_dir + f'/data/{p1_contract_nr}'
                    if not os.path.exists(p1_contract_dir) or not os.path.exists(p1_full_path_source_file_xls):
                        pass
                        # with p1.Controller(p1.View()):
                        #    pass
                    return True
        else:
            print(f'File {p1_program_info_f} not found or missing content')  # code later will p1.Controller(p.View())
        return False


def display_p1_program_info_d():
    global p1_program_info_d
    print('~~~ Reading program-info global value ~~~')
    pprint.pprint(p1_program_info_d)
    print('~~~ Finished reading program-info global value ~~~')


def display_p1_program_info_f():
    global p1_program_info_f
    print('~~~ Reading program-info.json file contents ~~~')
    with open(p1_program_info_f) as f:
        pprint.pprint(f.read())
    print('~~~ File program-info.json closed ~~~')


def chdir_n_p2_read():
    global p1_contract_nr
    global p1_contract_dir
    global p2_labels_info_f
    global p2_labels_info_d
    global p5_all_products_to_be_processed_set
    global p6_lbl_dir
    global p6_lbl_sel

    if not p1_read():
        # with p1.Controller(p1.View()):
        pass
    os.chdir(p1_contract_dir)

    if p2_labels_info_d:
        return True
    else:
        p2_labels_info_f = os.path.join(p1_contract_dir, 'p2_' + p1_contract_nr + '_labels-info.json')
        if os.path.isfile(p2_labels_info_f):
            with open(p2_labels_info_f) as f:
                p2_labels_info_d = json.load(f)
                if p2_labels_info_d:
                    if 'p2_contract_json' in p2_labels_info_d.keys():
                        return True
        else:
            print(f'File {p2_labels_info_f} not found or missing content')
        return False


def chdir_n_p4_read():
    global p1_contract_nr
    global p1_contract_dir
    global p2_labels_info_d
    global p2_labels_info_f
    global p5_all_products_to_be_processed_set

    chdir_n_p2_read()

    p2_labels_info_f = os.path.join(p1_contract_dir, 'p2_' + p1_contract_nr + '_labels-info.json')
    if os.path.isfile(p2_labels_info_f):
        with open(p2_labels_info_f) as f:
            p2_labels_info_d = json.load(f)
            if p2_labels_info_d:
                if 'p5_all_products_to_be_processed_set' in p2_labels_info_d.keys() \
                    and p2_labels_info_d['p5_all_products_to_be_processed_set'] \
                    and 'p6_extract_specifics' in p2_labels_info_d.keys() \
                        and p2_labels_info_d['p6_extract_specifics']:
                    p5_all_products_to_be_processed_set = p2_labels_info_d['p5_all_products_to_be_processed_set']
                return True
    else:
        print(f'File {p2_labels_info_f} not found or missing content')
    return False


def display_p2_labels_info_d():
    global p2_labels_info_d
    print('~~~ Reading labels-info global value ~~~')
    pprint.pprint(p2_labels_info_d)
    print('~~~ Finished reading labels-info global value ~~~')


def display_p2_labels_info_f():
    global p2_labels_info_f
    if p2_labels_info_f:
        if os.path.isfile(p2_labels_info_f):
            print('~~~ Reading labels-info.json file contents ~~~')
            with open(p2_labels_info_f) as f:
                # print(f.read())
                pprint.pprint(f.read())
            print('~~~ File labels-info.json closed ~~~')
    else:
        print(f'\nFile {p2_labels_info_f} not built yet\n')


p5_all_products_to_be_processed_set = None

p6_lbl_dir = None  # currently working label directory
p6_lbl_sel = None  # current label
lbl_lst = None  # list of labels  # Todo: not used at this point

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

    chdir_n_p4_read()
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


def select_dir_to_be_deleted(walk_dir):
    # function factory
    # defining what each label function should be doing
    def make_f(to_del_dir):
        def func():
            global p1_root_dir
            global p1_contract_dir

            full_to_del_dir = walk_dir + to_del_dir
            shutil.rmtree(full_to_del_dir)
            if full_to_del_dir == p1_contract_dir:
                os.remove(os.path.join(p1_root_dir, 'program-info.json'))

        func.__name__ = to_del_dir
        return func

    dr_l = read_dirs(walk_dir)
    functions_d = {}
    for idx in range(len(dr_l)):
        functions_d[idx] = make_f(dr_l[idx])

    """
    def back():
        m.menu = m.previous_menu
        m.menus = m.previous_menus

    assert back == back

    m.menu = 'Select dir to delete: '
    m.menus = {m.menu: {}}
    dr_l = read_dirs(walk_dir)
    for idx in range(len(dr_l)):
        m.menus[m.menu][str(idx)] = functions_d[idx]
    m.menus[m.menu]['m'] = eval('back')
    # a particular case of run to present the current situation in p6: listing existing / non existing directories
    m.run(display_dirs(walk_dir))
    return
        """


def display_dirs(walk_dir = None):
    global p1_contract_dir

    if not walk_dir:
        walk_dir = p1_contract_dir
    if p1_contract_dir:
        drs = read_dirs(walk_dir)
        print('~~~')
        for dr in drs:
            print(dr)
        print('~~~')

        current_dir_fp = os.getcwd()
        current_dir_lcl = current_dir_fp[current_dir_fp.rfind('/'):]
        print(f'Currently in {current_dir_lcl}')


def read_dirs(walk_dir):
    global p1_contract_dir

    (root, dirs, files) = next(os.walk(walk_dir))
    dirs.sort()
    return dirs


standard_labels_l = [
    '1.Outer_box_外箱',
    '6.Prod_sticker_产品上不干胶',
]

header_height = 7
page_view_box_w = 170
page_view_box_h = 257
