#!/usr/bin/env python3
# p1_select_contract.py
import json
import os
import pathlib
import pprint
import re
import shutil
import sys
from tkinter.filedialog import askopenfilename
import xlrd
import m_menus as m

# globals that need to be reset when a new contract is processed
all_products_to_be_processed_set = set()
doc_setup_d = {}
p1_cntrct_abs_dir = ''  # directory where a copy of the xls contract file and contract extracted data is
p1_cntrct_info_d = {}
p1_cntrct_info_f = ''
p1_d = {}
p1_search_reg_ex_l = []
p1b_indics_from_contract_l = []
p1c_prods_w_same_key_set = {}  # make a dictionary key= info, value = sets of prods with that key
p1d_common_indics_l = []
p1e_specific_fields_d_of_d = {}
prog_info_json_f = ''


def program_info_d_load_o_create():
    """
    Loads p1_d['cntrct_nr'], p1_d['file_xls'], and p1_cntrct_abs_dir from program-info.json
    Test:
    (i) json and file already in repository
    (ii) re-create from initial file as per contract-info.json
    (iii) point at file
    """
    global prog_info_json_f
    global p1_d
    global p1_cntrct_abs_dir

    # If the data directory does not exist, create it
    data_abs_dir = os.path.join(m.root_abs_dir, 'data')
    if not pathlib.Path(data_abs_dir).exists():
        os.mkdir(data_abs_dir)

    prog_info_json_f = os.path.join(m.root_abs_dir, 'program-info.json')
    if pathlib.Path(prog_info_json_f).exists():
        # then load the info from (i) the repository
        # or (ii) re-create it from the initial file
        with open(prog_info_json_f, encoding='utf8') as f:
            p1_d = json.load(f)
        if 'cntrct_nr' in p1_d.keys():
            p1_cntrct_abs_dir = os.path.join(os.path.join(m.root_abs_dir, 'data'), f'{p1_d["cntrct_nr"]}')
            if not pathlib.Path(p1_cntrct_abs_dir).exists():
                print(f"|\n| Cannot access {p1_cntrct_abs_dir} directory as in 'program-info.json', creating one\n|")
                os.mkdir(p1_cntrct_abs_dir)
            if 'file_xls' in p1_d.keys():
                file_xls = os.path.join(os.path.join(os.path.join(m.root_abs_dir, 'data'), p1_d['cntrct_nr']),
                                        p1_d['file_xls'])
                if pathlib.Path(file_xls).exists():
                    file_json = os.path.join(os.path.join(os.path.join(m.root_abs_dir, 'data'), p1_d['cntrct_nr']),
                                             p1_d['cntrct_nr'] + '_doc_setup.json')
                    if pathlib.Path(file_json).exists():
                        return True  # (i) json and file already in repository
                    else:
                        # create a _doc_setup.json with default values
                        print(f"|\n| {p1_d['cntrct_nr']}_doc_setup.json not found, creating one with default values\n|")
                        doc_set_up_load_o_create()
                else:
                    print(f"|\n| Cannot access '{file_xls}'\n|")
            else:
                print(f'program-info.json does not contain {p1_cntrct_abs_dir} data')
            print('| Trying to build from fpath_init_xls file in program-info.json')
            if 'fpath_init_xls' in p1_d.keys():
                if pathlib.Path(p1_d['fpath_init_xls']).exists():
                    shutil.copy(p1_d['fpath_init_xls'], p1_cntrct_abs_dir)
                    path, p1_d['file_xls'] = os.path.split(p1_d['fpath_init_xls'])

                    # copy setup file if exists
                    stpf_rel_f = p1_d['cntrct_nr'] + '_doc_setup.json'
                    stpf_abs_src = os.path.join(path, stpf_rel_f)
                    stpf_abs_dest = os.path.join(p1_cntrct_abs_dir, stpf_rel_f)
                    if pathlib.Path(stpf_abs_src).exists() and pathlib.Path(stpf_abs_dest).exists():
                        shutil.copy(stpf_abs_src, p1_cntrct_abs_dir)

                    # also copy template directories, svg and json files that might exists
                    _, dirs, _ = next(os.walk(path))
                    if dirs:
                        for some_dir in dirs:
                            shutil.copytree(os.path.join(path, some_dir),
                                            os.path.join(p1_cntrct_abs_dir, some_dir)
                                            )
                    doc_setup_f_ini = os.path.join(path, p1_d['cntrct_nr'] + '_doc_setup.json')
                    if pathlib.Path(doc_setup_f_ini).exists():
                        shutil.copy(doc_setup_f_ini, p1_cntrct_abs_dir)
                    process_selected_contract()
                    return True  # (ii) re-create from initial file as per contract-info.json
                else:
                    print(
                        f"|\n| Cannot access '{p1_d['fpath_init_xls']}' as in 'program-info.json, no such file'\n|")
            else:
                print(f"program-info.json does not contain {p1_d['fpath_init_xls']} data")

        else:
            print(f'program-info.json does not contain {p1_d["cntrct_nr"]} data')
    else:
        print(f'{prog_info_json_f} does not exist, no such file')
    # if select then return true
    step_1__select_a_contract_选择合同号()
    return True  # (iii) point at file


