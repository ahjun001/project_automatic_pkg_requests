#!/usr/bin/env python3
import json
import os
import pprint
import p0_menus as p
import p1_select_contract as p1
import p2_select_labels as p2

p0_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located
p3_already_selected_l = []
p3_options_l = []
p3_fields_dir = ''  # currently working fields directory
p3_fields_sel = ''  # current label
p3_fields_info_d = {}  # info on fields currently being edited
p3_fields_info_f = None  # info on fields currently being edited
p3_default_fields = ["03.Prod_spec", "total_qty", "pack", "u_parc"]
header_height = 7
page_view_box_w = 170
page_view_box_h = 257


def p3_select_specific_fields_context_func():
    print('~~~ Now processing contract #: ', p1.p1_contract_nr if p1.p1_contract_nr else None)
    print('~~~ Now working on label: ', p3_fields_dir)
    print('~~~ Specific fields selected so far:', p3_already_selected_l)
    print('\n>>> Select an action: ')


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
            '3': select_a_label,
            '4': display_specific_fields_for_all_products,
            '7': p1.display_p1_contract_info_d,
            '8': p1.display_p1_contract_info_f,
            '9': display_p3_fields_info_d,
            '10': display_p3_fields_info_f,
            '11': p3_load_fields_info_d,
            'b': p.back_to_main,
            'q': p.normal_exit,
        }
    }
    p.menus = menus

    global p3_options_l
    p3_options_l = []
    global p3_already_selected_l
    if p3_load_fields_info_d():
        p3_already_selected_l = p3_fields_info_d['selected_fields']
    else:
        p3_already_selected_l = []
        print('\nNo specific fields selected at this point\n')

    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}


def process_all_labels_with_default_specific_fields():
    global p3_fields_dir
    global p3_already_selected_l
    global p3_fields_info_d
    global p3_options_l
    global p3_fields_info_f

    # p3_select_specific_fields_context_func()
    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d()
    p3_options_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))

    # read existing labels
    drs = p2.p2_load_labels_info_l()
    if drs:
        for p3_fields_dir in drs:
            if p3_load_fields_info_d():
                p3_already_selected_l = p3_fields_info_d['selected_fields']
            for f in p3_default_fields:
                if f in p3_options_l and f not in p3_already_selected_l:
                    p3_already_selected_l.append(f)
            p3_fields_info_f = os.path.join(p1.p1_contract_dir + '/' + p3_fields_dir, 'label-info.json')
            with open(p3_fields_info_f, 'w') as f:
                json.dump(p3_fields_info_d, f, ensure_ascii = False)
            make_mako(p3_fields_dir)


def display_or_load_output_overview():
    pass


def select_a_label():
    global p3_fields_dir
    global p3_already_selected_l

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
                        # load fields already selected for label as they are on file
                        if p3_load_fields_info_d():
                            p3_already_selected_l = p3_fields_info_d['selected_fields']
                        print(f'now ready to work on {p3_fields_dir}')
                        while True:
                            p3_select_specific_fields_context_func()
                            s = input('\'a\' to add a field\n'
                                      '\'d\' to delete a field\n'
                                      '\'b\' to go back\n'
                                      '~~~\n')
                            if s == 'b':
                                os.system('clear')
                                break
                            elif s == 'a':
                                add_fields()
                            elif s == 'd':
                                del_fields()
                            else:
                                print(f'{s} is not an option, try again')
                        break
                    else:
                        print('!\n! Integer, but not an option, try again\n!')
                except ValueError:
                    print('!\n! That\'s not an integer, try again\n!')

        write_to_disk()
        make_mako(p3_fields_dir)
    else:
        return


def write_to_disk():
    global p3_fields_info_f
    global p3_fields_info_d

    p3_fields_info_d['selected_fields'] = p3_already_selected_l
    p3_fields_info_f = os.path.join(p1.p1_contract_dir + '/' + p3_fields_dir, 'label-info.json')
    with open(p3_fields_info_f, 'w') as f:
        json.dump(p3_fields_info_d, f, ensure_ascii = False)


