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
import p0_menus as p

p0_root_abs_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located
p1_contract_nr = ''  # prefix of the contract xls source file
p1_program_info_f = ''
p1_program_info_d = {}
p1_initial_xls_contract_file = ''
p1_full_path_source_file_xls = ''  # full path of source xls file
p1_contract_abs_dir = ''  # directory where a copy of the xls contract file and contract extracted data is


def p0_load_program_info_d():
    """
    Loads p1_contract_nr, p1_full_path_source_file_xls, and p1_contract_abs_dir from program-info.json
    """
    global p1_contract_nr
    global p1_program_info_f
    global p1_program_info_d
    global p1_full_path_source_file_xls
    global p1_contract_abs_dir

    # If the data directory does not exist, process_default_contract it
    data_abs_dir = os.path.join(p0_root_abs_dir, 'data')
    if not os.path.exists(data_abs_dir):
        os.mkdir(data_abs_dir, mode = 0o700)

    p1_program_info_f = os.path.join(p0_root_abs_dir, 'program-info.json')
    if pathlib.Path(p1_program_info_f).exists():
        # then load the info it contains in p1_program_info_d dictionary
        with open(p1_program_info_f) as f:
            p1_program_info_d = json.load(f)
        # check if p1_program_info_d['p1_contract_nr'] helps point to a valid file,
        if p1_program_info_d:
            p1_contract_nr = p1_program_info_d['p1_contract_nr']
            p1_full_path_source_file_xls = p1_program_info_d['p1_full_path_source_file_xls']
            p1_contract_abs_dir = p0_root_abs_dir + f'/data/{p1_contract_nr}'
            return True


# local path to contract-info.json file
p1_contract_info_d = {}
p1_contract_info_f = ''
p1_search_reg_ex_l = []
indicators_csv = os.path.join(p0_root_abs_dir + '/common', 'indicators.csv')
p1_all_products_to_be_processed_set = set()
p1b_indics_from_contract_l = []
p1c_prods_w_same_key_set = {}  # make a dictionary key= info, value = sets of prods with that key
p1d_common_indics_l = []
p1e_specific_fields_d_of_d = {}


def p1_load_contract_info_d():
    """
    Loads p1_contract_info_f into p1_contract_info_d, maybe resetting these values
    Will run p1.init() and p1.process_default_contact() if necessary
    """
    global p1_contract_info_d
    global p1_contract_info_f
    global p1_contract_abs_dir
    global p1_contract_nr

    if not p0_load_program_info_d():
        if not p1_contract_abs_dir or not p1_contract_nr:
            # init()
            p0_load_program_info_d()
            process_default_contract()
    p1_contract_info_f = os.path.join(p1_contract_abs_dir, 'p1_' + p1_contract_nr + '_contract-info.json')
    with open(p1_contract_info_f) as fi:
        p1_contract_info_d = json.load(fi)
    return True


