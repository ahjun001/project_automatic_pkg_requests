#!/usr/bin/env python3
import os
import shutil

import py_menus as p


def proc_del_dirs_context():
    print('~~~ Deleting dicts context ~~~')


context_func_d = {
    'Select dir to delete:': proc_del_dirs_context,
}

_, drs, _ = next(os.walk('.'))
drs.sort()
drs[:] = [d for d in drs if d[0] not in ['.', '_']]


def make_f(dd):
    def func():
        shutil.rmtree('./' + dd)
        p.back()

    func.__name__ = dd
    return func


functions_d = {}
for dr in drs:
    print('Processing: ', dr)
    functions_d[dr] = make_f(dr)


def init():
    global drs
    p.menu = 'Select dir to delete:'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            str(i): functions_d[drs[i]] for i in range(len(drs))
        },
    }
    p.menus[p.menu]['b'] = p.back
    p.menus[p.menu]['q'] = p.normal_exit
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
