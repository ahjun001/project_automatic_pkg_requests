#!/usr/bin/env python3
import os
import shutil

import u_menus as p

p0_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located

label_groups = ['1.Outer_box_外箱',
                '2.Inner_box_内盒',
                '3.Inside_box_中箱',
                '4.Prod_packaging_产品包装',
                '5.Plastic_bag_塑料袋',
                '6.Prod_sticker_产品上不干胶',
                ]


def edit_dirs_context():
    """
    for _, drs, _ in os.walk('.'):
        drs[:] = [d for d in drs if not d[0] == '.']
    for dr in drs:
        print(dr)
    """
    drs = u_list_dirs()
    for dr in drs:
        if dr[0] not in ['.', '_']:
            print(dr)


def u_list_dirs():
    _, drs, _ = next(os.walk('.'))
    drs.sort()
    drs[:] = [d for d in drs if d[0] not in ['.', '_']]
    return drs


context_func_d = {
    'edit_dirs_menu': edit_dirs_context,
}


def init():
    p.menu = 'edit_dirs_menu'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': auto_create,
            '1a': create_from_a_list,
            '2': display,
            '3': update,
            '4': delete,
            'b': p.back,
            'm': p.back_to_main,
            'q': p.normal_exit,
        },
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}


def process_default_contract():
    edit_dirs_context()
    print('~~~process_default_contract~~~')
    name = input('Enter new directory name: ')
    if os.path.exists(os.path.join('.', name)):
        print(f'mkdir: cannot process_default_contract directory {name}: File exists')
    else:
        os.makedirs(name)


def create_from_a_list():
    global label_groups
    print('~~~ Create from a list ~~~')
    drs = u_list_dirs()
    not_yet_l = []
    for d in label_groups:
        if d not in drs:
            not_yet_l.append(d)
    for i in range(len(not_yet_l)):
        print(str(i) + ' ' + not_yet_l[i][2:])
    print('~~~')
    while True:
        s = input('Enter nr of directory to be created, \'b\' to return : ')
        if s == 'b':
            os.system('clear')
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(not_yet_l)):
                    os.makedirs(not_yet_l[s_i])
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


def display():
    print('~~~display_sub_processes_output~~~')
    edit_dirs_context()
    print('~~~')


def update():
    print('~~~update_1~~~')


def delete():
    print('~~~delete_1~~~')
    drs = u_list_dirs()
    for i in range(len(drs)):
        print(i, drs[i])
    while True:
        s = input('Enter nr of directory to delete_all_data_on_selected_contract, \'b\' to return : ')
        if s == 'b':
            os.system('clear')
            # p.back()
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(drs)):
                    shutil.rmtree('./' + drs[int(s)])
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
