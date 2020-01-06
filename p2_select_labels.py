#!/usr/bin/env python3
# p2_select_labels.py
import os
import shutil
import p1_select_contract as p1
import u_menus as p

p0_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located


def p2_select_labels_context_func():
    p1.display_dirs(p1.p1_contract_dir)
    print('~~~ Now processing contract #: ', p1.p1_contract_nr if p1.p1_contract_nr else None)
    print('>>> Select action: ')


context_func_d = {
    'p2_select_labels': p2_select_labels_context_func,
}


def init():
    p.menu = 'p2_select_labels'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': create_default_labels,
            '2': load_n_display,
            '3': add_new_labels,
            '4': delete_existing_labels,
            'm': p.back_to_main,
            'q': p.normal_exit,
        },
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}

    # make sure p1 has been run
    p1.p1_load_p1_labels_info_d()


label_groups_l = [
    '1.Outer_box_外箱',
    '2.Inner_box_内盒',
    '3.Inside_box_中箱',
    '4.Prod_packaging_产品包装',
    '5.Plastic_bag_塑料袋',
    '6.Prod_sticker_产品上不干胶',
]

standard_labels_l = [
    '1.Outer_box_外箱',
    '6.Prod_sticker_产品上不干胶',
]


def create_default_labels():
    pass


def load_n_display():
    pass  # to do make a display_sub_processes_output for p2
    """
    print('~~~')
    p1.display_dirs(p1.p1_contract_dir)
    print('~~~')
        """


def add_new_labels():
    # read existing labels
    drs = p1.read_dirs(p1.p1_contract_dir)
    # make a candidate set of labels to be added
    candidates_l = []
    if drs:
        for lg in label_groups_l:
            if lg not in drs:
                candidates_l.append(lg)
    else:
        candidates_l = list(label_groups_l)

    print('>>> Select a label to add:')
    for i in range(len(candidates_l)):
        print(str(i) + '. ' + candidates_l[i])
    while True:
        s = input('Enter nr of directory to be created, \'b\' to return : ')
        if s == 'b':
            os.system('clear')
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(candidates_l)):
                    os.makedirs(candidates_l[s_i])
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


def delete_existing_labels():
    pass


def create_label(dr):
    # if directories do not exist, process_default_contract them
    p2_lbl_dir = os.path.join(p1.p1_contract_dir, dr)
    if not os.path.exists(p2_lbl_dir):
        os.mkdir(p2_lbl_dir, mode = 0o700)
    # and transfer the label_templates there
    if not os.path.exists(os.path.join(p2_lbl_dir, 'label_template_header.svg')):
        shutil.copy(os.path.join(p0_root_dir + '/common/1.Outer_box_外箱',
                                 'label_template_header.svg'), p2_lbl_dir)
    if not os.path.exists(os.path.join(p2_lbl_dir, 'label_template_body.svg')):
        shutil.copy(os.path.join(p0_root_dir + '/common/1.Outer_box_外箱',
                                 'label_template_body.svg'), p2_lbl_dir)


def create_label_dirs(drs_l):
    # if directories do not exist, process_default_contract them
    for dr in drs_l:
        p6_lbl_dir = os.path.join(p1.p1_contract_dir, dr)
        if not os.path.exists(p6_lbl_dir):
            os.mkdir(p6_lbl_dir, mode = 0o700)
        # and transfer the label_templates there
        if not os.path.exists(os.path.join(p6_lbl_dir, 'label_template_header.svg')):
            shutil.copy(os.path.join(p0_root_dir + '/common/1.Outer_box_外箱',
                                     'label_template_header.svg'), p6_lbl_dir)
        if not os.path.exists(os.path.join(p6_lbl_dir, 'label_template_body.svg')):
            shutil.copy(os.path.join(p0_root_dir + '/common/1.Outer_box_外箱',
                                     'label_template_body.svg'), p6_lbl_dir)

        # process_default_contract canonical p3_lbl_dir and p3_lbl_sel
        # write_in_mem_n_on_disk(dr)


"""
def write_in_mem_n_on_disk(p6_lbl_dir):
    # document the info in A1234-567_labels-info.json file
    p1.p1_labels_info_d['p3_lbl_dir'] = p6_lbl_dir
    _, p6_lbl_sel = os.path.split(p6_lbl_dir)
    p1.p1_labels_info_d['p3_lbl_sel'] = p6_lbl_sel
    with open(p1.p1_labels_info_f, 'w') as fi:
        json.dump(p1.p1_labels_info_d, fi, ensure_ascii = False)
"""


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
