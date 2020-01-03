#!/usr/bin/env python3
import csv
import os
import subprocess

import pandas as pd

import u_global_values as g
import py_menus as p


def p_context():
    print('~~~ Context for indicators maintenance ~~~')


context_func_d = {
    'u_maintain_set_of_indicators_RegEx_to_be_searched': p_context,
}


def init():
    p.menu = 'u_maintain_set_of_indicators_RegEx_to_be_searched'  # required to display on main_menu
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '3': update,
            'm': p.back_to_main,
            'q': p.normal_exit,
        },
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}


indicators_csv = os.path.join(g.p1_root_dir + '/common', 'indicators.csv')


def read():
    return pd.read_csv(indicators_csv, quoting = csv.QUOTE_NONE)


def update():
    subprocess.call(['/usr/bin/xed', indicators_csv])
    read()


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
