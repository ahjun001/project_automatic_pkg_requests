#!/usr/bin/env python3
"""
    p0u_utils.py

    Utility functions
     """
import json
import os
import pathlib
import re
import sys

import p0g_global_values as g




########################
#  Running the interface
########################


def re_init():
    """
    Should run so as to get all variables updated, not only when system starts,
    but also when a new contract is selected, 

         """
    __PRINT__ = False

    # If the data directory does not exist, create it
    data = os.path.join(g.root_dir, 'data')
    if not os.path.exists(data):
        os.mkdir(data, mode = 0o700)

    # point to the program-info.json file if it exists
    g.program_info_f = os.path.join(g.root_dir, 'program-info.json')

    """
        When the program starts the trace of program_info is in program-info.json if it exists, then it would be in 
        the program_info_d dictionary
        if a program-info exists:
            if cntrct_nr
            if a previous program is indicated -- cntrct_nr -- exists: check that the xls file exists in ./data/
        If no program-info.json exists in root_dir: create one
        """
    if g.program_info_d:
        # The program is already running this is updating program_info_d and then program-info_f
        if 'cntrct_nr' in g.program_info_d:
            _, result = check_a_unique_contract_ext_file_w_o_wo_prefix_exists_in_dir(g.root_dir +
                                                                 f'/data/{g.program_info_d["cntrct_nr"]}', '.xls')
            if not result:
                del g.program_info_d['cntrct_nr']
                set_program_info_d_on_root_xls_file()
    else:

        set_program_info_d_on_root_xls_file()

    # g.filename_source_xls = '/home/perubu/Desktop/11.27_lbl_factory_mvc/xls/A911008-008 嘉兴凯顺 双一字槽瓦楞钉.xls'
    if g.filename_source_xls is None:
        g.filename_source_xls = os.path.join(g.root_dir, 'xls/', 'A911008-008 嘉兴凯顺 双一字槽瓦楞钉.xls')
    print(f'self: g.filename_source_xls = {g.filename_source_xls}') if __PRINT__ else print('', end = '')

    # g.filename_xls = A911008-008 嘉兴凯顺 双一字槽瓦楞钉.xls'
    _, g.filename_xls = os.path.split(g.filename_source_xls)  # removing absolute path
    # print(f'self: path = {path}')
    print(f'self: g.filename_xls = {g.filename_xls}') if __PRINT__ else print('', end = '')

    # g.filename = A911008-008 嘉兴凯顺 双一字槽瓦楞钉 , ext = .xls
    g.filename, ext = os.path.splitext(g.filename_xls)  # removing extension
    print(f'self: g.filename = {g.filename}') if __PRINT__ else print('', end = '')
    print(f'self: ext = {ext}') if __PRINT__ else print('', end = '')

    # g.cntrct_nr = A911008-008
    g.contract_nr = re.match(r'\w+-\d+', g.filename).group()  # extract contract # & sub-#
    print(f'self: g.cntrct_nr = {g.contract_nr}') if __PRINT__ else print('', end = '')

    # g.contract_dir = /home/perubu/Desktop/11.27_lbl_factory_mvc/data/A911008-008
    g.contract_dir = os.path.join(g.root_dir, 'data/', g.contract_nr)
    print(f'self: g.contract_dir = {g.contract_dir}') if __PRINT__ else print('', end = '')

    # g.contract_dir_xls = /home/perubu/Desktop/11.27_lbl_factory_mvc/data/A911008-008/A911008-008 嘉兴凯顺
    # 双一字槽瓦楞钉.xls
    g.contract_dir_xls = os.path.join(g.contract_dir, g.filename_xls)
    print(f'self: g.contract_dir_xls = {g.contract_dir_xls}') if __PRINT__ else print('', end = '')

    # g.lbl_lst = ['1.Outer_box-外箱', '6.Prod_sticker-产品上不干胶']
    g.lbl_lst = ['1.Outer_box-外箱', '6.Prod_sticker-产品上不干胶']
    print(f'self: g.lbl_lst = {g.lbl_lst}') if __PRINT__ else print('', end = '')

    # g.lbl_sel = '1.Outer_box-外箱'
    g.lbl_sel = g.lbl_lst[0]
    print(f'self: g.lbl_sel = {g.lbl_sel}') if __PRINT__ else print('', end = '')

    # g.lbl_dir = /home/perubu/Desktop/11.27_lbl_factory_mvc/data/A911008-008/1.Outer_box-外箱
    g.lbl_dir = g.contract_dir + '/' + g.lbl_sel
    print(f'self: g.lbl_dir = {g.lbl_dir}') if __PRINT__ else print('', end = '')

    if not g.program_info_d:
        prefix, _ = check_a_unique_contract_ext_file_w_o_wo_prefix_exists_in_dir(g.root_dir, '.xls')
        g.program_info_d = {
            'contract_root': prefix,
        }
    update_program_info()
    print(f'self: g.program_info_d = {g.program_info_d}') if __PRINT__ else print('', end = '')


def update_program_info():
    if g.program_info_d['contract_root'] != g.contract_nr:
        g.program_info_d['cntrct_nr'] = g.contract_nr
    program_info_f = os.path.join(g.root_dir, 'program-info.json')
    with open(program_info_f, 'w') as f:
        json.dump(g.program_info_d, f, ensure_ascii = False)


def run():
    keep = True
    previous_menu = g.menu
    while keep:
        print(f'In process {g.menu}, currently working on: {g.contract_nr}\n')
        # display g.menu with data from g.menus dict
        for k, v in g.menus.get(g.menu).items():
            print(f'{k}. {v.__name__}')
        choice = input("\nEnter an option: ")
        os.system('clear')
        execute_option = g.menus[g.menu].get(choice)
        if choice in ['m']:
            g.menu = g.entry_level_menu
            g.menus = g.entry_level_menus
            keep = False
        elif choice in ['b']:
            g.menu = previous_menu
        else:
            if previous_menu == 'main_menu':
                previous_menu = g.menu
            if g.entry_level_menu is None:
                g.entry_level_menu = g.menu
            if g.entry_level_menus is None:
                g.entry_level_menus = g.menus
            if execute_option:
                execute_option()
            else:
                print(f'\n{choice} is not a valid choice\n')


def back():
    print('~~~ Returning to main menu ~~~')
    g.menu = g.entry_level_menu


def back_to_main():
    pass  # should not get there since would exit the run loop before execution


def normal_exit():
    print('~~~ Exiting program ~~~')
    sys.exit(0)
