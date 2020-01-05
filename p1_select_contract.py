#!/usr/bin/env python3
# p1_select_contract.py
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

import u_menus as p

p0_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located
p1_program_info_d = {}
p1_program_info_f = ''
p1_initial_xls_contract_file = ''
p1_contract_nr = ''  # prefix of the contract xls source file
p1_full_path_source_file_xls = ''  # full path of source xls file
p1_contract_dir = ''  # directory where a copy of the xls contract file and contract extracted data is


def p0_set_global_variables():
    global p1_contract_nr
    global p1_full_path_source_file_xls
    global p1_contract_dir
    global p1_program_info_d
    global p1_program_info_f

    p1_program_info_f = os.path.join(p0_root_dir, 'program-info.json')
    if pathlib.Path(p1_program_info_f).exists():
        # then load the info it contains in p1_program_info_d dictionary
        with open(p1_program_info_f) as f:
            p1_program_info_d = json.load(f)
        # check if p1_program_info_d['p1_contract_nr'] helps point to a valid file,
        if p1_program_info_d:
            p1_contract_nr = p1_program_info_d['p1_contract_nr']
            p1_full_path_source_file_xls = p1_program_info_d['p1_full_path_source_file_xls']
            p1_contract_dir = p0_root_dir + f'/data/{p1_contract_nr}'


# local path to labels-info.json file
p1_labels_info_d = {}
p1_labels_info_f = ''

p1_search_reg_ex_l = []
p1b_indics_from_contract_l = []
p1_prods_w_same_key_set = {}  # make a dictionary key= info, value = sets of prods with that key
p1_all_products_to_be_processed_set = set()
p1d_common_indics_l = []
p1e_specific_indics_d_of_d = {}
indicators_csv = os.path.join(p0_root_dir + '/common', 'indicators.csv')


def p1_read_from_disk_n_set_global_var_if_necessary(key):
    """
    "p1a_contract_json": "p1a_A906202-006-contract.json",
    "p1b_indics_from_contract_l": "p1b_A906202-006_indics_from_contract_l.json",
    "p1c_all_relevant_data": "p1c_A906202-006_all_relevant_data.txt",
    "p5_all_products_to_be_processed_set": [ "MS01001", "MS01022", "MS01037", "MS01038", "MS01039", "MS01040" ],
    "p1d_extract_common": "p1d_A906202-006_extract_common.json",
    "p1e_extract_specifics": "p1e_A906202-006_extract_specifics.json"
    """
    global p1_labels_info_d
    global p1_labels_info_f
    if not p1_labels_info_d:
        p1_labels_info_f = 'p1_' + p1_contract_nr + '_labels-info.json'
        with open(p1_labels_info_f) as fi:
            p1_labels_info_d = json.load(fi)
        return p1_labels_info_d[key]


def report_selected_file_is_not_xls(filename):
    print(f'\nSelected file {filename} extension is not \'.xls\'\n')


def p_context():
    display_dirs(p0_root_dir + '/data/')
    print('~~~ Select contract: ')


def display_1_context():
    display_dirs(p0_root_dir + '/data/')
    print('~~~ Select contract / Display ~~~')
    p0_set_global_variables()


context_func_d = {
    'select_contract': p_context,
    'display_sub_processes_output': display_1_context,
}


def init():
    global p1_program_info_f
    # menus
    p.menu = 'select_contract'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': auto_create,
            '2': read_n_display,
            '3': update_or_select_new_contract,
            '4': delete,
            '7': display_sub_processes_output,
            '8': display_p1_program_info_d,
            '9': display_p1_program_info_f,
            'm': p.back_to_main,
            'q': p.normal_exit,
        },
        'display_sub_processes_output': {
            '1': after_running_p1_only_display_p4_search_reg_ex_l,
            '2': display_p1_all_products_to_be_processed_set,
            '3': display_p1b_indics_from_contract_l,
            '4': display_p1d_common_indics_l,
            '5': display_p6_specific_indics_d_of_d,
            '6': display_p1_labels_info_d,
            '7': display_p1_labels_info_f,
            'b': p.back,
            'q': p.normal_exit,
        }
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}

    # If the data directory does not exist, auto_create it
    data_dir = os.path.join(p0_root_dir, 'data')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir, mode=0o700)

    # initializing globals necessary for all functions
    os.chdir(p0_root_dir + '/data/')
    p1_program_info_f = os.path.join(p0_root_dir, 'program-info.json')