def contract_info_d_load():
    """
    Loads p1_cntrct_info_f into p1_cntrct_info_d, maybe resetting these values
    Will run p1.step_2__select_templates_to_print_选择_编辑标签类型() and p1.process_default_contact() if necessary
    """
    global p1_cntrct_info_d
    global p1_cntrct_info_f
    global p1_cntrct_abs_dir

    if not program_info_d_load_o_create():
        exit()
    else:
        if not p1_cntrct_abs_dir or 'cntrct_nr' not in p1_d.keys():
            process_selected_contract()
    with open(os.path.join(p1_cntrct_abs_dir, '.' + p1_d['cntrct_nr'] + '_contract-info.json'),
              encoding='utf8') as fi:
        p1_cntrct_info_d = json.load(fi)
    return True


def p1_all_products_to_be_processed_set_load():
    global p1_cntrct_info_d
    global p1_cntrct_info_f
    global all_products_to_be_processed_set
    if not p1_cntrct_info_d:
        p1_cntrct_info_f = os.path.join(os.path.join(p1_cntrct_abs_dir, p1_d['cntrct_nr']), '_contract-info.json')
        with open(p1_cntrct_info_f, encoding='utf8') as f1:
            p1_cntrct_info_d = json.load(f1)

    all_products_to_be_processed_set = sorted(p1_cntrct_info_d['all_products_to_be_processed_set'])
    print(all_products_to_be_processed_set)
    if all_products_to_be_processed_set:
        return True


def p1b_indics_from_contract_l_load():
    global p1b_indics_from_contract_l
    global p1_cntrct_info_d
    if not (p1_cntrct_info_d or contract_info_d_load()):
        print('p1 has not run successfully')
    filename = p1_cntrct_info_d['p1b_indics_from_contract_l']
    with open(os.path.join(p1_cntrct_abs_dir, filename), encoding='utf8') as f1b:
        p1b_indics_from_contract_l = json.load(f1b)
        return True


def p1e_specific_fields_d_of_d_n_p3_needed_vars_load():
    global p1e_specific_fields_d_of_d
    global p1_cntrct_info_d
    if not (p1_cntrct_info_d or contract_info_d_load()):
        print('p1 has not run successfully')
    filename = p1_cntrct_info_d['p1e_extract_specifics']
    with open(os.path.join(p1_cntrct_abs_dir, filename), encoding='utf8') as f1e:
        p1e_specific_fields_d_of_d = json.load(f1e)
    if p1e_specific_fields_d_of_d:
        return True


def doc_set_up_load_o_create():
    global p1_cntrct_abs_dir
    global p1_d
    global doc_setup_d

    filename = os.path.join(p1_cntrct_abs_dir, p1_d['cntrct_nr'] + '_doc_setup.json')
    if pathlib.Path(filename).exists():
        with open(filename, encoding='utf8') as f:
            doc_setup_d = json.load(f)
    else:
        doc_setup_d['margin_w'] = 15
        doc_setup_d['margin_h'] = 15
        doc_setup_d['cover_page'] = True
        doc_setup_d['page_1_vert_offset'] = 0
        with open(filename, 'w', encoding='utf8') as f:
            json.dump(doc_setup_d, f, ensure_ascii=False, indent=4)


def dump_contract_info_json(key, filename):
    """ help function to process_selected_contract """
    global p1_cntrct_info_d
    global p1_cntrct_abs_dir
    p1_cntrct_info_d[key] = filename
    f = os.path.join(p1_cntrct_abs_dir, p1_cntrct_info_f)
    with open(f, 'w', encoding='utf8') as fi:
        json.dump(p1_cntrct_info_d, fi, ensure_ascii=False, indent=4)