def process_default_contract():
    global p1_contract_nr
    global p1_contract_abs_dir
    global p1_full_path_source_file_xls
    global p1_program_info_f
    global p1_program_info_d
    global p1_initial_xls_contract_file
    global p1_contract_info_d
    global p1_contract_info_f
    global p1_search_reg_ex_l
    global p1b_indics_from_contract_l
    global p1c_prods_w_same_key_set
    global p1_all_products_to_be_processed_set
    global p1d_common_indics_l
    global p1e_specific_fields_d_of_d
    # reset to zero if these had been loaded from disk before
    p1_search_reg_ex_l = []
    p1b_indics_from_contract_l = []
    p1c_prods_w_same_key_set = {}
    p1_all_products_to_be_processed_set = set()
    p1d_common_indics_l = []
    p1e_specific_fields_d_of_d = {}

    p0_load_program_info_d()
    # checking if a program-info.json file exists in the root directory
    if pathlib.Path(p1_program_info_f).exists():
        # then load the info it contains in p1_program_info_d dictionary
        with open(p1_program_info_f) as f:
            p1_program_info_d = json.load(f)
        # check if p1_program_info_d['p1_contract_nr'] helps point to a valid file,
        if p1_program_info_d:
            # then check if this one could be working data
            if 'p1_contract_nr' in p1_program_info_d:
                p1_contract_abs_dir = p0_root_abs_dir + f'/data/{p1_program_info_d["p1_contract_nr"]}'
                if not os.path.isdir(p1_contract_abs_dir):
                    os.mkdir(p1_contract_abs_dir)
                _, result = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(p1_contract_abs_dir, '.xls')
                if result:
                    # create_a_new_label_kind all global variables accordingly
                    p1_full_path_source_file_xls = result
                    p1_contract_nr = p1_program_info_d["p1_contract_nr"]
                # if the data from p1_program_info_d cannot be used
                else:
                    # if a valid initial file exists but is not uniquely copied in the repertory
                    if 'p1_initial_xls' in p1_program_info_d:
                        if not os.path.exists(p1_contract_abs_dir):
                            os.mkdir(p1_contract_abs_dir, mode = 0o700)
                        p1_initial_xls_contract_file = p1_program_info_d['p1_initial_xls']
                        shutil.copy(p1_initial_xls_contract_file, p1_contract_abs_dir)
                        _, filename_ext = os.path.split(p1_initial_xls_contract_file)
                        p1_full_path_source_file_xls = os.path.join(p1_contract_abs_dir, filename_ext)
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

    with open(os.path.join(p1_contract_abs_dir, rel_path_contract_json_f), 'w') as fc:
        json.dump(contract_json_d, fc, ensure_ascii = False)
    # document in A1234-456-info.json
    p1_contract_info_f = 'p1_' + p1_contract_nr + '_contract-info.json'
    # process_default_contract a structure to store label information
    p1_contract_info_d = {'p1a_contract_json': rel_path_contract_json_f}
    filename = os.path.join(p1_contract_abs_dir, p1_contract_info_f)
    with open(filename, 'w') as fi:
        json.dump(p1_contract_info_d, fi, ensure_ascii = False)

    # def create_2():
    # reading info from ./common/indicators.csv, which was kept in csv format to make human input easier
    load_p1_search_reg_ex_l()

    # p1b_indics_from_contract_l: harvesting all indicators possibly available in the contract_json_d
    for row_indic in p1_search_reg_ex_l:
        what = row_indic['what']
        info_kind = row_indic['info_kind']
        how = row_indic['how']
        for prod in contract_json_d['l_i']:  # inspecting products one by one
            tmp_dct = {  # adding 03.Prod_spec-产品规则 info
                'info_kind': 'spec',
                'what': 'xl_prod_spec',
                'where': 'xl_quantity-数量',
                'prod_nr': prod['01.TST_prod_#-需方产品编号'],
                'info': prod["03.Prod_spec-产品规格"]
            }
            p1b_indics_from_contract_l.append(tmp_dct)
            tmp_dct = {  # adding 05.Quantity-数量 info
                'info_kind': 'pack_qty',
                'what': 'total_qty',
                'where': 'xl_quantity-数量',
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
        p1b_indics_from_contract_l.sort(key = lambda item: item['prod_nr'])
        file_indics = 'p1b_' + p1_contract_nr + '_indics_from_contract_l.json'

        # register in file and object
        document_in_contract_info_json('p1b_indics_from_contract_l', file_indics)

        f = os.path.join(p1_contract_abs_dir, file_indics)
        with open(f, 'w') as f:
            json.dump(p1b_indics_from_contract_l, f, ensure_ascii = False)

        # p1c_prods_w_same_key_set = {}  # make a dictionary key= info, value = sets of prods with that key
        for row in p1b_indics_from_contract_l:
            # for index, row in c_df.iterrows():  # index is not used
            if (row['info_kind'], row['what'], row['where'], row['info']) not in p1c_prods_w_same_key_set.keys():
                p1c_prods_w_same_key_set[(row['info_kind'], row['what'], row['where'], row['info'])] = set()
            p1c_prods_w_same_key_set[(row['info_kind'], row['what'], row['where'], row['info'])].add(
                row['prod_nr'])

            # document in all_relevant_data_json
    p1c_file_out_f = 'p1c_' + p1_contract_nr + '_all_relevant_data.txt'
    f = os.path.join(p1_contract_abs_dir, p1c_file_out_f)
    with open(f, 'w') as f1c:
        # json.dump(p1c_prods_w_same_key_set, f1c, ensure_ascii = False) won't work
        # f1c.write(p1c_prods_w_same_key_set.__str__()) doesn't look pretty
        pprint.PrettyPrinter(indent = 2, stream = f1c).pprint(p1c_prods_w_same_key_set)

    document_in_contract_info_json('p1c_all_relevant_data', p1c_file_out_f)

    # p1c_build_set_of_all_products_to_be_processed
    for prod in contract_json_d['l_i']:
        p1_all_products_to_be_processed_set.add(prod["01.TST_prod_#-需方产品编号"])
    document_in_contract_info_json('p1_all_products_to_be_processed_set',
                                   sorted(list(p1_all_products_to_be_processed_set)))

    # p6_split_between p6_common_indics and p6_specific_indics
    for k, v in p1c_prods_w_same_key_set.items():
        # indic is not a  packing quantity and is common to all products
        if k[0] != 'pack_qty' and v == p1_all_products_to_be_processed_set:
            if k[3]:  # todo: check why this sometimes not happens
                p1d_common_indics_l.append(k)
        else:
            for prod in v:
                if p1e_specific_fields_d_of_d.get(prod) is None:
                    p1e_specific_fields_d_of_d[prod] = {}
                p1e_specific_fields_d_of_d[prod][k[1]] = k[3]  # prod_n : 'what' = indic

    # Checking that numbers are coherent before storing or displaying
    for k, v in p1e_specific_fields_d_of_d.items():
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
    f = os.path.join(p1_contract_abs_dir, filename)
    with open(f, 'w') as p1d_f:
        json.dump(p1d_common_indics_l, p1d_f, ensure_ascii = False)

    document_in_contract_info_json('p1d_extract_common', filename)

    # indicators specific to one or more products, but not to all: print p1e_specific_fields_d_of_d
    filename = 'p1e_' + p1_contract_nr + '_extract_specifics.json'
    f = os.path.join(p1_contract_abs_dir, filename)
    with open(f, 'w') as p1e_f:
        json.dump(p1e_specific_fields_d_of_d, p1e_f, ensure_ascii = False)

    document_in_contract_info_json('p1e_extract_specifics', filename)


def display_or_load_output_overview():
    if p1_load_contract_info_d():
        display()


def display():
    if p1_contract_info_d:
        display_p1_contract_info_d()
    elif p1_contract_info_f:
        print('trying to read_program_info from disk:')
        display_p1_program_info_f()
    else:
        print('p1 has not run or data cannot be loaded from disk:')


def display_sub_processes_output():
    print('~~~display_sub_processes_output~~~')
    p.mod_lev_1_menu = p.menu
    p.menu = 'display_sub_processes_output'


def select_new_contract():
    global p1_contract_nr
    global p1_contract_abs_dir
    global p1_full_path_source_file_xls
    global p1_initial_xls_contract_file

    (p1_contract_nr, p1_initial_xls_contract_file, p1_full_path_source_file_xls) = (None, None, None)
    # pick a new xls contract source file with the tkinter browser
    print('~~~ Select a filename in graphic file browser -- check if window is hidden')
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
            p1_contract_abs_dir = os.path.join(p0_root_abs_dir + '/data/' + p1_contract_nr)
            p1_full_path_source_file_xls = os.path.join(p1_contract_abs_dir, filename_ext)
            if not os.path.exists(p1_contract_abs_dir):
                os.mkdir(p1_contract_abs_dir, mode = 0o700)
                # do not overwrite an existing contract file
            if not os.path.exists(p1_full_path_source_file_xls):
                shutil.copy(p1_initial_xls_contract_file, p1_contract_abs_dir)
        # the prefix has not been checked
        else:
            view_a_prefix_could_not_be_read_from_filename_ext()
            return
        # create_a_new_label_kind 'p1_contract_abs_dir'
        document_in_program_info_json()
    else:
        report_selected_file_is_not_xls(filename)
    process_default_contract()


def delete_all_data_on_selected_contract():
    global p1_program_info_d
    global p1_contract_nr
    global p0_root_abs_dir
    print('~~~ deleting non-empty directories ~~~')
    drs = read_dirs(p0_root_abs_dir + '/data/')
    if not drs:
        return
    for i in range(len(drs)):
        print(i, drs[i])
    print('~~~')
    while True:
        s = input('Enter nr of directory to delete_all_data_on_selected_contract, \'b\' to return : ')
        if s == 'b':
            os.system('clear')
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(drs)):
                    if drs[int(s)] == p1_contract_nr:
                        print(
                            '\n\t!!! Erasing current directory\n'
                            '\tthis will also delete_all_data_on_selected_contract program-info.json\n'
                            '\tand start as if repository is empty !!!'
                        )
                        os.remove(os.path.join(p0_root_abs_dir, 'program-info.json'))
                        p1_program_info_d = {}
                        p1_contract_nr = ''
                    shutil.rmtree(p0_root_abs_dir + '/data/' + drs[int(s)])
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


