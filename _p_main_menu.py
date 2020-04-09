#!/usr/bin/env python3
import json
import os
import pathlib
import shutil
from datetime import datetime

import m_menus as m
import p1_select_contract as p1
import p2_select_templates as p2
import p3_select_specific_fields as p3
import pu_maintain_set_of_indicators_regex_to_be_searched as pu

p0_root_abs_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located


def run_full_demo_with_selected_or_default_values_运行完整演示():
    p1.process_selected_contract()
    p2.create_default_templates()
    p3.display_all()


def main_menu_context_func():
    temp_f = []
    c_nr = p1.p1_d['cntrct_nr'] if 'cntrct_nr' in p1.p1_d.keys() else ''
    print(f'Step 1 selected contract: ' + f'{c_nr if c_nr else "None"}')
    templ_l, default = p1.read_dirs(p1.p1_cntrct_abs_dir), ''
    if not templ_l:
        templ_l, default = p2.p2_default_templates_l, ' (Default)'
    print(f'Step 2 selected templates to print: {templ_l} {default}')
    p3_f = os.path.join(p1.p1_cntrct_abs_dir + '/' + templ_l[0], 'template-info.json')
    if pathlib.Path(p3_f).exists():
        with open(p3_f) as f:
            p3_d = json.load(f)
        temp_f = p3_d['selected_fields']
    else:
        if 'selected_fields' in p3.p3_d.keys():
            temp_f = f'{p3.p3_d["selected_fields"]} (Defaults)'
        # either read data,
    print(f'Step 3 selected fields to print for each template: {temp_f}')
    print(60 * '-', '\n\n')
    print('>>> Main menu:')


context_func_d = {
    'root_menu': main_menu_context_func,
    'debug': main_menu_context_func,
}


def save_selected_contract():
    main_dir = p0_root_abs_dir + '/contract_samples/' + p1.p1_d['cntrct_nr']
    copy_dir = main_dir + '_' + str(datetime.timestamp(datetime.now()))
    shutil.copytree(main_dir, copy_dir)

    shutil.copy(os.path.join(p1.p1_cntrct_abs_dir, p1.p1_d['cntrct_nr'] + '_doc_setup.json'), main_dir)

    drs = p1.read_dirs(p1.p1_cntrct_abs_dir)
    if drs:
        for dr in drs:
            shutil.copy(os.path.join(p1.p1_cntrct_abs_dir + '/' + dr, 'template-info.json'), main_dir + '/' + dr)
            shutil.copy(os.path.join(p1.p1_cntrct_abs_dir + '/' + dr, 'label_template.svg'), main_dir + '/' + dr)


def step_1__select_a_contract_选择合同号():
    # p1.reset_globals()
    p3.reset_globals()
    p1.step_1__select_a_contract_选择合同号()


def init():
    os.system('clear')
    # assign a program
    p1.load_o_create_program_info_d()
    # menus
    m.menu = 'root_menu'
    # m.mod_lev_1_menu = m.menu
    if not m.main_menu:
        m.main_menu = m.menu
    m.menus = {
        m.menu: {
            '0': run_full_demo_with_selected_or_default_values_运行完整演示,
            '1': step_1__select_a_contract_选择合同号,
            '2': p2.step_2__select_templates_to_print_选择_编辑标签类型,
            '3': p3.step_3__select_fields_to_print_for_each_template_选择每种标签类型的资料,
            '4': save_selected_contract,
            '5': p1.process_selected_contract,
            'q': m.normal_exit_正常出口,
            'd': m.debug,
        },
        'debug': {
            'u': pu.u_maintain_set_of_indicators_regex_to_be_searched,
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

    # If the data directory does not exist, process_selected_contract it
    data_adir = os.path.join(p0_root_abs_dir, 'data')
    if not pathlib.Path(data_adir).exists():
        os.mkdir(data_adir, mode = 0o700)


def main():
    """ Driver """
    init()
    m.run()


if __name__ == '__main__':
    main()