def p3_display_selected_fields():
    with open(os.path.join(p1.p1_contract_dir, 'p4_' + p1.p1_contract_nr + '_fields_from_contract_l.json')) as f:
        p3_fields_from_contract_l = json.load(f)
    indic_val_d = {}
    for option in p3_options_l:
        temp_d = {}
        for indic in p3_fields_from_contract_l:
            if indic['what'] == option:
                temp_d[indic['prod_nr']] = indic['info']
        indic_val_d[option] = temp_d

    for option in p3_options_l:
        nr_tabs = 1 if len(option) >= 8 else 2
        print(option, nr_tabs * '\t', list(indic_val_d[option].values()))
    print('\nAlready selected: ', p3_already_selected_l, '\n')
    print('Currently processing ', p3_fields_dir)


def display_p3_fields_info_d():
    global p3_fields_info_d
    print('~~~ Reading label-info global value ~~~')
    pprint.pprint(p3_fields_info_d)
    print(p3_fields_info_d)
    print('~~~ Finished reading label-info global value ~~~')


def display_p3_fields_info_f():
    global p3_fields_info_f

    if p3_fields_info_d:
        if os.path.exists(p3_fields_info_f):
            print('~~~ Reading label-info.json file contents ~~~')
            with open(p3_fields_info_f) as f:
                pprint.pprint(f.read())
            print('~~~ File label-info.json closed ~~~')
    else:
        print(f'\nFile {p3_fields_info_f} not built yet\n')


def add_fields():
    global p3_fields_info_f
    global p3_fields_dir
    global p3_already_selected_l
    global p3_options_l

    # if not p3_already_selected_l:
    #     p3_already_selected_l = ["03.Prod_spec", "pack", "total_qty"]

    # p3_select_specific_fields_context_func()
    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d()
    p3_options_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))
    # select from p3_options_l and put in p3_already_selected_l
    while True:
        print(f'~~~ Already selected:\n{p3_already_selected_l}\n~~~ Can be added:')
        not_yet_l = []
        for o in p3_options_l:
            if o not in p3_already_selected_l:
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
                    p3_already_selected_l.append(not_yet_l[s_i])
                    # break
                else:
                    print('!\n! Integer, but not an option, try again\n!')
            except ValueError:
                print('!\n! That\'s not an integer, try again\n!')
    write_to_disk()


def del_fields():
    global p3_already_selected_l
    global p3_fields_info_f
    global p3_fields_info_d

    while True:
        print(f'~~~ Already selected:')
        for i in range(len(p3_already_selected_l)):
            print(f'{i}. {p3_already_selected_l[i]}')
        print(f'~~~')
        s = input('Enter nr of indicator to delete, \'b\' to return : ')
        if s == 'b':
            os.system('clear')
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(p3_already_selected_l)):
                    del p3_already_selected_l[s_i]
                    # break
                else:
                    print('!\n! Integer, but not an option, try again\n!')
            except ValueError:
                print('!\n! That\'s not an integer, try again\n!')

    write_to_disk()


def make_mako(dr):
    global p3_already_selected_l

    # writing the input file for Mako
    mako_input = ''

    # make sure global variables are set in all situations, outside the loop to do it once only
    if not p1.p1b_indics_from_contract_l:
        p1.load_p1b_indics_from_contract_l()
    if not p1.p1_all_products_to_be_processed_set:
        p1.load_p1_all_products_to_be_processed_set()

    if p3_already_selected_l:
        # building the header
        mako_input += 'idx, prod_n'
        for indc in p3_already_selected_l:
            mako_input += ', ' + indc
        mako_input += '\n'
        # building the body
        indc_by_prod = {}
        for prod in p1.p1_all_products_to_be_processed_set:
            indc_by_prod[prod] = {}
        for indc_c in p1.p1b_indics_from_contract_l:  # loop over the big one once
            if indc_c['what'] in p3_already_selected_l:  # loop over the smaller more
                indc_by_prod[indc_c['prod_nr']][indc_c['what']] = indc_c['info']
        idx = 0
        for prod in indc_by_prod.keys():
            mako_input += str(idx)
            mako_input += ', ' + prod
            for k in indc_by_prod[prod].keys():
                mako_input += ', ' + str(indc_by_prod[prod][k])
            mako_input += '\n'
            idx += 1

        with open(os.path.join(p1.p1_contract_dir + '/' + dr, 'mako_input.csv'), 'w') as f:
            f.write(mako_input)


