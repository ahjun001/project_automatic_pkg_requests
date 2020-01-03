#!/usr/bin/env python3
# p2_select_label_kinds_n_print.py
import json
import os
import shutil

import p1_set_up_full_dir_struct_n_process_info as p1
import u_global_values as g
import py_menus as p


def proc_2_context():
    print('~~~ Context p6 set up label dirs n infos ~~~')
    g.display_dirs('.')


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
    create_or_update()


def update():
    create_or_update(False)


def delete():
    pass


def create_or_update(default = True):
    global already_selected_l
    global options_l
    global p7_specific_indics_d_of_d

    drs = g.read_dirs(g.p1_contract_dir)
    if not drs:
        create_label_dirs(g.standard_labels_l)
    # documenting in memory but not on disk, so as to keep the option of editing out of program
    # then p2_labels_info_d and p2_labels_info_f will look different
    # g.p2_labels_info_d['p6_label_l'] = g.read_dirs(g.p1_contract_dir)

    # create canonical p6_lbl_dir and p6_lbl_sel
    for dr in drs:
        os.chdir(g.p1_contract_dir + '/' + dr)
        g.p6_lbl_sel = dr
        g.p6_lbl_dir = os.path.join(g.p1_contract_dir, g.p6_lbl_sel)
        # g.write_in_mem_n_on_disk()
        if g.chdir_n_p7_read():
            already_selected_l = g.p7_label_info_d['selected_indicators']

        if default and not already_selected_l:
            already_selected_l = ["03.Prod_spec", "pack", "total_qty"]

        # create selected indicators set
        if not default:
            proc_2_context()
            with open(os.path.join(g.p1_contract_dir, g.p2_labels_info_d['p6_extract_specifics'])) as fj:
                p7_specific_indics_d_of_d = json.load(fj)
            options_l = list(next(iter(p7_specific_indics_d_of_d.values())))
            # select from options_l and put in already_selected_l
            while True:
                print(f'~~~ already selected ~~~\n{already_selected_l}\n~~~~~~')
                not_yet_l = []
                for o in options_l:
                    if o not in already_selected_l:
                        not_yet_l.append(o)
                for i in range(len(not_yet_l)):
                    print(str(i) + ' ' + not_yet_l[i])
                print('~~~')
                s = input('Enter nr of indicator to add, \'b\' to return : ')
                if s == 'b':
                    os.system('clear')
                    break
                else:
                    try:
                        s_i = int(s)
                        if s_i in range(len(not_yet_l)):
                            already_selected_l.append(not_yet_l[s_i])
                            # break
                        else:
                            print('Integer, but not an option, try again')
                    except ValueError:
                        print('That\'s not an integer, try again')

        g.p7_label_info_d['selected_indicators'] = already_selected_l

        with open(g.p7_label_info_f, 'w') as f:
            json.dump(g.p7_label_info_d, f, ensure_ascii = False)

        make_mako()


def display():
    print('~~~')
    g.display_dirs(g.p1_contract_dir)
    print('~~~')


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


# def select_a_new_label_group_n_save():
#     select_existing_o_non_existing_menu_for_exec_help_function(g.write_in_mem_n_on_disk, True)

def create_selected_indicators_set():
    pass


def p7_display_selected_indicators():
    """
    os.chdir(g.p1_contract_dir)
    if g.chdir_n_p7_read():
        already_selected_l = g.p7_label_info_d['selected_indicators']
    """

    with open(os.path.join(g.p1_contract_dir, 'p4_' + g.p1_contract_nr + '_indics_from_contract_l.json')) as f:
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



def chdir_exec_function():
    if os.path.isdir(g.p6_lbl_dir):
        os.chdir(g.p6_lbl_dir)
    print(f'Now in {os.getcwd()} ')


def cd_to_selected_dir():
    chdir_exec_function()
    # select_existing_o_non_existing_menu_for_exec_help_function(chdir_exec_function, True)


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
