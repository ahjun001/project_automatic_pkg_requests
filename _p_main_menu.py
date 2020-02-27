#!/usr/bin/env python3
import os
import pathlib

import p0_menus as p
import p1_select_contract as p1
import p2_select_templates as p2
import p3_select_specific_fields as p3
import pu_maintain_set_of_indicators_regex_to_be_searched as i

p0_root_abs_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located


def run_full_demo_with_assigned_values_运行完整演示():
    p1.process_selected_contract()
    p2.create_default_templates()
    p3.display_all()


def p1_select_contract():
    p1.init()


def p2_select_templates():
    p2.init()


def p3_select_distinctive_fields():
    p3.init()


def u_maintain_set_of_indicators_regex_to_be_searched():
    i.init()


def step_1__select_a_contract_选择合同号():
    p1.select_new_contract()


def step_2__select_type_of_labels_to_print_选择_编辑标签类型():
    pass


def step_3__select_fields_to_print_for_each_label_type_选择每种标签类型的资料():
    pass


def display_and_edit_svg_files():
    pass


def export_svg_s_to_pdf_and_collate():
    pass


def main_menu_context_func():
    c_nr = p1.p1_d['cntrct_nr'] if 'cntrct_nr' in p1.p1_d.keys() else ''
    print(f'Step 1 selected contract: ' + f'{c_nr if c_nr else "None"}')
    templ_l = p1.read_dirs(p1.p1_cntrct_abs_dir)
    if not templ_l:
        templ_l = p2.p2_default_templates_l
    print(f'Step 2 selected type of labels to print: {templ_l}')
    print(f'Step 3 selected fields to print for each label type: {p3.p3_d["selected_fields"]}')
    print(60 * '-', '\n\n')
    print('>>> Main menu:')


context_func_d = {
    'root_menu': main_menu_context_func,
    'debug': main_menu_context_func,
}


def init():
    # assign a program
    p1.load_o_create_program_info_d()
    # menus
    p.menu = 'root_menu'
    # p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '0': run_full_demo_with_assigned_values_运行完整演示,
            '1': step_1__select_a_contract_选择合同号,
            '2': step_2__select_type_of_labels_to_print_选择_编辑标签类型,
            '3': step_3__select_fields_to_print_for_each_label_type_选择每种标签类型的资料,
            'q': p.normal_exit_正常出口,
            'd': p.debug,
        },
        'debug': {
            '1': p1_select_contract,
            '2': p2_select_templates,
            '3': p3_select_distinctive_fields,
            'u': u_maintain_set_of_indicators_regex_to_be_searched,
            'b': p.back,
            'q': p.normal_exit_正常出口,
        },
    }
    # p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus

    if __name__ == '__main__':
        p.mod_lev_1_menu = p.menu
        p.mod_lev_1_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}

    # If the data directory does not exist, process_selected_contract it
    data_adir = os.path.join(p0_root_abs_dir, 'data')
    if not pathlib.Path(data_adir).exists():
        os.mkdir(data_adir, mode = 0o700)


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
