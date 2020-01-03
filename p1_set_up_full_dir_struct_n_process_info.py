#!/usr/bin/env python3
# p1_set_up_full_dir_struct_n_process_info.py
import csv
import json
import os
import pathlib
import pprint
import re
import shutil
import sys
from tkinter.filedialog import askopenfilename

import xlrd

import u_global_values as g
import py_menus as p


def report_selected_file_is_not_xls(filename):
    print(f'\nSelected file {filename} extension is not \'.xls\'\n')


def p_context():
    print('~~~ Context for p1 set up dir struct n contract xls select n chdir ~~~')
    g.display_dirs('.')


def display_1_context():
    print('~~~ Context for p1 display ~~~')
    g.display_dirs('.')


context_func_d = {
    'p1_set_up_dir_struct_n_contract_xls_select_n_chdir': p_context,
    'display': display_1_context,
}


def init():
    p.menu = 'p1_set_up_dir_struct_n_contract_xls_select_n_chdir'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': create,
            '2': display,
            '3': update,
            '4': delete,
            '8': g.display_p1_program_info_d,
            '9': g.display_p1_program_info_f,
            'm': p.back_to_main,
            'q': p.normal_exit,
        },
        'display': {
            '2': g.display_dirs,
            '6': display_p4_search_reg_ex_l,
            '7': display_p4_indics_from_contract_l,
            '8': display_p5_prods_w_same_key_set,
            '9': display_p5_all_products_to_be_processed_set,
            '10': display_p6_common_indics_l,
            '11': display_p6_specific_indics_d_of_d,
            '12': g.display_p2_labels_info_d,
            '13': g.display_p2_labels_info_f,
            'b': p.back,
            'q': p.normal_exit,
        }
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}

    os.chdir('./data/')


# If the data directory does not exist, create it
data_dir = os.path.join(g.p1_root_dir, 'data')
if not os.path.exists(data_dir):
    os.mkdir(data_dir, mode = 0o700)
g.p1_read()
p4_search_reg_ex_l = []
p4_indics_from_contract_l = []
p5_prods_w_same_key_set = {}  # make a dictionary key= info, value = sets of prods with that key
p5_all_products_to_be_processed_set = set()
p6_common_indics_l = []
p6_specific_indics_d_of_d = {}
indicators_csv = os.path.join(g.p1_root_dir + '/common', 'indicators.csv')


# rel_path_contract_json_f = ''  # will be initialized when p1_contract_nr is set


