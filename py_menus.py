#!/usr/bin/env python3
import os
import sys

menu = main_menu = mod_lev_1_menu = None
menus = main_menus = mod_lev_1_menus = {}


def back():
    global menu
    global mod_lev_1_menu

    menu = mod_lev_1_menu
    print('~~~ Returning to level 1  ~~~')


def back_to_main():  # just there to have a selection in the menu, the function won't be executed
    global menu, main_menu
    global menus, main_menus

    menu = main_menu
    menus = main_menus
    print('~~~ Returning to main  ~~~')


def normal_exit():
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

    # storing last menu to come back either from module menu to main_menu, or from sub_menu to module menu
    keep = True
    while keep:
        print()
        menus_context_func()
        print()
        # display menu with data from menus dict
        for k, v in menus.get(menu).items():
            # for each menu entry: key to execute, function to be executed (name should be explicit)
            print(f'{k}. {v.__name__}')
        selection = input("\nEnter selection: ")
        os.system('clear')
        print(f'Option {selection} selected')
        # getting the function name from the key entered
        selection_func_name = menus[menu].get(selection)

        if selection_func_name:
            selection_func_name()
        else:
            print(f'\n{selection} is not a valid selection\n')