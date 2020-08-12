#!/usr/bin/env python3
import os
import random
import menus_n_loop as m
import json_struct_process as j

###################################################################################################
#  a process: create d.result['a'] and a.json
# low level functions:
# Create
a_inputs = {}


def a_process_in_memory(force_create = False):
    j.overall_process_d['a'] = random.choice(['a', 'A'])


def a_read():
    return 'a' in j.overall_process_d and j.overall_process_d['a'] in ['a', 'A']


def a_delete():
    j.overall_process_d['a'] = ''
    if os.path.exists('a.json'):
        if not os.remove('a.json'):  # = None
            return True
    else:
        return False


a = j.JsonStructProcess('a', 'a.json', a_inputs, a_process_in_memory, a_read, a_delete)

###################################################################################################
# b process: inputs 'a' or 'A', creates 'b1' or 'B1', store in b1.json, 'b2' or 'B2', store in b2.json
#  'b3' or 'B3', store in b3.json
b_inputs = {'a': a.load_or_create}


def b_process_in_memory(force_create = False):
    j.overall_process_d['b'] = random.choice(['b', 'B'])


def b_read():
    return 'b' in j.overall_process_d and j.overall_process_d['b'] in ['b', 'B']


def b_delete():
    j.overall_process_d['b'] = ''
    if os.path.exists('b.json') and not os.remove('b.json'):
        return True
    else:
        return False


b = j.JsonStructProcess('b', 'b.json', b_inputs, b_process_in_memory, b_read, b_delete)

###################################################################################################
# c process: inputs 'b' or 'B', creates 'c' or 'c', store in c.json


c_inputs = {'b': b.load_or_create}


def c_process_in_memory(force_create = False):
    j.overall_process_d['c'] = random.choice(['c', 'C'])


def c_read():
    return 'c' in j.overall_process_d and j.overall_process_d['c'] in ['c', 'C']


def c_delete():
    j.overall_process_d['c'] = ''
    if os.path.exists('c.json'):
        if not os.remove('c.json'):  # = None
            return True
    else:
        return False


c = j.JsonStructProcess('c', 'c.json', c_inputs, c_process_in_memory, c_read, c_delete)

###################################################################################################
# shell interface data & functions
context_func_d = {
    'pull': lambda: 0,
    'push': lambda: 0,
    'test_scenari': lambda: 0,
}


def mod_abc():
    # initializing menus last, so that context functions display most recent information
    m.menu = 'pull'
    if not m.main_menu:
        m.main_menu = m.menu
    m.menus = {
        m.menu: {
            'la': a.load_or_create,
            'pa': a.push,
            'da': a.delete,
            'lb': b.load_or_create,
            'pb': b.push,
            'db': b.delete,
            'lc': c.load_or_create,
            'pc': c.push,
            # 'dc': c.delete,
            # 'p': m.push,
            't': m.test_scenari,
            'b': m.back_to_main_退到主程序,
            'q': m.normal_exit_正常出口,
        },
        'push': {
            # 'pe': push_e,
            # 'pf': push_f,
            'b': m.back_后退,
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
    mod_abc()
    m.run()


if __name__ == '__main__':
    main()