def check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(some_abs_dir, ext, check_prefix = True):
    """
        To check prefix, this requires that p1_contract_nr has been initialized
        """
    global p1_contract_nr
    global p1_contract_abs_dir
    global p1_full_path_source_file_xls
    global p1_program_info_f
    global p1_program_info_d
    global p1_initial_xls_contract_file
    global p1_contract_info_d
    global p1_contract_info_f

    # if the cntrct_nr directory os.path.exists
    c_nr_abs_dir = pathlib.Path(some_abs_dir)  # check why this is necessary
    if c_nr_abs_dir.exists():
        # make the sublist of the files that have an '.ext' extension
        ext_file_l = [fl.name for fl in c_nr_abs_dir.glob('*' + ext)]
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
                            p1_full_path_source_file_xls = os.path.join(some_abs_dir, ext_file_l[0])
                            return prfx, p1_full_path_source_file_xls
                        else:
                            view_filename_prefix_inconsistent_with_contract_nr(p1_contract_nr, prfx)
                            return None, None
                # p1_contract_nr has not been populated, probably running the program for the first time
                p1_full_path_source_file_xls = os.path.join(some_abs_dir, ext_file_l[0])
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
    global p1_contract_abs_dir
    global p1_full_path_source_file_xls
    global p1_program_info_f
    global p1_program_info_d
    global p1_initial_xls_contract_file
    global p1_contract_nr
    global p1_contract_abs_dir

    # look for a single xls contract file in the root directory
    p1_contract_nr, p1_full_path_source_file_xls = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
        p0_root_abs_dir, '.xls')

    if not p1_contract_nr or not p1_full_path_source_file_xls:
        select_new_contract()
        return
    else:

        p1_contract_abs_dir = os.path.join(p0_root_abs_dir, 'data/', p1_contract_nr)

        # If the directory does not exist yet, process_default_contract it
        if not os.path.exists(p1_contract_abs_dir):
            try:
                os.mkdir(p1_contract_abs_dir, mode = 0o700)
            except OSError:
                raise

        # If the directory pre-existed, check if it is coherently populated
        contract_nr_l, filename_source_xls_l = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
            p1_contract_abs_dir, '.xls')

        # check for name consistency
        if contract_nr_l:
            if contract_nr_l != p1_contract_nr:
                view_filename_prefix_inconsistent_with_contract_nr(p1_contract_nr, contract_nr_l)

        # if a xls contract file does not exist in contract_dir, copy from the root xls file
        if not filename_source_xls_l:
            # make a copy in the directory that has just been created
            shutil.copy(p1_full_path_source_file_xls, p1_contract_abs_dir)
            # have p1_full_path_source_file_xls now point to the program repository
            _, p1_full_path_source_file_xls = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
                p1_contract_abs_dir, '.xls')
            print(f'p1: re-building from root xls contract: {p1_full_path_source_file_xls}')

    document_in_program_info_json()