def create():
    # checking if a program-info.json file exists in the root directory
    g.p1_program_info_f = os.path.join(g.p1_root_dir, 'program-info.json')
    # if program-info.json exists
    if pathlib.Path(g.p1_program_info_f).exists():
        # then load the info it contains in g.p1_program_info_d dictionary
        with open(g.p1_program_info_f) as f:
            g.p1_program_info_d = json.load(f)
        # check if p1_program_info_d['p1_contract_nr'] helps point to a valid file,
        if g.p1_program_info_d:
            # then check if this one could be working data
            if 'p1_contract_nr' in g.p1_program_info_d:
                g.p1_contract_dir = g.p1_root_dir + f'/data/{g.p1_program_info_d["p1_contract_nr"]}'
                _, result = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(g.p1_contract_dir, '.xls')
                if result:
                    # create_a_new_label_kind all global variables accordingly
                    g.p1_full_path_source_file_xls = result
                    g.p1_contract_nr = g.p1_program_info_d["p1_contract_nr"]
                # if the data from p1_program_info_d cannot be used
                else:
                    # if a valid initial file exists but is not uniquely copied in the repertory
                    if 'p1_initial_xls' in g.p1_program_info_d:
                        if not os.path.exists(g.p1_contract_dir):
                            os.mkdir(g.p1_contract_dir, mode = 0o700)
                        g.p1_initial_xls_contract_file = g.p1_program_info_d['p1_initial_xls']
                        shutil.copy(g.p1_initial_xls_contract_file, g.p1_contract_dir)
                    else:
                        # cannot do much else with this info, abandon and start-over
                        del g.p1_program_info_d['p1_contract_nr']
                        build_program_info_d_from_root_xls_file_or_ask_open_file()
        # if program-info.json doesn't point to a valid ./data/p1_contract_nr and xls file, then rebuild
        else:
            build_program_info_d_from_root_xls_file_or_ask_open_file()
    # if program-info.json does not exist
    else:
        build_program_info_d_from_root_xls_file_or_ask_open_file()

    # p1_contract_nr is now set
    os.chdir(g.p1_contract_dir)
    print(f'Current working dir is now {os.getcwd()}')
    # the name of the -contract.json file can now be set
    rel_path_contract_json_f = 'p2_' + g.p1_contract_nr + '-contract.json'

    # Creating the json file from the local xls file: opening the xl file
    book = xlrd.open_workbook(g.p1_full_path_source_file_xls)
    sheet = book.sheet_by_index(0)

    row = 0
    while not sheet.col_values(0, 0)[row]:  # getting to last row before D1 in col. A
        row += 1

    # get global info
    if sheet.cell(1, 7).value[0:4] == '合同编号':
        contract_json_d = {'合同编号': sheet.cell(1, 7).value[5:].strip()}  # select data from cell 'H2'
    else:
        sys.exit("Error reading contract XLS file:  expecting to select 合同编号 in cell 'H2'")

    non_decimal = re.compile(r'[^\d.]+')  # necessary to clean formatting characters in XLS cells

    contract_json_d['l_i'] = []
    while sheet.col_values(0, 0)[row]:  # looping while there is product information available
        prod_n = sheet.cell(row, 1).value  # correcting XL showing an int but passing a float,
        # all prod # are not numbers
        if isinstance(prod_n, float):
            prod_n = str(int(prod_n))
        tmp_dict = {  # use to be OrderedDict for human readability, not necessary for program
            "01.TST_prod_#-需方产品编号": prod_n,
            "02.Sup_prod_#-供方产品编号": sheet.cell(row, 2).value,
            "03.Prod_spec-产品规格": sheet.cell(row, 3).value,
            "04.Prod_name-产品名称": sheet.cell(row, 4).value,
            "05.Quantity-数量": sheet.cell(row, 5).value,
            "06.Units-单位": sheet.cell(row, 6).value,
            "07.Unit_price-单价": float(non_decimal.sub('', sheet.cell(row, 7).value[3:])),
            "08.Total_price-全额": float(non_decimal.sub('', sheet.cell(row, 8).value[3:])),
            "09.Tech_spec-技术参数_1": sheet.cell(row + 1, 2).value,
            "10.Tech_spec-技术参数_2": sheet.cell(row + 1, 7).value,
            "11.Pack_spec-包装要求": sheet.cell(row + 2, 2).value
        }
        contract_json_d['l_i'].append(dict(tmp_dict))
        row += 3

    with open(rel_path_contract_json_f, 'w') as fc:
        json.dump(contract_json_d, fc, ensure_ascii = False)
    # document in A1234-456-info.json
    g.p2_labels_info_f = 'p2_' + g.p1_contract_nr + '_labels-info.json'
    # create a structure to store label information
    g.p2_labels_info_d = {'p2_contract_json': rel_path_contract_json_f}
    with open(g.p2_labels_info_f, 'w') as fi:
        json.dump(g.p2_labels_info_d, fi, ensure_ascii = False)

    # def create_2():
    # reading info from ./common/indicators.csv, which was kept in csv format to make human input easier
    with open(indicators_csv) as f:
        my_dict_reader = csv.DictReader(f)
        for row in my_dict_reader:
            temp_dict = dict(row)
            p4_search_reg_ex_l.append(temp_dict)

    # p4_indics_from_contract_l: harvesting all indicators possibly available in the contract_json_d
    for row_indic in p4_search_reg_ex_l:
        what = row_indic['what']
        info_kind = row_indic['info_kind']
        how = row_indic['how']
        for prod in contract_json_d['l_i']:  # inspecting products one by one
            tmp_dct = {  # adding 03.Prod_spec-产品规则 info
                'info_kind': 'spec',
                'what': '03.Prod_spec',
                'where': '05.Quantity-数量',
                'prod_nr': prod['01.TST_prod_#-需方产品编号'],
                'info': prod["03.Prod_spec-产品规格"]
            }
            p4_indics_from_contract_l.append(tmp_dct)
            tmp_dct = {  # adding 05.Quantity-数量 info
                'info_kind': 'pack_qty',
                'what': 'total_qty',
                'where': '05.Quantity-数量',
                'prod_nr': prod['01.TST_prod_#-需方产品编号'],
                'info': int(prod['05.Quantity-数量'])
            }
            p4_indics_from_contract_l.append(tmp_dct)
            for key, value in prod.items():  # looping over each xl field, searching its value
                if isinstance(value, str):  # ignore 05.Qty, 07.Unit_price, and 08.Total_price
                    s_tmp = re.findall(how, value)
                    if s_tmp:  # if this test succeeds then info must be registered
                        srch = []
                        for s in s_tmp:
                            srch.append(s.strip())  # strip the search result
                        for indication in srch:
                            tmp_dct = {
                                'info_kind': info_kind,  # from indicators.csv: pack_qty, logo, spec, pack_spec
                                'what': what,  # from indicators.csv : pack, kg, mm, 牌, v_Hz, plstc_bg
                                'where': key,  # xl cell: 10.Tech_spec-技术参数_2
                                'info': indication,  # 1.00    = indic
                                'prod_nr': prod["01.TST_prod_#-需方产品编号"],  # 1050205001#
                            }
                            p4_indics_from_contract_l.append(tmp_dct)
        p4_indics_from_contract_l.sort(key = lambda item: item['prod_nr'])
        file_indics = 'p4_' + g.p1_contract_nr + '_indics_from_contract_l.json'

        # register in file and object
        document_in_labels_info_json('p4_indics_from_contract_l', file_indics)

        with open(file_indics, 'w') as f:
            json.dump(p4_indics_from_contract_l, f, ensure_ascii = False)

        # p5_prods_w_same_key_set = {}  # make a dictionary key= info, value = sets of prods with that key
        for row in p4_indics_from_contract_l:
            # for index, row in c_df.iterrows():  # index is not used
            if (row['info_kind'], row['what'], row['where'], row['info']) \
                            not in p5_prods_w_same_key_set.keys():
                p5_prods_w_same_key_set[(row['info_kind'], row['what'], row['where'], row['info'])] = set()
            p5_prods_w_same_key_set[(row['info_kind'], row['what'], row['where'], row['info'])].add(
                row['prod_nr'])

            # document in all_relevant_data_json
    p5_file_out_f = 'p5_' + g.p1_contract_nr + '_all_relevant_data.txt'
    with open(p5_file_out_f, 'w') as f4:
        # json.dump(p5_prods_w_same_key_set, f4, ensure_ascii = False) won't work
        # f4.write(p5_prods_w_same_key_set.__str__()) doesn't look pretty
        pprint.PrettyPrinter(indent = 2, stream = f4).pprint(p5_prods_w_same_key_set)

    document_in_labels_info_json('p5_all_relevant_data', p5_file_out_f)

    # p5_build_set_of_all_products_to_be_processed
    for prod in contract_json_d['l_i']:
        p5_all_products_to_be_processed_set.add(prod["01.TST_prod_#-需方产品编号"])
    document_in_labels_info_json('p5_all_products_to_be_processed_set',
                                 sorted(list(p5_all_products_to_be_processed_set)))

    # p6_split_between p6_common_indics and p6_specific_indics
    for k, v in p5_prods_w_same_key_set.items():
        # indic is not a  packing quantity and is common to all products
        if k[0] != 'pack_qty' and v == p5_all_products_to_be_processed_set:
            if k[3]:  # todo: check why this sometimes not happens
                p6_common_indics_l.append(k)
        else:
            for prod in v:
                if p6_specific_indics_d_of_d.get(prod) is None:
                    p6_specific_indics_d_of_d[prod] = {}
                p6_specific_indics_d_of_d[prod][k[1]] = k[3]  # prod_n : 'what' = indic

    # Checking that numbers are coherent before storing or displaying
    for k, v in p6_specific_indics_d_of_d.items():
        # Checking that packing quantities info are coherent with total_quantity, if not: exit with a message
        if v['total_qty'] != int(v['parc']) * int(v['u_parc']):  # * int(float(v['pack'])):
            print(60 * '*' + '\nIncoherent quantities in xls contract in product: ' + k + '\n' + 60 * '*')
            exit()
        # Checking that under_packing are multiple of parcels (boxes are full), if not: exit the program with a
        # message
        if int(v['u_parc']) % int(float(v['pack'])) != 0:
            print(60 * '*' + '\nUnder-parcels not full in xls contract in product: ' + k + '\n' + 60 * '*')
            exit()

    # indicators common to all products: write to file
    filename = 'p6_' + g.p1_contract_nr + '_extract_common.json'
    with open(filename, 'w') as c3a_f:
        json.dump(p6_common_indics_l, c3a_f, ensure_ascii = False)

    document_in_labels_info_json('p6_extract_common', filename)

    # indicators specific to one or more products, but not to all: print p6_specific_indics_d_of_d
    filename = 'p6_' + g.p1_contract_nr + '_extract_specifics.json'
    with open(filename, 'w') as c3b_f:
        json.dump(p6_specific_indics_d_of_d, c3b_f, ensure_ascii = False)

    document_in_labels_info_json('p6_extract_specifics', filename)


