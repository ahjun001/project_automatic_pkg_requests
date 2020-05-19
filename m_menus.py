#!/usr/bin/env python3
import os
import sys

menu = main_menu = mod_lev_1_menu = None
menus = main_menus = mod_lev_1_menus = {}
root_abs_dir = os.path.dirname(os.path.abspath(__file__))


def back_后退():
    global menu
    global mod_lev_1_menu

    print('~~~ Returning to level 1  ~~~')
    menu = mod_lev_1_menu


def back_to_main_退到主程序():  # just there to have a selection in the menu, the function won't be executed
    global menu, main_menu
    global menus, main_menus

    print('~~~ Returning to main  ~~~')
    menu = main_menu
    menus = main_menus


def debug():
    global mod_lev_1_menu
    global menu

    print('~~~debug~~~')
    mod_lev_1_menu = menu
    menu = 'debug'


def normal_exit_正常出口():
    print('~~~ Regular program exit ~~~')
    sys.exit(0)


context_func_d = {
}


def menus_context_func():
    global context_func_d
    global menu
    context_func_d[menu]()


def run():
    global menu
    global menus
    global main_menu
    global main_menus

    # storing last menu to come back_后退 either from module menu to main_menu, or from sub_menu to module menu
    keep = True
    while keep:
        print()
        menus_context_func()
        print()
        # display_sub_processes_output menu with data from menus dict
        for k, v in menus.get(menu).items():
            # for each menu entry: key to execute, function to be executed (name should be explicit)
            print(f'{k}. {v.__name__}')
        selection = input("\nEnter selection: ")
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f'Option {selection} selected')
        # getting the function name from the key entered
        selection_func_name = menus[menu].get(selection)

        if selection_func_name:
            selection_func_name()
        else:
            print(f'|\n| {selection} is not a valid selection\n|')
