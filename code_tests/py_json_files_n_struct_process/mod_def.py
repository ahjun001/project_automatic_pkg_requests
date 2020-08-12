#!/usr/bin/env python3
import os
import random
import menus_n_loop as m
import json_struct_process as j
import mod_abc as abc

###################################################################################################
#  d process: create d.result['d'] and d.json
# low level functions:
# Create
d_inputs = {'c': abc.c.load_or_create}


def d_process_in_memory(force_create = False):
    j.overall_process_d['d'] = random.choice(['d', 'D'])


def d_read():
    return 'd' in j.overall_process_d and j.overall_process_d['d'] in ['d', 'D']


def d_delete():
    j.overall_process_d['d'] = ''
    if os.path.exists('d.json'):
        if not os.remove('d.json'):  # = None
            return True
    else:
        return False


d = j.JsonStructProcess('d', 'd.json', d_inputs, d_process_in_memory, d_read, d_delete)

###################################################################################################
# e process: inputs 'd' or 'D', creates 'e' or 'E', store in e.json
e_inputs = {'d': d.load_or_create}


def e_process_in_memory(force_create = False):
    if force_create:
        print('low level: e process, will run only if force_create = True')
        j.overall_process_d['e'] = random.choice(['e', 'E'])


def e_read():
    return 'e' in j.overall_process_d and j.overall_process_d['e'] in ['e', 'E']


def e_delete():
    j.overall_process_d['e'] = ''
    if os.path.exists('e.json'):
        if not os.remove('e.json'):  # = None
            return True
    else:
        return False


e = j.JsonStructProcess('e', 'e.json', e_inputs, e_process_in_memory, e_read, e_delete)

###################################################################################################
# f process: inputs 'e' or 'E', creates 'f' or 'f', store in f.json


f_inputs = {'e': e.load_or_create}


def f_process_in_memory(force_create = False):
    print('low level: f process, will run for each loop')
    j.overall_process_d['f'] = random.choice(['f', 'F'])


def f_read():
    return 'f' in j.overall_process_d and j.overall_process_d['f'] in ['f', 'F']


def f_delete():
    j.overall_process_d['f'] = ''
    if os.path.exists('f.json'):
        if not os.remove('f.json'):  # = None
            return True
    else:
        return False


f = j.JsonStructProcess('f', 'f.json', f_inputs, f_process_in_memory, f_read, f_delete)

###################################################################################################
# shell interface data & functions
context_func_d = {
    'pull': lambda: 0,
    'push': lambda: 0,
    'test_scenari': lambda: 0,
}


def mod_def():
    # initializing menus last, so that context functions display most recent information
    m.menu = 'pull'
    if not m.main_menu:
        m.main_menu = m.menu
    m.menus = {
        m.menu: {
            'ld': d.load_or_create,
            'pd': d.push,
            'dd': d.delete,
            'le': e.load_or_create,
            'pe': e.push,
            'de': e.delete,
            'lf': f.load_or_create,
            'pf': f.push,
            'df': f.delete,
            'p': m.push,
            't': m.test_scenari,
            'b': m.back_to_main_退到主程序,
            'q': m.normal_exit_正常出口,
        },
        'push': {
            # 'pe': push_e,
            # 'pf': push_f,
            'e': m.back_后退,
            'q': m.normal_exit_正常出口
        },
        'test_scenari': {
            # 'ld': load_or_create_d,
            # 'pd': push_d,
            # 'le': load_or_create_e,
            # 'pe': push_e,
            # 'de': delete_e,
            # 'lf': load_or_create_f,
            # 'pf': push_f,
            # 'df': delete_f,
            'b': m.back_后退,
            'q': m.normal_exit_正常出口
        }
    }
    if not m.main_menus:
        m.main_menus = m.menus
    if __name__ == '__main__':
        m.mod_lev_1_menu = m.menu
        m.mod_lev_1_menus = m.menus
    m.context_func_d = {**m.context_func_d, **context_func_d}


# driver
def main():
    """ Driver """
    mod_def()
    m.run()


if __name__ == '__main__':
    main()