def display():
    print('~~~display~~~')
    p.mod_lev_1_menu = p.menu
    p.menu = 'display'
    g.chdir_n_p2_read()


def update():
    (g.p1_contract_nr, g.p1_initial_xls_contract_file, g.p1_full_path_source_file_xls) = (None, None, None)
    # pick a new xls contract source file with the tkinter browser
    print('Select a filename in graphic file browser -- check if window is hidden')
    g.p1_initial_xls_contract_file = askopenfilename()
    if not g.p1_initial_xls_contract_file:
        return
    # split path and filename
    path, filename_ext = os.path.split(g.p1_initial_xls_contract_file)
    # split filename and extension
    filename, ext = os.path.splitext(filename_ext)
    # check extension indeed is '.xls'
    if ext == '.xls':
        # extract contract_nr
        s = re.match(r'\w+-\d+', filename).group()
        if s:
            g.p1_contract_nr = s
            g.p1_contract_dir = os.path.join(g.p1_root_dir + '/data/' + g.p1_contract_nr)
            g.p1_full_path_source_file_xls = os.path.join(g.p1_contract_dir, filename_ext)
            if not os.path.exists(g.p1_contract_dir):
                os.mkdir(g.p1_contract_dir, mode = 0o700)
                # do not overwrite an existing contract file
            if not os.path.exists(g.p1_full_path_source_file_xls):
                shutil.copy(g.p1_initial_xls_contract_file, g.p1_contract_dir)
        # the prefix has not been checked
        else:
            view_a_prefix_could_not_be_read_from_filename_ext()
            return
        # create_a_new_label_kind 'g.p1_contract_dir'
        document_in_program_info_json_n_chdir()
    else:
        report_selected_file_is_not_xls(filename)
    create()


