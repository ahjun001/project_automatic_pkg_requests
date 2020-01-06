#!/usr/bin/env python3
# p2_select_labels.py
import os
import shutil
import p1_select_contract as p1
import u_menus as p

p0_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located


def p2_select_labels_context_func(prompt = True):
    print('~~~ Now processing contract #: ', p1.p1_contract_nr if p1.p1_contract_nr else None)
    print('\n~~~ Labels already added:')

    p1.display_dirs(p1.p1_contract_dir)
    if prompt:
        print('\n>>> Select action: ')


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
    add_labels_from_list(standard_labels_l, ask_questions = False)


def load_n_display():
    p1.read_dirs(p1.p1_contract_dir)
    p1.display_dirs(p1.p1_contract_dir)


def add_new_labels():
    add_labels_from_list(label_groups_l, ask_questions = True)


def add_labels_from_list(list_l, ask_questions):
    # read existing labels
    drs = p1.read_dirs(p1.p1_contract_dir)
    # make a candidate set of labels to be added
    candidates_l = []
    if drs:
        for lg in list_l:
            if lg not in drs:
                candidates_l.append(lg)
    else:
        candidates_l = list(list_l)

    if ask_questions:
        p2_select_labels_context_func(prompt = False)
        print('>>> Select # in front of the label name to be added:\n')
        for i in range(len(candidates_l)):
            print(str(i) + '. ' + candidates_l[i][2:])
        while True:
            s = input('\nEnter nr of directory to be created, \'b\' to return : ')
            if s == 'b':
                os.system('clear')
                break
            else:
                try:
                    s_i = int(s)
                    if s_i in range(len(candidates_l)):
                        create_label(candidates_l[s_i])
                    else:
                        print('Integer, but not an option, try again')
                except ValueError:
                    print('That\'s not an integer, try again')
    else:
        for c in candidates_l:
            create_label(c)


def delete_existing_labels():
    print('~~~ Deleting labels non-empty directory data')
    drs = p1.read_dirs(p1.p1_contract_dir)
    if not drs:
        return
    for i in range(len(drs)):
        print(i, drs[i][2:])
    print('~~~')
    while True:
        s = input('Enter nr of label to delete, \'b\' to return:\n')
        if s == 'b':
            os.system('clear')
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(drs)):
                    shutil.rmtree(os.path.join(p1.p1_contract_dir, drs[s_i]))
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


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


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