def document_in_program_info_json():
    # document the info in program-info.json
    p1_program_info_d['p1_contract_nr'] = p1_contract_nr
    p1_program_info_d['p1_initial_xls'] = p1_initial_xls_contract_file
    p1_program_info_d['p1_full_path_source_file_xls'] = p1_full_path_source_file_xls
    with open(p1_program_info_f, 'w') as fw:
        json.dump(p1_program_info_d, fw, ensure_ascii = False)


def load_p1_all_products_to_be_processed_set():
    global p1_contract_info_d
    global p1_contract_info_f
    global p1_all_products_to_be_processed_set
    if not p1_contract_info_d:
        p1_contract_info_f = os.path.join(p1_contract_abs_dir, 'p1_' + p1_contract_nr + '_contract-info.json')
        with open(p1_contract_info_f) as f1:
            p1_contract_info_d = json.load(f1)
    p1_all_products_to_be_processed_set = p1_contract_info_d['p1_all_products_to_be_processed_set']
    if p1_all_products_to_be_processed_set:
        return True


def load_p1_search_reg_ex_l():
    with open(indicators_csv) as f:
        my_dict_reader = csv.DictReader(f)
        for row in my_dict_reader:
            temp_dict = dict(row)
            p1_search_reg_ex_l.append(temp_dict)
    if p1_search_reg_ex_l:
        return True