def auto_create():
    global p1_contract_nr
    global p1_contract_dir
    global p1_full_path_source_file_xls
    global p1_program_info_f
    global p1_program_info_d
    global p1_initial_xls_contract_file
    global p1_labels_info_d
    global p1_labels_info_f

    # checking if a program-info.json file exists in the root directory
    if pathlib.Path(p1_program_info_f).exists():
        # then load the info it contains in p1_program_info_d dictionary
        with open(p1_program_info_f) as f:
            p1_program_info_d = json.load(f)
        # check if p1_program_info_d['p1_contract_nr'] helps point to a valid file,
        if p1_program_info_d:
            # then check if this one could be working data
            if 'p1_contract_nr' in p1_program_info_d:
                p1_contract_dir = p0_root_dir + f'/data/{p1_program_info_d["p1_contract_nr"]}'
                if not os.path.isdir(p1_contract_dir):
                    os.mkdir(p1_contract_dir)
                os.chdir(p1_contract_dir)
                _, result = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(p1_contract_dir, '.xls')
                if result:
                    # create_a_new_label_kind all global variables accordingly
                    p1_full_path_source_file_xls = result
                    p1_contract_nr = p1_program_info_d["p1_contract_nr"]
                # if the data from p1_program_info_d cannot be used
                else:
                    # if a valid initial file exists but is not uniquely copied in the repertory
                    if 'p1_initial_xls' in p1_program_info_d:
                        if not os.path.exists(p1_contract_dir):
                            os.mkdir(p1_contract_dir, mode=0o700)
                            os.chdir(p1_contract_dir)
                        p1_initial_xls_contract_file = p1_program_info_d['p1_initial_xls']
                        shutil.copy(p1_initial_xls_contract_file, p1_contract_dir)
                        _, filename_ext = os.path.split(p1_initial_xls_contract_file)
                        p1_full_path_source_file_xls = os.path.join(p1_contract_dir, filename_ext)
                    else:
                        # cannot do much else with this info, abandon and start-over
                        del p1_program_info_d['p1_contract_nr']
                        build_program_info_d_from_root_xls_file_or_ask_open_file()
        # if program-info.json doesn't point to a valid ./data/p1_contract_nr and xls file, then rebuild
        else:
            build_program_info_d_from_root_xls_file_or_ask_open_file()
    # if program-info.json does not exist
    else:
        build_program_info_d_from_root_xls_file_or_ask_open_file()

    # the name of the -contract.json file can now be set
    rel_path_contract_json_f = 'p1a_' + p1_contract_nr + '-contract.json'

    # Creating the json file from the local xls file: opening the xl file
    book = xlrd.open_workbook(p1_full_path_source_file_xls)
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
        json.dump(contract_json_d, fc, ensure_ascii=False)
    # document in A1234-456-info.json
    p1_labels_info_f = 'p1_' + p1_contract_nr + '_labels-info.json'
    # auto_create a structure to store label information
    p1_labels_info_d = {'p1a_contract_json': rel_path_contract_json_f}
    with open(p1_labels_info_f, 'w') as fi:
        json.dump(p1_labels_info_d, fi, ensure_ascii=False)

    # def create_2():
    # reading info from ./common/indicators.csv, which was kept in csv format to make human input easier
    with open(indicators_csv) as f:
        my_dict_reader = csv.DictReader(f)
        for row in my_dict_reader:
            temp_dict = dict(row)
            p1_search_reg_ex_l.append(temp_dict)

    # p1b_indics_from_contract_l: harvesting all indicators possibly available in the contract_json_d
    for row_indic in p1_search_reg_ex_l:
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
            p1b_indics_from_contract_l.append(tmp_dct)
            tmp_dct = {  # adding 05.Quantity-数量 info
                'info_kind': 'pack_qty',
                'what': 'total_qty',
                'where': '05.Quantity-数量',
                'prod_nr': prod['01.TST_prod_#-需方产品编号'],
                'info': int(prod['05.Quantity-数量'])
            }
            p1b_indics_from_contract_l.append(tmp_dct)
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
                            p1b_indics_from_contract_l.append(tmp_dct)
        p1b_indics_from_contract_l.sort(key=lambda item: item['prod_nr'])
        file_indics = 'p1b_' + p1_contract_nr + '_indics_from_contract_l.json'

        # register in file and object
        document_in_labels_info_json('p1b_indics_from_contract_l', file_indics)

        with open(file_indics, 'w') as f:
            json.dump(p1b_indics_from_contract_l, f, ensure_ascii=False)

        # p1_prods_w_same_key_set = {}  # make a dictionary key= info, value = sets of prods with that key
        for row in p1b_indics_from_contract_l:
            # for index, row in c_df.iterrows():  # index is not used
            if (row['info_kind'], row['what'], row['where'], row['info']) \
                    not in p1_prods_w_same_key_set.keys():
                p1_prods_w_same_key_set[(row['info_kind'], row['what'], row['where'], row['info'])] = set()
            p1_prods_w_same_key_set[(row['info_kind'], row['what'], row['where'], row['info'])].add(
                row['prod_nr'])

            # document in all_relevant_data_json
    p5_file_out_f = 'p1c_' + p1_contract_nr + '_all_relevant_data.txt'
    with open(p5_file_out_f, 'w') as f4:
        # json.dump(p1_prods_w_same_key_set, f4, ensure_ascii = False) won't work
        # f4.write(p1_prods_w_same_key_set.__str__()) doesn't look pretty
        pprint.PrettyPrinter(indent=2, stream=f4).pprint(p1_prods_w_same_key_set)

    document_in_labels_info_json('p1c_all_relevant_data', p5_file_out_f)

    # p5_build_set_of_all_products_to_be_processed
    for prod in contract_json_d['l_i']:
        p1_all_products_to_be_processed_set.add(prod["01.TST_prod_#-需方产品编号"])
    document_in_labels_info_json('p1_all_products_to_be_processed_set',
                                 sorted(list(p1_all_products_to_be_processed_set)))

    # p6_split_between p6_common_indics and p6_specific_indics
    for k, v in p1_prods_w_same_key_set.items():
        # indic is not a  packing quantity and is common to all products
        if k[0] != 'pack_qty' and v == p1_all_products_to_be_processed_set:
            if k[3]:  # todo: check why this sometimes not happens
                p1d_common_indics_l.append(k)
        else:
            for prod in v:
                if p1e_specific_indics_d_of_d.get(prod) is None:
                    p1e_specific_indics_d_of_d[prod] = {}
                p1e_specific_indics_d_of_d[prod][k[1]] = k[3]  # prod_n : 'what' = indic

    # Checking that numbers are coherent before storing or displaying
    for k, v in p1e_specific_indics_d_of_d.items():
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
    filename = 'p1d_' + p1_contract_nr + '_extract_common.json'
    with open(filename, 'w') as c3a_f:
        json.dump(p1d_common_indics_l, c3a_f, ensure_ascii=False)

    document_in_labels_info_json('p1d_extract_common', filename)

    # indicators specific to one or more products, but not to all: print p1e_specific_indics_d_of_d
    filename = 'p1e_' + p1_contract_nr + '_extract_specifics.json'
    with open(filename, 'w') as c3b_f:
        json.dump(p1e_specific_indics_d_of_d, c3b_f, ensure_ascii=False)

    document_in_labels_info_json('p1e_extract_specifics', filename)


