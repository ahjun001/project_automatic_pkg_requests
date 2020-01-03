#!/usr/bin/env python3

import py_menus as p
import p1_set_up_full_dir_struct_n_process_info as p1
import p2_select_label_kinds_n_print as p2
import u_maintain_set_of_indicators_regex_to_be_searched as i
import u_global_values as g


def main_menu_context():
    print('Context when running main')
    g.display_dirs('.')


context_func_d = {
    'main_menu': main_menu_context,
}


def init():
    p.menu = 'main_menu'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': p1_set_up_full_dir_struct_n_process_info,
            '2': p2_select_label_kinds_n_print,
            'u': u_maintain_set_of_indicators_RegEx_to_be_searched,
            'q': p.normal_exit,
        },
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}


def p1_set_up_full_dir_struct_n_process_info():
    p1.init()

def p2_select_label_kinds_n_print():
    p2.init()

def u_maintain_set_of_indicators_RegEx_to_be_searched():
    i.init()


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
