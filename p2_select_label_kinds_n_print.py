#!/usr/bin/env python3
# p6_set_up_label_dirs_n_infos
import json
import os
import shutil

import p1_set_up_full_dir_struct_n_process_info as p1
import u_global_values as g
import py_menus as p


def proc_2_context():
    print('~~~ Context p6 set up label dirs n infos ~~~')


context_func_d = {
    'p6_set_up_label_dirs_n_infos': proc_2_context,
}


def init():
    p.menu = 'p6_set_up_label_dirs_n_infos'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': create,
            '2': display,
            '3': update,
            '4': delete,
            '5': g.display_p2_labels_info_d,
            '6': g.display_p2_labels_info_f,
            '7': create_selected_indicators_set,
            '8': p7_display_selected_indicators,
            '9': cd_to_selected_dir,
            'm': p.back_to_main,
            'q': p.normal_exit,
        },
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}

    # make sure p1 infrastructure is in place
    # if not g.p1_read():
    #     p1.Controller(p1.View())

    if not g.chdir_n_p2_read():
        p1.init()
        p1.create()

    os.chdir(g.p1_contract_dir)


already_selected_l = []
p7_specific_indics_d_of_d = {}
options_l = []


def create():
    drs = g.read_dirs(g.p1_contract_dir)
    if not drs:
        create_label_dirs(g.standard_labels_l)
    # documenting in memory but not on disk, so as to keep the option of editing out of program
    # then p2_labels_info_d and p2_labels_info_f will look different
    # g.p2_labels_info_d['p6_label_l'] = g.read_dirs(g.p1_contract_dir)

    # create canonical p6_lbl_dir and p6_lbl_sel
    """
    for dr in drs:
        g.p6_lbl_sel = dr
        g.p6_lbl_dir = os.path.join(g.p1_contract_dir, g.p6_lbl_sel)
        # g.write_in_mem_n_on_disk()
        if g.chdir_n_p7_read():
            already_selected_l = g.p7_label_info_d['selected_indicators']

        # create selected indicators set
        with open(os.path.join(g.p1_contract_dir, g.p2_labels_info_d['p6_extract_specifics'])) as fj:
            p7_specific_indics_d_of_d = json.load(fj)
        options_l = list(next(iter(p7_specific_indics_d_of_d.values())))

        # function factory: defining what each label function should be doing
        def make_f(indic):
            def func():
                already_selected_l.append(indic)
                m.menu = menu
                m.menus = menus

            func.__name__ = indic  # as function is not read before being called for execution
            return func

        functions_d = {}
        for option in options_l:
            functions_d[option] = make_f(option)

        def back():
            m.menu = menu
            m.menus = menus

        assert back == back  # unless Lint would report back is not used

        m.menu = 'Select label to add'
        m.menus = {m.menu: {}}
        for i in range(len(options_l)):
            if options_l[i] not in already_selected_l:
                m.menus[m.menu][f'{i}'] = functions_d[options_l[i]]
        m.menus[m.menu]['m'] = eval('back')
        m.run(p7_display_selected_indicators)  # argument to give context for decision

        g.p7_label_info_d['selected_indicators'] = already_selected_l

        with open(g.p7_label_info_f, 'w') as f:
            json.dump(g.p7_label_info_d, f, ensure_ascii = False)

        make_mako()
            """


def make_mako():
    # writing the input file for Mako
    mako_input = ''
    with open(os.path.join('..', 'p4_' + g.p1_contract_nr + '_indics_from_contract_l.json')) as f:
        p7_indcs_from_contract_l = json.load(f)  # todo: replace by mem pointer if it exists
    if already_selected_l:
        # building the header
        mako_input += 'idx, prod_n'
        for indc in already_selected_l:
            mako_input += ', ' + indc
        mako_input += '\n'
        # building the body
        indc_by_prod = {}
        for prod in g.p5_all_products_to_be_processed_set:
            indc_by_prod[prod] = {}
        for indc_c in p7_indcs_from_contract_l:  # loop over the big one once
            if indc_c['what'] in already_selected_l:  # loop over the smaller more
                indc_by_prod[indc_c['prod_nr']][indc_c['what']] = indc_c['info']
        idx = 0
        for prod in indc_by_prod.keys():
            mako_input += str(idx)
            mako_input += ', ' + prod
            for k in indc_by_prod[prod].keys():
                mako_input += ', ' + str(indc_by_prod[prod][k])
                mako_input += '\n'
                idx += 1

        with open('mako_input.csv', 'w') as f:
            f.write(mako_input)


def display():
    dirs = read_dirs()
    print('~~~')
    for dr in dirs:
        print(dr)
    print('~~~')


def update():
    select_existing_o_non_existing_menu_for_exec_help_function(create_exec_function, False)


def delete():
    select_existing_o_non_existing_menu_for_exec_help_function(delete_exec_function, True)


# def select_a_new_label_group_n_save():
#     select_existing_o_non_existing_menu_for_exec_help_function(g.write_in_mem_n_on_disk, True)

def create_selected_indicators_set():
    pass