# noinspection PyPep8Naming,NonAsciiCharacters
def step_1__select_a_contract_选择合同号(test_contract_nr=''):
    """ Help function to build program-info_d"""
    global p1_cntrct_abs_dir
    global p1_d

    ini_xls = ''
    # (p1_d['cntrct_nr'], p1_d['fpath_init_xls'], p1_d['file_xls']) = (None, None, None)
    print('~~~ Step 1: Selecting a contract ~~~')
    print('~~~ Select a contract xls file in the graphic file browser -- mind the browser window could be hidden')
    if test_contract_nr:
        # path = './contract_samples/' + test_contract_nr
        path = os.path.join('contract_samples', test_contract_nr)
        _, _, files = next(os.walk(path))
        for file in files:
            path_f, file_ext = os.path.split(file)
            _, ext = os.path.splitext(file_ext)
            if ext == '.xls':
                ini_xls = os.path.join(os.path.join('contract_samples', test_contract_nr), file)
        pass
    else:
        ini_xls = askopenfilename(initialdir='contract_samples')
    if not ini_xls:
        return False
    # split path and filename
    path, filename_ext = os.path.split(ini_xls)
    # split filename and extension
    filename, ext = os.path.splitext(filename_ext)
    # check extension indeed is '.xls'
    if ext == '.xls':
        # extract contract_nr
        s = re.match(r'\w+-\w+', filename).group()
        if s:
            print(f"Processing {s}")
            p1_d['cntrct_nr'] = s
            p1_cntrct_abs_dir = os.path.join(os.path.join(m.root_abs_dir, 'data'), p1_d['cntrct_nr'])
            if not pathlib.Path(p1_cntrct_abs_dir).exists():
                os.mkdir(p1_cntrct_abs_dir)
                # do not overwrite an existing contract file
            p1_d['file_xls'] = filename_ext
            p1_d['fpath_init_xls'] = ini_xls
            filename = os.path.join(os.path.join(os.path.join(m.root_abs_dir, 'data'), p1_d['cntrct_nr']),
                                    p1_d['file_xls']
                                    )
            if not pathlib.Path(filename).exists():
                shutil.copy(p1_d['fpath_init_xls'], p1_cntrct_abs_dir)

            # document the info in program-info.json
            with open(prog_info_json_f, 'w', encoding='utf8') as fw:
                # json.dump(p1_d, fw, ensure_ascii = False).encode('utf8', indent = 4)
                json.dump(p1_d, fw, ensure_ascii=False, indent=4)

            # copy setup file if exists
            stpf_rel_f = p1_d['cntrct_nr'] + '_doc_setup.json'
            stpf_abs_src = os.path.join(path, stpf_rel_f)
            stpf_abs_dest = os.path.join(p1_cntrct_abs_dir, stpf_rel_f)
            if pathlib.Path(stpf_abs_src).exists():
                if not pathlib.Path(stpf_abs_dest).exists():
                    shutil.copy(stpf_abs_src, p1_cntrct_abs_dir)

                # also copy template directories, svg and json files that might exists
            _, dirs, _ = next(os.walk(path))
            if dirs:
                for some_dir in dirs:
                    dest_dir = os.path.join(p1_cntrct_abs_dir, some_dir)
                    if not pathlib.Path(dest_dir).exists():
                        shutil.copytree(os.path.join(path, some_dir), dest_dir)
            process_selected_contract()
            return True
        else:  # the prefix has not been checked
            print('A prefix could not be read from filename ext')
            return False
    else:
        print(f'\nSelected file {filename} extension is not \'.xls\'\n')
        return False