def delete():  # todo: still display directory in list just after it has been deleted, and bomb when del selected
    print('~~~ deleting non-empty directories ~~~')
    os.chdir(g.p1_root_dir + '/data/')
    drs = g.read_dirs('.')
    for i in range(len(drs)):
        print(i, drs[i])
    print('~~~')
    while True:
        s = input('Enter nr of directory to delete, \'b\' to return : ')
        if s == 'b':
            os.system('clear')
            # p.back()
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(drs)):
                    if drs[int(s)] == g.p1_contract_nr:
                        print(
                            '!!! Erasing current directory\n'
                            'will also delete program-info.json\n'
                            'and start from zero!!!'
                        )
                        os.remove(os.path.join(g.p1_root_dir, 'program-info.json'))
                        del g.p1_program_info_d
                    shutil.rmtree('./' + drs[int(s)])
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


def check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(g_dir, ext, check_prefix = True):
    """
        To check prefix, this requires that p1_contract_nr has been initialized
        """

    # if the cntrct_nr directory os.path.exists
    c_nr_dir = pathlib.Path(g_dir)
    if c_nr_dir.exists():
        # make the sublist of the files that have an '.ext' extension
        ext_file_l = [fl.name for fl in c_nr_dir.glob('*' + ext)]
        # if this list contains only one file return prefix and filename, or check the prefix is correct
        if len(ext_file_l) == 1:
            # check that this file name begins with cntrct_nr if it exists (after the first time run)
            s = re.match(r'\w+-\d+', ext_file_l[0])
            if s:
                prfx = s.group()
                if check_prefix:
                    if g.p1_contract_nr:
                        # if prefix and p1_contract_nr match, return prefix, filename
                        if prfx == g.p1_contract_nr:
                            g.p1_full_path_source_file_xls = os.path.join(g_dir, ext_file_l[0])
                            return prfx, g.p1_full_path_source_file_xls
                        else:
                            view_filename_prefix_inconsistent_with_contract_nr(g.p1_contract_nr, prfx)
                            return None, None
                # p1_contract_nr has not been populated, probably running the program for the first time
                g.p1_full_path_source_file_xls = os.path.join(g_dir, ext_file_l[0])
                return prfx, g.p1_full_path_source_file_xls
            # the prefix has not been checked
            else:
                view_a_prefix_could_not_be_read_from_filename_ext()
                return None, None
        # but also there maybe no ext file in the cntrct_nr directory
        elif len(ext_file_l) == 0:
            # view_file_not_in_directory()
            return None, None
        # or there maybe more than one, which would not be the canonical situation
        else:
            view_too_many_ext_files_in_directory(ext_file_l, ext)
            return None, None
    # if the cntrct_nr directory does not exist, return False
    else:
        return None, None