def p7_display_selected_indicators():
    with open(os.path.join('..', 'p4_' + g.p1_contract_nr + '_indics_from_contract_l.json')) as f:
        p7_indics_from_contract_l = json.load(f)
    indic_val_d = {}
    for option in options_l:
        temp_d = {}
        for indic in p7_indics_from_contract_l:
            if indic['what'] == option:
                temp_d[indic['prod_nr']] = indic['info']
        indic_val_d[option] = temp_d

    for option in options_l:
        nr_tabs = 1 if len(option) >= 8 else 2
        print(option, nr_tabs * '\t', list(indic_val_d[option].values()))
    print('\nAlready selected: ', already_selected_l, '\n')
    print('Currently in: ', os.path.relpath(os.getcwd(), os.getcwd() + '..'))
    # m.display_context_in_most_cases()


def create_exec_function():
    if not os.path.exists(g.p6_lbl_dir):
        os.mkdir(g.p6_lbl_dir, mode = 0o700)
    # and transfer the label_templates there
    if not os.path.exists(os.path.join(g.p6_lbl_dir, 'label_template_header.svg')):
        shutil.copy(os.path.join(g.p1_root_dir + '/common/1.Outer_box_外箱', 'label_template_header.svg'),
                    g.p6_lbl_dir)
    if not os.path.exists(os.path.join(g.p6_lbl_dir, 'label_template_body.svg')):
        shutil.copy(os.path.join(g.p1_root_dir + '/common/1.Outer_box_外箱', 'label_template_body.svg'),
                    g.p6_lbl_dir)


def delete_exec_function():
    if os.path.isdir(g.p6_lbl_dir):
        shutil.rmtree(g.p6_lbl_dir)


def chdir_exec_function():
    if os.path.isdir(g.p6_lbl_dir):
        os.chdir(g.p6_lbl_dir)
    print(f'Now in {os.getcwd()} ')


def read_dirs():
    (root, dirs, files) = next(os.walk(g.p1_contract_dir))
    dirs.sort()
    return dirs


def cd_to_selected_dir():
    chdir_exec_function()
    # select_existing_o_non_existing_menu_for_exec_help_function(chdir_exec_function, True)


def select_existing_o_non_existing_menu_for_exec_help_function(exec_function, in_o_out):
    assert in_o_out == in_o_out
    assert exec_function == exec_function
    pass
    """
    label_groups = ['1.Outer_box_外箱',
                    '2.Inner_box_内盒',
                    '3.Inside_box_中箱',
                    '4.Prod_packaging_产品包装',
                    '5.Plastic_bag_塑料袋',
                    '6.Prod_sticker_产品上不干胶',
                    ]

    # function factory
    # defining what each label function should be doing
    def make_f(group):  # positional argument has no number
        def func():
            group_dir = ''
            for n_group in label_groups:
                if group in n_group:
                    group_dir = n_group
            g.p6_lbl_dir = os.path.join(g.p1_contract_dir, group_dir)
            exec_function()
            m.menu = menu
            m.menus = menus

        func.__name__ = group  # as function is not read before being called for execution

        return func

    functions_d = {}
    for label_group in label_groups:
        functions_d[label_group[2:]] = make_f(label_group[2:])

    def back():
        m.menu = menu
        m.menus = menus

    assert back == back

    m.menu = 'Select label to add'
    m.menus = {m.menu: {}}
    for label_group in label_groups:
        dir_l = read_dirs()
        if label_group in dir_l if in_o_out else label_group not in dir_l:
            m.menus[m.menu][label_group[0]] = functions_d[label_group[2:]]
    m.menus[m.menu]['m'] = eval('back')
    # a particular case of run to present the current situation in p6: listing existing / non existing directories
    # m.run(p6_display_existing_non_existing_dirs)
    """


def p6_display_existing_non_existing_dirs():
    display()

    selected_lbl = g.p6_lbl_dir[g.p6_lbl_dir.rfind('/'):]
    current_dir_fp = os.getcwd()
    current_dir_lcl = current_dir_fp[current_dir_fp.rfind('/'):]
    print(f'Selected label: {selected_lbl}, currently in {current_dir_lcl}')


def create_label_dirs(drs_l):
    # if directories do not exist, create them
    for dr in drs_l:
        p6_lbl_dir = os.path.join(g.p1_contract_dir, dr)
        if not os.path.exists(p6_lbl_dir):
            os.mkdir(p6_lbl_dir, mode = 0o700)
        # and transfer the label_templates there
        if not os.path.exists(os.path.join(p6_lbl_dir, 'label_template_header.svg')):
            shutil.copy(os.path.join(g.p1_root_dir + '/common/1.Outer_box_外箱',
                                     'label_template_header.svg'), p6_lbl_dir)
        if not os.path.exists(os.path.join(p6_lbl_dir, 'label_template_body.svg')):
            shutil.copy(os.path.join(g.p1_root_dir + '/common/1.Outer_box_外箱',
                                     'label_template_body.svg'), p6_lbl_dir)

        # create canonical p6_lbl_dir and p6_lbl_sel
        write_in_mem_n_on_disk(dr)


def write_in_mem_n_on_disk(p6_lbl_dir):
    # document the info in A1234-567_labels-info.json file
    g.p2_labels_info_d['p6_lbl_dir'] = p6_lbl_dir
    _, p6_lbl_sel = os.path.split(p6_lbl_dir)
    g.p2_labels_info_d['p6_lbl_sel'] = p6_lbl_sel
    with open(g.p2_labels_info_f, 'w') as fi:
        json.dump(g.p2_labels_info_d, fi, ensure_ascii = False)


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