def display_p1_search_reg_ex_l():
    if load_p1_search_reg_ex_l():
        pprint.pprint(p1_search_reg_ex_l)


def display_p1_all_products_to_be_processed_set():
    if load_p1_all_products_to_be_processed_set():
        pprint.pprint(p1_all_products_to_be_processed_set)


def load_p1b_indics_from_contract_l():
    global p1b_indics_from_contract_l
    global p1_contract_info_d
    if not p1_contract_info_d:
        if not p1_load_contract_info_d():
            print('p1 has not run successfully')
    filename = p1_contract_info_d['p1b_indics_from_contract_l']
    with open(os.path.join(p1_contract_abs_dir, filename)) as f1b:
        p1b_indics_from_contract_l = json.load(f1b)
        return True


def display_p1b_indics_from_contract_l():
    if load_p1b_indics_from_contract_l():
        pprint.pprint(p1b_indics_from_contract_l)


def display_p1c_all_relevant_data():
    global p1c_prods_w_same_key_set
    global p1_contract_info_d
    if not p1_contract_info_d:
        if not p1_load_contract_info_d():
            print('p1 has not run successfully')
    filename = p1_contract_info_d['p1c_all_relevant_data']
    with open(os.path.join(p1_contract_abs_dir, filename)) as f1c:
        p1c_prods_w_same_key_set = f1c.read()
    print(p1c_prods_w_same_key_set)


def display_p1d_common_indics_l():
    global p1d_common_indics_l
    global p1_contract_info_d
    if not p1_contract_info_d:
        if not p1_load_contract_info_d():
            print('p1 has not run successfully')
    filename = p1_contract_info_d['p1d_extract_common']
    with open(os.path.join(p1_contract_abs_dir, filename)) as f1d:
        p1d_common_indics_l = json.load(f1d)
    pprint.pprint(p1d_common_indics_l)


def load_p1e_specific_fields_d_of_d():
    global p1e_specific_fields_d_of_d
    global p1_contract_info_d
    if not p1_contract_info_d:
        if not p1_load_contract_info_d():
            print('p1 has not run successfully')
    filename = p1_contract_info_d['p1e_extract_specifics']
    with open(os.path.join(p1_contract_abs_dir, filename)) as f1e:
        p1e_specific_fields_d_of_d = json.load(f1e)
    if p1e_specific_fields_d_of_d:
        return True


def display_p1e_specific_fields_d_of_d():
    if load_p1e_specific_fields_d_of_d():
        pprint.pprint(p1e_specific_fields_d_of_d)


def document_in_contract_info_json(key, filename):
    global p1_contract_info_d
    global p1_contract_abs_dir
    p1_contract_info_d[key] = filename
    f = os.path.join(p1_contract_abs_dir, p1_contract_info_f)
    with open(f, 'w') as fi:
        json.dump(p1_contract_info_d, fi, ensure_ascii = False)