def build_program_info_d_from_root_xls_file_or_ask_open_file():
    # look for a single xls contract file in the root directory
    g.p1_contract_nr, g.p1_full_path_source_file_xls = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
        g.p1_root_dir, '.xls')

    if not g.p1_contract_nr or not g.p1_full_path_source_file_xls:
        update()
        return
    else:

        g.p1_contract_dir = os.path.join(g.p1_root_dir, 'data/', g.p1_contract_nr)

        # If the directory does not exist yet, create it
        if not os.path.exists(g.p1_contract_dir):
            try:
                os.mkdir(g.p1_contract_dir, mode = 0o700)
            except OSError:
                raise

        # If the directory pre-existed, check if it is coherently populated
        contract_nr_l, filename_source_xls_l = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
            g.p1_contract_dir, '.xls')

        # check for name consistency
        if contract_nr_l:
            if contract_nr_l != g.p1_contract_nr:
                view_filename_prefix_inconsistent_with_contract_nr(g.p1_contract_nr, contract_nr_l)

        # if a xls contract file does not exist in g.contract_dir, copy from the root xls file
        if not filename_source_xls_l:
            # make a copy in the directory that has just been created
            shutil.copy(g.p1_full_path_source_file_xls, g.p1_contract_dir)
            # have g.p1_full_path_source_file_xls now point to the program repository
            _, g.p1_full_path_source_file_xls = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
                g.p1_contract_dir, '.xls')
            print(f'p1: re-building from root xls contract: {g.p1_full_path_source_file_xls}')

    document_in_program_info_json_n_chdir()


def document_in_program_info_json_n_chdir():
    # document the info in program-info.json
    g.p1_program_info_d['p1_contract_nr'] = g.p1_contract_nr
    g.p1_program_info_d['p1_initial_xls'] = g.p1_initial_xls_contract_file
    g.p1_program_info_d['p1_full_path_source_file_xls'] = g.p1_full_path_source_file_xls
    with open(g.p1_program_info_f, 'w') as fw:
        json.dump(g.p1_program_info_d, fw, ensure_ascii = False)
    os.chdir(g.p1_contract_dir)


def display_p4_search_reg_ex_l():
    pprint.pprint(p4_search_reg_ex_l)


def display_p4_indics_from_contract_l():
    pprint.pprint(p4_indics_from_contract_l)


def display_p5_prods_w_same_key_set():
    pprint.pprint(p5_prods_w_same_key_set)


def display_p5_all_products_to_be_processed_set():
    pprint.pprint(p5_all_products_to_be_processed_set)


def display_p6_common_indics_l():
    pprint.pprint(p6_common_indics_l)


def display_p6_specific_indics_d_of_d():
    pprint.pprint(p6_specific_indics_d_of_d)


def document_in_labels_info_json(key, filename):
    g.p2_labels_info_d[key] = filename
    with open(g.p2_labels_info_f, 'w') as fi:
        json.dump(g.p2_labels_info_d, fi, ensure_ascii = False)


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


def select_exec_function():
    # document the info in A1234-567_labels-info.json file
    g.p2_labels_info_d['p6_lbl_dir'] = g.p6_lbl_dir
    _, g.p6_lbl_sel = os.path.split(g.p6_lbl_dir)
    g.p2_labels_info_d['p6_lbl_sel'] = g.p6_lbl_sel
    with open(g.p2_labels_info_f, 'w') as fi:
        json.dump(g.p2_labels_info_d, fi, ensure_ascii = False)


def chdir_exec_function():
    if os.path.isdir(g.p6_lbl_dir):
        os.chdir(g.p6_lbl_dir)
    print(f'Now in {os.getcwd()} ')


def p6_display_existing_non_existing_dirs():
    g.display_dirs()

    selected_lbl = g.p6_lbl_dir[g.p6_lbl_dir.rfind('/'):]
    current_dir_fp = os.getcwd()
    current_dir_lcl = current_dir_fp[current_dir_fp.rfind('/'):]
    print(f'Selected label: {selected_lbl}, currently in {current_dir_lcl}')


def view_too_many_ext_files_in_directory(xls_file_l, ext):
    print(f"\n{len(xls_file_l)} {ext} files are present, that's too many, exiting\n")


def view_filename_prefix_inconsistent_with_contract_nr(cntrct_nr, prfx):
    print(f'\nIncorrect! The file in {cntrct_nr} starts with {prfx}\n')


def view_file_not_in_directory():
    print(f'\nThe xls file corresponding to {g.p1_contract_nr} contract is not present, exiting\n')


def view_a_prefix_could_not_be_read_from_filename_ext():
    print('A prefix could not be display from filename ext')


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