def read_n_display():
    read()
    display()


def read():
    """
    Process p1 has run successfully, returns a directory of global variables, either already in memory
    either resulting from a previous run, then saved and now re-loaded from disk
        """
    global p1_program_info_f
    global p1_program_info_d

    # info is already in memory, let's check its validity
    if p1_program_info_d:
        # a contract has been selected
        if p1_program_info_d['p1_contract_nr']:
            # if a contract file is already in the repository
            if p1_program_info_d['p1_full_path_source_file_xls']:
                return p1_program_info_d
            # or if a contract file outside the repository has been selected, put it back and pursue
            elif p1_program_info_d['p1_full_path_source_file_xls']:
                shutil.copy(p1_program_info_d['p1_full_path_source_file_xls'], p1_contract_dir)
                return p1_program_info_d
    # info can be loaded from disk to populate global variables
    p1_program_info_f = os.path.join(p0_root_dir, 'program-info.json')
    if os.path.isfile(p1_program_info_f):
        with open(p1_program_info_f) as f:
            p1_program_info_d = json.load(f)
            if p1_program_info_d:
                p0_set_global_variables()
                if not os.path.exists(p1_contract_dir) or not os.path.exists(p1_full_path_source_file_xls):
                    return None
                return p1_program_info_d
    return None


def display():
    pass


def display_sub_processes_output():
    print('~~~display_sub_processes_output~~~')
    p.mod_lev_1_menu = p.menu
    p.menu = 'display_sub_processes_output'


