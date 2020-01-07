#!/usr/bin/env python3
import json
import os
import pprint
import p0_menus as p
import p1_select_contract as p1
import p2_select_labels as p2

p0_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located
already_selected_l = []
header_height = 7
page_view_box_w = 170
page_view_box_h = 257
options_l = []
p3_fields_dir = ''  # currently working fields directory
p3_fields_sel = ''  # current label
p3_fields_info_d = {}  # info on fields currently being edited
p3_fields_info_f = None  # info on fields currently being edited


def p3_select_specific_fields_context_func():
    print('~~~ Now processing contract #: ', p1.p1_contract_nr if p1.p1_contract_nr else None)
    print('~~~ Selecting specific fields for labels as follows:\n')
    p1.display_dirs(p1.p1_contract_dir)
    print('\n>>> Select action: ')


context_func_d = {
    'select_specific_fields': p3_select_specific_fields_context_func,
}


def init():
    # make sure p1 infrastructure is in place
    if not p1.p1_load_contract_info_d():
        print('p1 has not run successfully')
    if not p1.read_dirs(p1.p1_contract_dir):
        p2.create_default_labels()

    # initializing menus last, so that context functions display most recent information
    menu = 'select_specific_fields'
    p.menu = menu
    menus = {
        menu: {
            '1': process_all_labels_with_default_specific_fields,
            '2': display_or_load_output_overview,
            '3': select_a_label_and_add_fields,
            '4': select_a_label_and_delete_fields,
            '6': p1.display_p1_contract_info_d,
            '7': p1.display_p1_contract_info_f,
            '8': display_p3_fields_info_d,
            '9': display_p3_fields_info_f,
            '11': p3_load_fields_info_d,
            'p': p.back_to_main,
            'q': p.normal_exit,
        }
    }
    p.menus = menus

    global options_l
    options_l = []
    global already_selected_l
    if load_p3_fields_info_d():
        already_selected_l = p3_fields_info_d['selected_fields']
    else:
        already_selected_l = []
        print('\nNo specific fields selected at this point\n')

    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}


def process_all_labels_with_default_specific_fields():
    pass


def display_or_load_output_overview():
    pass


def select_a_label_and_add_fields():
    global p3_fields_dir

    # read existing labels
    drs = p1.read_dirs(p1.p1_contract_dir)
    if drs:
        print(f'~~~ Now processing contract #: {p1.p1_contract_nr}')
        print('>>> Select label to edit:\n')
        for i in range(len(drs)):
            print(str(i) + '. ' + drs[i][2:])
        while True:
            s = input('\nEnter nr of directory to delete_all_data_on_selected_contract, \'b\' to return : ')
            if s == 'b':
                os.system('clear')
                break
            else:
                try:
                    s_i = int(s)
                    if s_i in range(len(drs)):
                        os.system('clear')
                        p3_fields_dir = drs[s_i]
                        print(f'now ready to work on {p3_fields_dir}')
                        create_or_update()
                        break
                    else:
                        print('Integer, but not an option, try again')
                except ValueError:
                    print('That\'s not an integer, try again')
    else:
        return


def select_a_label_and_delete_fields():
    pass


def p3_display_selected_fields():
    with open(os.path.join(p1.p1_contract_dir, 'p4_' + p1.p1_contract_nr + '_fields_from_contract_l.json')) as f:
        p3_fields_from_contract_l = json.load(f)
    indic_val_d = {}
    for option in options_l:
        temp_d = {}
        for indic in p3_fields_from_contract_l:
            if indic['what'] == option:
                temp_d[indic['prod_nr']] = indic['info']
        indic_val_d[option] = temp_d

    for option in options_l:
        nr_tabs = 1 if len(option) >= 8 else 2
        print(option, nr_tabs * '\t', list(indic_val_d[option].values()))
    print('\nAlready selected: ', already_selected_l, '\n')
    print('Currently processing ', p3_fields_dir)


def load_p3_fields_info_d():
    pass


def display_p3_fields_info_d():
    global p3_fields_info_d
    print('~~~ Reading label-info global value ~~~')
    pprint.pprint(p3_fields_info_d)
    print(p3_fields_info_d)
    print('~~~ Finished reading label-info global value ~~~')


def display_p3_fields_info_f():
    global p3_fields_info_f

    if p3_fields_info_d:
        if os.path.isfile(p3_fields_info_f):
            print('~~~ Reading label-info.json file contents ~~~')
            with open(p3_fields_info_f) as f:
                pprint.pprint(f.read())
            print('~~~ File label-info.json closed ~~~')
    else:
        print(f'\nFile {p3_fields_info_f} not built yet\n')


def create():
    create_or_update()


def update():
    create_or_update(False)


def create_or_update(default = True):
    global already_selected_l
    global options_l

    if p3_load_fields_info_d():
        already_selected_l = p3_fields_info_d['selected_fields']

    if default and not already_selected_l:
        already_selected_l = ["03.Prod_spec", "pack", "total_qty"]

    # process default contract selected fields set
    if not default:
        p3_select_specific_fields_context_func()
        with open(os.path.join(p1.p1_contract_dir, p3_fields_info_d['p3_extract_specifics'])) as fj:
            p1.p1e_specific_fields_d_of_d = json.load(fj)
        options_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))
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

    p3_fields_info_d['selected_fields'] = already_selected_l

    global p3_fields_info_f
    p3_fields_info_f = os.path.join(p1.p1_contract_dir + '/' + p3_fields_dir, 'label-info.json')
    with open(p3_fields_info_f, 'w') as f:
        json.dump(p3_fields_info_d, f, ensure_ascii = False)

    make_mako()


def make_mako():
    # writing the input file for Mako
    mako_input = ''
    with open(os.path.join(p1.p1_contract_dir, 'p1b_' + p1.p1_contract_nr + '_indics_from_contract_l.json')) as f:
        p3_indcs_from_contract_l = json.load(f)  # todo: replace by mem pointer if it exists
    if already_selected_l:
        # building the header
        mako_input += 'idx, prod_n'
        for indc in already_selected_l:
            mako_input += ', ' + indc
        mako_input += '\n'
        # building the body
        indc_by_prod = {}
        for prod in p1.p1_all_products_to_be_processed_set:
            indc_by_prod[prod] = {}
        for indc_c in p3_indcs_from_contract_l:  # loop over the big one once
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


def p3_load_fields_info_d():
    global p3_fields_info_f
    global p3_fields_info_d
    global p3_fields_dir

    if p3_fields_dir:
        p3_fields_info_f = os.path.join(p3_fields_dir, 'label-info.json')
        if os.path.exists(p3_fields_dir):
            with open(p3_fields_info_f) as f:
                p3_fields_info_d = json.load(f)
                if p3_fields_info_d:
                    return True
    return False


"""
def write_in_mem_n_on_disk(p3_fields_dir):
    # document the info in A1234-567_fields-info.json file
    p3_fields_info_d['p3_fields_dir'] = p3_fields_dir
    _, p3_fields_sel = os.path.split(p3_fields_dir)
    p3_fields_info_d['p3_fields_sel'] = p3_fields_sel
    with open(p3_fields_info_f, 'w') as fi:
        json.dump(p3_fields_info_d, fi, ensure_ascii = False)
"""


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