def view_too_many_ext_files_in_directory(xls_file_l, ext):
    print(f"\n{len(xls_file_l)} {ext} files are present, that's too many, exiting\n")


def view_filename_prefix_inconsistent_with_contract_nr(cntrct_nr, prfx):
    print(f'\nIncorrect! The file in {cntrct_nr} starts with {prfx}\n')


def view_file_not_in_directory():
    print(f'\nThe xls file corresponding to {p1_contract_nr} contract is not present, exiting\n')


def view_a_prefix_could_not_be_read_from_filename_ext():
    print('A prefix could not be display_sub_processes_output from filename ext')


def display_p1_contract_info_d():
    global p1_contract_info_d
    print('~~~ Reading contract-info global value ~~~')
    pprint.pprint(p1_contract_info_d)
    print('~~~ Finished reading contract-info global value ~~~')


def display_p1_contract_info_f():
    # global p1_contract_info_f
    # p1_contract_info_f = os.path.join(p1_contract_abs_dir, 'p1_' + p1_contract_nr + '_contract-info.json')
    if p1_contract_info_f:
        if os.path.isfile(p1_contract_info_f):
            print('~~~ Reading contract-info.json file contents ~~~')
            with open(p1_contract_info_f) as f:
                # print(f.read_program_info())
                pprint.pprint(f.read())
            print('~~~ File contract-info.json closed ~~~')
    else:
        print(f'\nFile {p1_contract_info_f} not built yet\n')


def display_p1_program_info_d():
    global p1_program_info_d
    print('~~~ Reading program-info global value ~~~')
    pprint.pprint(p1_program_info_d)
    print('~~~ Finished reading program-info global value ~~~')


def display_p1_program_info_f():
    global p1_program_info_f
    print('~~~ Reading program-info.json file contents')
    with open(p1_program_info_f) as f:
        pprint.pprint(f.read())
    print('File program-info.json closed ~~~')


def report_selected_file_is_not_xls(filename):
    print(f'\nSelected file {filename} extension is not \'.xls\'\n')


def read_dirs(walk_abs_dir):
    global p1_contract_abs_dir

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
    else:
        return None


def p1_select_contract_main_context_func():
    if p0_load_program_info_d():
        display_dirs(p0_root_abs_dir + '/data/')
        print('~~~ Now processing contract #: ', p1_contract_nr if p1_contract_nr else None)
        print('>>> Select action: ')
    else:
        print('File \'program-info.json\' could not be loaded')


def p1_select_contract_display_context_func():
    if p0_load_program_info_d():
        display_dirs(p0_root_abs_dir + '/data/')
        print('~~~ Select contract / Display ~~~')
    else:
        print('File \'program-info.json\' could not be loaded')


context_func_d = {
    'select_contract': p1_select_contract_main_context_func,
    'display_sub_processes_output': p1_select_contract_display_context_func,
}


def init():
    global p1_program_info_f
    # initializing globals necessary for all functions
    p1_program_info_f = os.path.join(p0_root_abs_dir, 'program-info.json')

    # initializing menus last, so that context functions display most recent information
    p.menu = 'select_contract'
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': process_default_contract,
            '2': display_or_load_output_overview,
            '3': select_new_contract,
            '4': delete_all_data_on_selected_contract,
            '7': display_sub_processes_output,
            '8': display_p1_program_info_d,
            '9': display_p1_program_info_f,
            'b': p.back_to_main,
            'q': p.normal_exit,
        },
        'display_sub_processes_output': {
            '1': display_p1_search_reg_ex_l,
            '2': display_p1_all_products_to_be_processed_set,
            '3': display_p1b_indics_from_contract_l,
            '4': display_p1c_all_relevant_data,
            '5': display_p1d_common_indics_l,
            '6': display_p1e_specific_fields_d_of_d,
            'b': p.back,
            'q': p.normal_exit,
        }
    }
    if not p.main_menus:
        p.main_menus = p.menus
    if __name__ == '__main__':
        p.mod_lev_1_menu = p.menu
        p.mod_lev_1_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
