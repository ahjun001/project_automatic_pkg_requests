#!/usr/bin/env python3
import os
import p0_menus as p
import p1_select_contract as p1
import p2_select_labels as p2
import p3_select_specific_fields as p3
import pu_maintain_set_of_indicators_regex_to_be_searched as i

p0_root_adir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located


def main_menu_context_func():
    print(f'p1 selected contract: {p1.p1_contract_nr if p1.p1_contract_nr else None}')
    print(f'p2 selected labels: {p1.read_dirs(p1.p1_contract_adir)}')
    print(f'p3 selected distinctive fields: {p3.p3_already_selected_l}')
    print('>>> Main menu:')


context_func_d = {
    'main_menu': main_menu_context_func,
}


def init():
    # menus
    p.menu = 'main_menu'
    # p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': run_all_with_default_values,
            '2': p1_select_contract,
            '3': p2_select_labels,
            '4': p3_select_distinctive_fields,
            'u': u_maintain_set_of_indicators_regex_to_be_searched,
            'q': p.normal_exit,
        },
    }
    # p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus

    if __name__ == '__main__':
        p.mod_lev_1_menu = p.menu
        p.mod_lev_1_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}

    # If the data directory does not exist, process_default_contract it
    data_adir = os.path.join(p0_root_adir, 'data')
    if not os.path.exists(data_adir):
        os.mkdir(data_adir, mode=0o700)


def run_all_with_default_values():
    p1.process_default_contract()
    p2.create_default_labels()
    p3.process_all_labels_with_default_specific_fields()


def p1_select_contract():
    p1.init()


def p2_select_labels():
    p2.init()


def p3_select_distinctive_fields():
    p3.init()


def u_maintain_set_of_indicators_regex_to_be_searched():
    i.init()


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
