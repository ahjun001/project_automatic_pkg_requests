#!/usr/bin/env python3
# p2_select_templates.py
import os
import pathlib
import shutil
from tkinter.filedialog import askopenfilename

import m_menus as m
import p1_select_contract as p1

p2_templates_l = [
    'a.Outer_box_外箱',
    'b.Inner_box_内盒',
    'c.Inside_box_中箱',
    'd.Prod_packaging_产品包装',
    'e.Plastic_bag_塑料袋',
    'f.Prod_sticker_塑料上不干胶',
]

p2_default_templates_l = [
    'a.Outer_box_外箱',
    'f.Prod_sticker_塑料上不干胶',
]


def add_templates_from_list(list_l, ask_questions):
    new_temp_abs_dir = ''
    # read existing templates
    drs = p2_load_templates_info_l()
    # make a candidate set of templates to be added
    candidates_l = []
    if drs:
        for lg in list_l:
            if lg not in drs:
                candidates_l.append(lg)
    else:
        candidates_l = list(list_l)

    if ask_questions:
        select_templates_context_func(prompt=False)
        print('>>> Select # in front of the template name to be added:\n')
        for i in range(len(candidates_l)):
            print(str(i) + '. ' + candidates_l[i][2:])
        while True:
            s = input('\nEnter nr of directory to be created, \'b\' to return : ')
            if s == 'b':
                m.clear()
                break
            else:
                try:
                    s_i = int(s)
                    if s_i in range(len(candidates_l)):
                        new_temp_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, candidates_l[s_i])
                        create_template_dir(candidates_l[s_i])
                        break
                    else:
                        print('Integer, but not an option, try again')
                except ValueError:
                    print('That\'s not an integer, try again')

        print('~~~ Select a template svg file in the graphic file browser -- mind the browser window could be hidden')
        ini_svg = askopenfilename()
        if not ini_svg:
            return False
        # split path and filename
        path, filename_ext = os.path.split(ini_svg)
        # split filename and extension
        filename, ext = os.path.splitext(filename_ext)
        # check extension indeed is '.svg'
        if ext == '.svg':
            shutil.copy(ini_svg, os.path.join(new_temp_abs_dir, 'label_template.svg'))
        else:
            print(f'\nSelected file {filename} extension is not \'.svg\'\n')
            return False

        # copy 'template-info.json' file from same directory if it exists
        p3_f = os.path.join(path, 'template-info.json')
        if pathlib.Path(p3_f).exists():
            shutil.copy(p3_f, new_temp_abs_dir)
        return True

    else:
        for c in candidates_l:
            create_template_dir(c)


def load_or_create_templates():
    drs = p2_load_templates_info_l()
    if not drs:
        add_templates_from_list(p2_default_templates_l, ask_questions=False)


def read_dirs(walk_abs_dir):
    if walk_abs_dir:
        _, dirs, _ = next(os.walk(walk_abs_dir))
        if dirs:
            dirs.sort()
            dirs[:] = [d for d in dirs if d[0] not in ['.', '_']]
            return dirs
    return None


def display_dirs(walk_abs_dir):
    drs = read_dirs(walk_abs_dir)
    if drs:
        for dr in drs:
            print(dr)
        return True
    else:
        return False


def load_n_display():
    display_dirs(p1.p1_cntrct_abs_dir)


def p2_load_templates_info_l():  # used in p3
    """
    :return: list of label subdirectories to the main contract directory
    """
    result_l = read_dirs(p1.p1_cntrct_abs_dir)
    if  result_l and 'pics' in result_l:
        result_l.remove('pics')
    return result_l


def add_new_template():
    add_templates_from_list(p2_templates_l, ask_questions=True)


def delete_existing_template():
    print('~~~ Deleting templates non-empty directory data')
    drs = p2_load_templates_info_l()
    if not drs:
        return
    for i in range(len(drs)):
        print(i, drs[i][2:])
    print('~~~')
    while True:
        s = input('Enter nr of template to delete, \'b\' to return:\n')
        if s == 'b':
            m.clear()
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(drs)):
                    shutil.rmtree(os.path.join(p1.p1_cntrct_abs_dir, drs[s_i]))
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


def create_template_dir(dr):
    lbl_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, dr)
    if not pathlib.Path(lbl_abs_dir).exists():
        os.mkdir(lbl_abs_dir, mode=0o700)


def select_templates_context_func(prompt=True):
    print('~~~ Step 2: Selecting templates to print ~~~')
    print('Editing contract #: ', p1.p1_d["cntrct_nr"] if p1.p1_d["cntrct_nr"] else None)
    print('\nTemplates already added:')
    if not display_dirs(p1.p1_cntrct_abs_dir):
        print('None added yet')
    print(60 * '-', '\n\n')
    if prompt:
        print('\n>>> Select action: ')


context_func_d = {
    'p2_select_templates': select_templates_context_func,
    'debug': select_templates_context_func,
}


# noinspection PyPep8Naming,NonAsciiCharacters
def step_2__select_templates_to_print_选择_编辑标签类型():
    # make sure p1 has been run
    if not p1.contract_info_d_load():
        print('p1 has not run successfully')

    # initializing menus last, so that context functions display most recent information
    m.menu = 'p2_select_templates'
    # m.mod_lev_1_menu = m.menu
    if not m.main_menu:
        m.main_menu = m.menu
    m.menus = {
        m.menu: {
            '1': load_or_create_templates,
            '2': add_new_template,
            '3': delete_existing_template,
            'b': m.back_to_main_退到主程序,
            'q': m.normal_exit_正常出口,
            'd': m.debug,
        },
        'debug': {
            '2': load_n_display,
            'b': m.back_后退,
            'q': m.normal_exit_正常出口,
        },
    }
    if not m.main_menus:
        m.main_menus = m.menus
    if __name__ == '__main__':
        m.mod_lev_1_menu = m.menu
        m.mod_lev_1_menus = m.menus
    m.context_func_d = {**m.context_func_d, **context_func_d}


def main():
    """ Driver """
    step_2__select_templates_to_print_选择_编辑标签类型()
    m.run()


if __name__ == '__main__':
    main()