def process_selected_contract():
    global p1_cntrct_info_f
    global p1_cntrct_info_d
    global p1_cntrct_abs_dir
    global prog_info_json_f
    global p1_d
    global p1_search_reg_ex_l
    global p1b_indics_from_contract_l
    global p1c_prods_w_same_key_set
    global all_products_to_be_processed_set
    global p1d_common_indics_l
    global p1e_specific_fields_d_of_d

    # reset to zero if these had been loaded from disk before
    p1_search_reg_ex_l = []
    p1b_indics_from_contract_l = []
    p1c_prods_w_same_key_set = {}
    all_products_to_be_processed_set = set()
    p1d_common_indics_l = []
    p1e_specific_fields_d_of_d = {}

    p1_cntrct_info_f = '.' + p1_d['cntrct_nr'] + '_contract-info.json'
    filename = os.path.join(p1_cntrct_abs_dir, p1_cntrct_info_f)
    if pathlib.Path(filename).exists():
        with open(filename, encoding='utf8') as fi:
            p1_cntrct_info_d = json.load(fi)
    else:
        p1_cntrct_info_d = {}

    # setting the name of the -contract.json file
    rel_path_contract_json_f = '.p1a_' + p1_d['cntrct_nr'] + '-contract.json'

    # Creating the json file from the local xls file: opening the xl file
    book = xlrd.open_workbook(
        os.path.join(p1_cntrct_abs_dir, p1_d['file_xls']))
    sheet = book.sheet_by_index(0)

    row = 0
    while not sheet.col_values(0, 0)[row]:  # getting to last row before D1 in col. A
        row += 1

    # Read xls file into memory: p1a_contract_json_d, and disk: p1_cntrct_info_d['p1a_contract_json']
    if sheet.cell(1, 7).value[0:4] == '合同编号':
        p1a_contract_json_d = {'合同编号': sheet.cell(1, 7).value[5:].strip()}  # select data from cell 'H2'
    else:
        sys.exit("Error reading contract XLS file:  expecting to select 合同编号 in cell 'H2'")

    non_decimal = re.compile(r'[^\d.]+')  # necessary to clean formatting characters in XLS cells

    p1a_contract_json_d['l_i'] = []
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
        p1a_contract_json_d['l_i'].append(dict(tmp_dict))
        row += 3

    with open(os.path.join(p1_cntrct_abs_dir, rel_path_contract_json_f), 'w', encoding='utf8') as fc:
        json.dump(p1a_contract_json_d, fc, indent=4, ensure_ascii=False)

    # also write into a text file to validate regex in www.regex101.com
    contract_long_list = ""
    for product in p1a_contract_json_d['l_i']:
        for value in product.values():
            # contract_long_list += (str(value)).strip()
            # contract_long_list += (str(value)).replace(r'\r\n', r'\n')
            contract_long_list += (str(value)).replace('\r', '')
    with open(
            os.path.join(p1_cntrct_abs_dir, '.p1a_' + p1_d['cntrct_nr'] + '-contract.txt'), 'w', encoding='utf8'
    ) as fw:
        fw.write(contract_long_list)

    # populate p1_cntrct_info_d: a structure to store template information, and its corresponding json file
    p1_cntrct_info_d['p1a_contract_json'] = rel_path_contract_json_f

    rx_file_local = os.path.join(os.path.join(m.root_abs_dir, 'common'), 'regular_expressions_local.json')
    rx_file_common = os.path.join(os.path.join(m.root_abs_dir, 'common'), 'regular_expressions_common.json')

    if not os.path.exists(rx_file_local):
        shutil.copy(rx_file_common, rx_file_local)
    with open(rx_file_local, encoding='utf8') as f:
        p1_search_reg_ex_l = json.load(f)

    # harvesting all indicators possibly available in p1a_contract_json_d
    # Read xls file into memory: p1b_indics_from_contract_l,
    #               and disk: p1_cntrct_info_d['p1b_indics_from_contract_l']
    for row_indic in p1_search_reg_ex_l:
        what = row_indic['what']
        how = row_indic['how']
        for prod in p1a_contract_json_d['l_i']:  # inspecting products one by one
            tmp_dct = {  # adding 03.Prod_spec-产品规则 info
                'what': 'xl_prod_spec',
                'where': 'xl_quantity-数量',
                'prod_nr': prod['01.TST_prod_#-需方产品编号'],
                'info': prod["03.Prod_spec-产品规格"]
            }
            p1b_indics_from_contract_l.append(tmp_dct)
            tmp_dct = {  # adding 05.Quantity-数量 info
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
                                'what': what,  # from regular_expressions_local.json : pack, kg, mm, 牌, v_Hz, plstc_bg
                                'where': key,  # xl cell: 10.Tech_spec-技术参数_2
                                'info': indication,  # 1.00    = indic
                                'prod_nr': prod["01.TST_prod_#-需方产品编号"],  # 1050205001#
                            }
                            p1b_indics_from_contract_l.append(tmp_dct)
        p1b_indics_from_contract_l.sort(key=lambda item: item['prod_nr'])
        file_indics = '.p1b_' + p1_d['cntrct_nr'] + '_indics_from_contract_l.json'

        # register in file and object
        dump_contract_info_json('p1b_indics_from_contract_l', file_indics)

        f = os.path.join(p1_cntrct_abs_dir, file_indics)
        with open(f, 'w', encoding='utf8') as f:
            json.dump(p1b_indics_from_contract_l, f, ensure_ascii=False, indent=4)

        # p1c_prods_w_same_key_set: dictionary with key= info, value = sets of prods with that key
        # organize data from p1b_indics_from_contract_l into memory: p1c_all_relevant_data
        #               and disk: p1_cntrct_info_d['p1c_all_relevant_data']
        for row in p1b_indics_from_contract_l:
            # for index, row in c_df.iterrows():  # index is not used
            if (row['what'], row['where'], row['info']) not in p1c_prods_w_same_key_set.keys():
                p1c_prods_w_same_key_set[(row['what'], row['where'], row['info'])] = set()
            p1c_prods_w_same_key_set[(row['what'], row['where'], row['info'])].add(row['prod_nr'])

            # document in all_relevant_data_json
    p1c_file_out_f = '.p1c_' + p1_d['cntrct_nr'] + '_all_relevant_data.txt'
    f = os.path.join(p1_cntrct_abs_dir, p1c_file_out_f)
    with open(f, 'w', encoding='utf8') as f1c:
        # json.dump(p1c_prods_w_same_key_set, f1c, ensure_ascii = False) won't work
        # f1c.write(p1c_prods_w_same_key_set.__str__()) doesn't look pretty
        pprint.PrettyPrinter(indent=2, stream=f1c).pprint(p1c_prods_w_same_key_set)

    dump_contract_info_json('p1c_all_relevant_data', p1c_file_out_f)

    # all_products_to_be_processed
    # Read xls file into memory: all_products_to_be_processed_set,
    #               and disk: p1_cntrct_info_d['all_products_to_be_processed_set']
    for prod in p1a_contract_json_d['l_i']:
        all_products_to_be_processed_set.add(prod["01.TST_prod_#-需方产品编号"])
    dump_contract_info_json('all_products_to_be_processed_set', sorted(list(all_products_to_be_processed_set)))

    # split info from p1c_all_relevant_data into
    # p1d_extract_common
    # p1e_extract_specifics
    for k, v in p1c_prods_w_same_key_set.items():
        # indic is not a  packing quantity and is common to all products
        if k[0] not in ['pack', 'parc', 'u_parc'] and v == all_products_to_be_processed_set:
            p1d_common_indics_l.append(k)
        else:
            for prod in v:
                if p1e_specific_fields_d_of_d.get(prod) is None:
                    p1e_specific_fields_d_of_d[prod] = {}
                p1e_specific_fields_d_of_d[prod][k[0]] = k[2]  # prod_n : 'what' = indic

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
    filename = '.p1d_' + p1_d['cntrct_nr'] + '_extract_common.json'
    f = os.path.join(p1_cntrct_abs_dir, filename)
    with open(f, 'w', encoding='utf8') as p1d_f:
        json.dump(p1d_common_indics_l, p1d_f, ensure_ascii=False, indent=4)

    dump_contract_info_json('p1d_extract_common', filename)

    # indicators specific to one or more products, but not to all: print p1e_specific_fields_d_of_d
    filename = '.p1e_' + p1_d['cntrct_nr'] + '_extract_specifics.json'
    f = os.path.join(p1_cntrct_abs_dir, filename)
    with open(f, 'w', encoding='utf8') as p1e_f:
        json.dump(p1e_specific_fields_d_of_d, p1e_f, ensure_ascii=False, indent=4)

    dump_contract_info_json('p1e_extract_specifics', filename)

    # define page setup
    doc_set_up_load_o_create()

    # document in A1234-456_contract-info.json
    filename = os.path.join(p1_cntrct_abs_dir, p1_cntrct_info_f)
    with open(filename, 'w', encoding='utf8') as fi:
        json.dump(p1_cntrct_info_d, fi, ensure_ascii=False, indent=4)


# Shell interface data & functions #####################################################################################
def select_contract_main_context_func():
    print('~~~ Now editing contract #: ', p1_d['cntrct_nr'] if 'cntrct_nr' in p1_d.keys() else 'None selected')
    print('>>> Select action: ')


context_func_d = {
    'init': select_contract_main_context_func,
    'debug': lambda: 0
}


def init():
    program_info_d_load_o_create()

    # initializing menus last, so that context functions display most recent information
    m.menu = 'init'
    if not m.main_menu:
        m.main_menu = m.menu
    m.menus = {
        m.menu: {
            '1': step_1__select_a_contract_选择合同号,
            '2': process_selected_contract,
            'b': m.back_to_main_退到主程序,
            'q': m.normal_exit_正常出口,
            'd': m.debug,
        },
        'debug': {
            '3': program_info_d_load_o_create,
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
    init()
    m.run()


if __name__ == '__main__':
    main()