def p3_load_fields_info_d():
    """
    if information is already in memory, do not reload it, returns True
    else load from disk
    """
    global p3_fields_info_f
    global p3_fields_info_d
    global p3_fields_dir

    if p3_fields_info_d:
        return True
    if p3_fields_dir:
        p3_fields_info_f = os.path.join(p1.p1_contract_dir + '/' + p3_fields_dir, 'label-info.json')
        if os.path.exists(p3_fields_info_f):
            with open(p3_fields_info_f) as f:
                p3_fields_info_d = json.load(f)
                if p3_fields_info_d:
                    return True
    return False


def display_specific_fields_for_all_products():
    # make sure global variables are set in all situations, outside the loop to do it once only
    if not p1.p1_all_products_to_be_processed_set:
        p1.load_p1_all_products_to_be_processed_set()
    if not p1.p1b_indics_from_contract_l:
        p1.load_p1b_indics_from_contract_l()

    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d()
    p1e_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))

    # building the header
    tmp_l = [8*' ']
    for f in p1e_l:
        tmp_l.append(f)
    dsp_l = [tmp_l]

    # building the body
    spec_by_prod = {}
    for prod in p1.p1_all_products_to_be_processed_set:
        spec_by_prod[prod] = {}
    for d in p1.p1b_indics_from_contract_l:
        if d['what'] in p1e_l:
            spec_by_prod[d['prod_nr']][d['what']] = d['info']

    for prod in spec_by_prod.keys():
        tmp_l = [prod]
        for k in spec_by_prod[prod].keys():
            tmp_l.append(spec_by_prod[prod][k])
        dsp_l.append(tmp_l)

    m = 0
    for l_l in dsp_l:
        for ls in l_l:
            m = max(m, len(str(ls)))
    s = ''
    for l_l in dsp_l:
        for ls in l_l:
            s += (m - len(str(ls))) * ' ' + str(ls)
        s += '\n'
    print(s)


def good_by_not_pretty_display_specific_fields_for_all_products():
    # writing for dsp_sf
    dsp_p = ''

    # make sure global variables are set in all situations, outside the loop to do it once only
    if not p1.p1_all_products_to_be_processed_set:
        p1.load_p1_all_products_to_be_processed_set()
    if not p1.p1b_indics_from_contract_l:
        p1.load_p1b_indics_from_contract_l()

    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d()
    p1e_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))

    # building the header
    for f in p1e_l:
        dsp_p += f'\t{f}'
    dsp_p += '\n'
    # building the body
    spec_by_prod = {}

    for prod in p1.p1_all_products_to_be_processed_set:
        spec_by_prod[prod] = {}
    for d in p1.p1b_indics_from_contract_l:
        if d['what'] in p1e_l:
            spec_by_prod[d['prod_nr']][d['what']] = d['info']

    for prod in spec_by_prod.keys():
        dsp_p += '\t' + prod
        for k in spec_by_prod[prod].keys():
            dsp_p += '\t' + str(spec_by_prod[prod][k])
        dsp_p += '\n'

    print(dsp_p)


def inverted_display_specific_fields_for_all_products():
    # writing for dsp_sf
    dsp_s = ''

    # make sure global variables are set in all situations, outside the loop to do it once only
    if not p1.p1b_indics_from_contract_l:
        p1.load_p1b_indics_from_contract_l()
    if not p1.p1_all_products_to_be_processed_set:
        p1.load_p1_all_products_to_be_processed_set()

    # building the header
    dsp_s += 'field'
    for f in p1.p1_all_products_to_be_processed_set:
        dsp_s += f'\t{f}'
    dsp_s += '\n'
    # building the body
    prod_by_spec = {}
    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d()
    p1e_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))
    for spec in p1e_l:
        prod_by_spec[spec] = {}
    for d in p1.p1b_indics_from_contract_l:
        if d['what'] in p1e_l:
            prod_by_spec[d['what']][d['prod_nr']] = d['info']

    idx = 0
    for spec in prod_by_spec.keys():
        dsp_s += str(idx)
        dsp_s += '\t' + spec
        for k in prod_by_spec[spec].keys():
            dsp_s += '\t' + str(prod_by_spec[spec][k])
        dsp_s += '\n'
        idx += 1

    print(dsp_s)


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
