#!/usr/bin/env python3
import os
import p1_select_contract as p1
import p2_select_labels as p2  # todo move variables so that they don't call p2
import u_maintain_set_of_indicators_regex_to_be_searched as i
import u_menus as p

p0_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located


def main_menu_context():
    print(f'p1 selected contract: {p1.p1_contract_nr}')
    print(f'p2 selected labels: {p1.read_dirs(p1.p1_contract_dir)}')
    print(f'p3 selected distinctive fields: {p2.already_selected_l}')
    print('~~~ Main menu:')


context_func_d = {
    'main_menu': main_menu_context,
}


def init():
    # menus
    p.menu = 'main_menu'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': p1_select_contract,
            '2': p2_select_labels,
            'u': u_maintain_set_of_indicators_regex_to_be_searched,
            'q': p.normal_exit,
        },
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}

    # reading repository
    # If the data directory does not exist, auto_create it
    data_dir = os.path.join(p0_root_dir, 'data')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir, mode=0o700)


def p1_select_contract():
    p1.init()


def p2_select_labels():
    p2.init()


def p3_select_fields():
    pass


def u_maintain_set_of_indicators_regex_to_be_searched():
    i.init()


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
