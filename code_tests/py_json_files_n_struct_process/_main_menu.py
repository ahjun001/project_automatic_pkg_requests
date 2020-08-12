#!/usr/bin/env python3
import os

import menus_n_loop as m
import mod_abc
import mod_def

p0_root_abs_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located


def pull_menu_context_func():
    print('displaying pull context function')
    print(60 * '-', '\n\n')
    print('>>> Pull menu:')


def push_menu_context_func():
    print('displaying push menu context function')
    print(60 * '-', '\n\n')
    print('>>> Push menu:')


def qual_test_menu_context_func():
    print('displaying test menu context function')
    print(60 * '-', '\n\n')
    print('>>> Test menu:')


context_func_d = {
    'pull': pull_menu_context_func,
    'push': push_menu_context_func,
    'test': qual_test_menu_context_func
}


def init():
    # ret_value = os.system('clear')
    # print('os.system:', ret_value)
    # menus
    m.menu = 'pull'
    # m.mod_lev_1_menu = m.menu
    if not m.main_menu:
        m.main_menu = m.menu
    m.menus = {
        m.menu: {
            '1': mod_abc.mod_abc,
            '2': mod_def.mod_def,
            '3': m.push,
            '4': m.test_scenari,
            'q': m.normal_exit_正常出口,
        },
        'push': {
            'b': m.back_后退,
            'q': m.normal_exit_正常出口,
        },
        'test': {
            'b': m.back_后退,
            'q': m.normal_exit_正常出口,
        },
    }
    # m.mod_lev_1_menus = m.menus
    if not m.main_menus:
        m.main_menus = m.menus

    if __name__ == '__main__':
        m.mod_lev_1_menu = m.menu
        m.mod_lev_1_menus = m.menus

    m.context_func_d = {**m.context_func_d, **context_func_d}


def main():
    """ Driver """
    init()
    m.run()


if __name__ == '__main__':
    main()