def update_or_select_new_contract():
    global p1_contract_nr
    global p1_contract_dir
    global p1_full_path_source_file_xls
    global p1_initial_xls_contract_file

    (p1_contract_nr, p1_initial_xls_contract_file, p1_full_path_source_file_xls) = (None, None, None)
    # pick a new xls contract source file with the tkinter browser
    print('Select a filename in graphic file browser -- check if window is hidden')
    p1_initial_xls_contract_file = askopenfilename()
    if not p1_initial_xls_contract_file:
        return
    # split path and filename
    path, filename_ext = os.path.split(p1_initial_xls_contract_file)
    # split filename and extension
    filename, ext = os.path.splitext(filename_ext)
    # check extension indeed is '.xls'
    if ext == '.xls':
        # extract contract_nr
        s = re.match(r'\w+-\d+', filename).group()
        if s:
            p1_contract_nr = s
            p1_contract_dir = os.path.join(p0_root_dir + '/data/' + p1_contract_nr)
            p1_full_path_source_file_xls = os.path.join(p1_contract_dir, filename_ext)
            if not os.path.exists(p1_contract_dir):
                os.mkdir(p1_contract_dir, mode=0o700)
                # do not overwrite an existing contract file
            if not os.path.exists(p1_full_path_source_file_xls):
                shutil.copy(p1_initial_xls_contract_file, p1_contract_dir)
        # the prefix has not been checked
        else:
            view_a_prefix_could_not_be_read_from_filename_ext()
            return
        # create_a_new_label_kind 'p1_contract_dir'
        document_in_program_info_json()
    else:
        report_selected_file_is_not_xls(filename)
    auto_create()


def delete():  # todo: still display_sub_processes_output directory in list just after it has been deleted,
    # and bomb when del selected
    print('~~~ deleting non-empty directories ~~~')
    drs = read_dirs('.')
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
                    if drs[int(s)] == p1_contract_nr:
                        print(
                            '!!! Erasing current directory\n'
                            'will also delete program-info.json\n'
                            'and start from zero!!!'
                        )
                        os.remove(os.path.join(p0_root_dir, 'program-info.json'))
                        del p1_program_info_d
                    shutil.rmtree('./' + drs[int(s)])
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


def check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(g_dir, ext, check_prefix=True):
    """
        To check prefix, this requires that p1_contract_nr has been initialized
        """
    global p1_contract_nr
    global p1_contract_dir
    global p1_full_path_source_file_xls
    global p1_program_info_f
    global p1_program_info_d
    global p1_initial_xls_contract_file
    global p1_labels_info_d
    global p1_labels_info_f

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
                    if p1_contract_nr:
                        # if prefix and p1_contract_nr match, return prefix, filename
                        if prfx == p1_contract_nr:
                            p1_full_path_source_file_xls = os.path.join(g_dir, ext_file_l[0])
                            return prfx, p1_full_path_source_file_xls
                        else:
                            view_filename_prefix_inconsistent_with_contract_nr(p1_contract_nr, prfx)
                            return None, None
                # p1_contract_nr has not been populated, probably running the program for the first time
                p1_full_path_source_file_xls = os.path.join(g_dir, ext_file_l[0])
                return prfx, p1_full_path_source_file_xls
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
    global p1_contract_nr
    global p1_contract_dir
    global p1_full_path_source_file_xls
    global p1_program_info_f
    global p1_program_info_d
    global p1_initial_xls_contract_file
    global p1_contract_nr
    global p1_contract_dir

    # look for a single xls contract file in the root directory
    p1_contract_nr, p1_full_path_source_file_xls = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
        p0_root_dir, '.xls')

    if not p1_contract_nr or not p1_full_path_source_file_xls:
        update_or_select_new_contract()
        return
    else:

        p1_contract_dir = os.path.join(p0_root_dir, 'data/', p1_contract_nr)

        # If the directory does not exist yet, auto_create it
        if not os.path.exists(p1_contract_dir):
            try:
                os.mkdir(p1_contract_dir, mode=0o700)
            except OSError:
                raise

        # If the directory pre-existed, check if it is coherently populated
        contract_nr_l, filename_source_xls_l = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
            p1_contract_dir, '.xls')

        # check for name consistency
        if contract_nr_l:
            if contract_nr_l != p1_contract_nr:
                view_filename_prefix_inconsistent_with_contract_nr(p1_contract_nr, contract_nr_l)

        # if a xls contract file does not exist in contract_dir, copy from the root xls file
        if not filename_source_xls_l:
            # make a copy in the directory that has just been created
            shutil.copy(p1_full_path_source_file_xls, p1_contract_dir)
            # have p1_full_path_source_file_xls now point to the program repository
            _, p1_full_path_source_file_xls = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
                p1_contract_dir, '.xls')
            print(f'p1: re-building from root xls contract: {p1_full_path_source_file_xls}')

    document_in_program_info_json()


def document_in_program_info_json():
    # document the info in program-info.json
    p1_program_info_d['p1_contract_nr'] = p1_contract_nr
    p1_program_info_d['p1_initial_xls'] = p1_initial_xls_contract_file
    p1_program_info_d['p1_full_path_source_file_xls'] = p1_full_path_source_file_xls
    with open(p1_program_info_f, 'w') as fw:
        json.dump(p1_program_info_d, fw, ensure_ascii=False)


def after_running_p1_only_display_p4_search_reg_ex_l():
    pprint.pprint(p1_search_reg_ex_l)


def display_p1b_indics_from_contract_l():
    p1_read_from_disk_n_set_global_var_if_necessary('p1b_indics_from_contract_l')
    pprint.pprint(p1b_indics_from_contract_l)


def display_p1_all_products_to_be_processed_set():
    global p1_labels_info_d
    global p1_labels_info_f
    global p1_all_products_to_be_processed_set
    if not p1_labels_info_d:
        p1_labels_info_f = os.path.join(p1_contract_dir, 'p1_' + p1_contract_nr + '_labels-info.json')
        with open(p1_labels_info_f) as fi:
            p1_labels_info_d = json.load(fi)
    p1_all_products_to_be_processed_set = p1_labels_info_d['p1_all_products_to_be_processed_set']
    pprint.pprint(p1_all_products_to_be_processed_set)


def display_p1d_common_indics_l():
    p1_read_from_disk_n_set_global_var_if_necessary('p1d_extract_common')
    pprint.pprint(p1d_common_indics_l)


def display_p6_specific_indics_d_of_d():
    p1_read_from_disk_n_set_global_var_if_necessary('p1e_extract_specifics')
    pprint.pprint(p1e_specific_indics_d_of_d)


def document_in_labels_info_json(key, filename):
    global p1_labels_info_d
    p1_labels_info_d[key] = filename
    with open(p1_labels_info_f, 'w') as fi:
        json.dump(p1_labels_info_d, fi, ensure_ascii=False)


def view_too_many_ext_files_in_directory(xls_file_l, ext):
    print(f"\n{len(xls_file_l)} {ext} files are present, that's too many, exiting\n")


def view_filename_prefix_inconsistent_with_contract_nr(cntrct_nr, prfx):
    print(f'\nIncorrect! The file in {cntrct_nr} starts with {prfx}\n')


def view_file_not_in_directory():
    print(f'\nThe xls file corresponding to {p1_contract_nr} contract is not present, exiting\n')


def view_a_prefix_could_not_be_read_from_filename_ext():
    print('A prefix could not be display_sub_processes_output from filename ext')


def display_p1_labels_info_d():
    global p1_labels_info_d
    print('~~~ Reading labels-info global value ~~~')
    pprint.pprint(p1_labels_info_d)
    print('~~~ Finished reading labels-info global value ~~~')


def display_p1_labels_info_f():
    # global p1_labels_info_f
    # p1_labels_info_f = os.path.join(p1_contract_dir, 'p1_' + p1_contract_nr + '_labels-info.json')
    if p1_labels_info_f:
        if os.path.isfile(p1_labels_info_f):
            print('~~~ Reading labels-info.json file contents ~~~')
            with open(p1_labels_info_f) as f:
                # print(f.read())
                pprint.pprint(f.read())
            print('~~~ File labels-info.json closed ~~~')
    else:
        print(f'\nFile {p1_labels_info_f} not built yet\n')


def read_dirs(walk_dir):
    global p1_contract_dir

    if walk_dir:
        (root, dirs, files) = next(os.walk(walk_dir))
        if dirs:
            dirs.sort()
            dirs[:] = [d for d in dirs if d[0] not in ['.', '_']]
            return dirs
    return None


def display_p1_program_info_d():
    global p1_program_info_d
    print('~~~ Reading program-info global value ~~~')
    pprint.pprint(p1_program_info_d)
    print('~~~ Finished reading program-info global value ~~~')


def display_p1_program_info_f():
    global p1_program_info_f
    print('~~~ Reading program-info.json file contents ~~~')
    with open(p1_program_info_f) as f:
        pprint.pprint(f.read())
    print('~~~ File program-info.json closed ~~~')


def display_dirs(walk_dir):
    drs = read_dirs(walk_dir)
    if drs:
        for dr in drs:
            print(dr)
    else:
        return None


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()