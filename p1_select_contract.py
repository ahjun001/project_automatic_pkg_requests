#!/usr/bin/env python3
# p1_select_contract.py
import csv
import json
import os
import pathlib
import pprint
import sys
import xlrd
import re
import shutil
from tkinter.filedialog import askopenfilename
import p0_menus as p

p0_root_abs_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located
prog_info_json_f = ''
p1_d = {}
p1_cntrct_abs_dir = ''  # directory where a copy of the xls contract file and contract extracted data is


# todo: why does it have to be here?
def load_o_create_program_info_d():
    """
    Loads p1_d['cntrct_nr'], p1_d["fpath_file_xls"], and p1_cntrct_abs_dir from program-info.json
    Test:
    (i) json and file already in repository
    (ii) re-create from initial file as per contract-info.json
    (iii) point at file
    """
    global prog_info_json_f
    global p1_d
    global p1_cntrct_abs_dir

    # If the data directory does not exist, create it
    data_abs_dir = os.path.join(p0_root_abs_dir, 'data')
    if not pathlib.Path(data_abs_dir).exists():
        os.mkdir(data_abs_dir, mode = 0o700)

    prog_info_json_f = os.path.join(p0_root_abs_dir, 'program-info.json')
    if pathlib.Path(prog_info_json_f).exists():
        # then load the info from (i) the repository
        # or (ii) re-create it from the initial file
        with open(prog_info_json_f) as f:
            p1_d = json.load(f)
        if 'cntrct_nr' in p1_d.keys():
            p1_cntrct_abs_dir = p0_root_abs_dir + f'/data/{p1_d["cntrct_nr"]}'
            if pathlib.Path(p1_cntrct_abs_dir).exists():
                if 'fpath_file_xls' in p1_d.keys():
                    if pathlib.Path(p1_d['fpath_file_xls']).exists():
                        return True  # (i) json and file already in repository
                    else:
                        print(f"|\n| Cannot access '{p1_d['fpath_file_xls']}'\n|")
                else:
                    print(f'program-info.json does not contain {p1_d["fpath_file_xls"]} data')
                print('| Trying to build from fpath_init_xls file in program-info.json')
                if 'fpath_init_xls' in p1_d.keys():
                    if pathlib.Path(p1_d['fpath_init_xls']).exists():
                        shutil.copy(p1_d['fpath_init_xls'], p1_cntrct_abs_dir)
                        _, filename_ext = os.path.split(p1_d['fpath_init_xls'])
                        p1_d['fpath_file_xls'] = os.path.join(p1_cntrct_abs_dir, filename_ext)
                        return True  # (ii) re-create from initial file as per contract-info.json
                    else:
                        print(
                            f"|\n| Cannot access '{p1_d['fpath_init_xls']}' as in 'program-info.json, no such file'\n|")
                else:
                    print(f'program-info.json does not contain {p1_d["fpath_init_xls"]} data')
            else:
                os.mkdir(p1_cntrct_abs_dir, mode = 0o700)
                print(f"|\n| Cannot access '{p1_cntrct_abs_dir}' as in 'program-info.json, no such directory'\n|")

        else:
            print(f'program-info.json does not contain {p1_d["cntrct_nr"]} data')
    # else:
    print(f'{prog_info_json_f} does not exist, no such file')
    # (iii) point at file
    select_new_contract()
    return True  # Todo: be more rigorous


# local path to contract-info.json file
p1_cntrct_info_d = {}
p1_cntrct_info_f = ''
page_setup_d = {}
p1_search_reg_ex_l = []
indicators_csv = os.path.join(p0_root_abs_dir + '/common', 'indicators.csv')
p1_all_products_to_be_processed_set = set()
p1b_indics_from_contract_l = []
p1c_prods_w_same_key_set = {}  # make a dictionary key= info, value = sets of prods with that key
p1d_common_indics_l = []
p1e_specific_fields_d_of_d = {}


def check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(some_abs_dir, ext, check_prefix = True):
    """
        To check prefix, this requires that p1_d['cntrct_nr'] has been initialized
        """
    global p1_cntrct_abs_dir
    global prog_info_json_f
    global p1_d
    global p1_cntrct_info_d
    global p1_cntrct_info_f

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
                    c_nr = p1_d['cntrct_nr'] if 'cntrct_nr' in p1_d.keys() else ''
                    if c_nr:
                        # if prefix and p1_d['cntrct_nr'] match, return prefix, filename
                        if prfx == p1_d['cntrct_nr']:
                            p1_d["fpath_file_xls"] = os.path.join(some_abs_dir, ext_file_l[0])
                            return prfx, p1_d["fpath_file_xls"]
                        else:
                            print(f'\nIncorrect! The file in {p1_d["cntrct_nr"]} starts with {prfx}\n')
                            return None, None
                # p1_d['cntrct_nr'] has not been populated, probably running the program for the first time
                p1_d["fpath_file_xls"] = os.path.join(some_abs_dir, ext_file_l[0])
                return prfx, p1_d["fpath_file_xls"]
            # the prefix has not been checked
            else:
                print('A prefix could not be read from filename ext')
                return None, None
        # but also there maybe no ext file in the cntrct_nr directory
        elif len(ext_file_l) == 0:
            # view_file_not_in_directory()
            return None, None
        # or there maybe more than one, which would not be the canonical situation
        else:
            print(f"\n{len(ext_file_l)} {ext} files are present, that's too many, exiting\n")
            return None, None
    # if the cntrct_nr directory does not exist, return False
    else:
        return None, None


def dump_program_info_json():
    global prog_info_json_f
    global p1_d
    # document the info in program-info.json
    with open(prog_info_json_f, 'w') as fw:
        json.dump(p1_d, fw, ensure_ascii = False)


def select_new_contract():
    global p1_cntrct_abs_dir
    global p1_d

    (p1_d['cntrct_nr'], p1_d['fpath_init_xls'], p1_d["fpath_file_xls"]) = (None, None, None)
    # pick a new xls contract source file with the tkinter browser
    print('~~~ Select a filename in graphic file browser -- check if window is hidden')
    ini_xls = askopenfilename()
    if not ini_xls:
        return
    p1_d['fpath_init_xls'] = ini_xls
    # split path and filename
    path, filename_ext = os.path.split(p1_d['fpath_init_xls'])
    # split filename and extension
    filename, ext = os.path.splitext(filename_ext)
    # check extension indeed is '.xls'
    if ext == '.xls':
        # extract contract_nr
        s = re.match(r'\w+-\d+', filename).group()
        if s:
            p1_d['cntrct_nr'] = s
            p1_cntrct_abs_dir = os.path.join(p0_root_abs_dir + '/data/' + p1_d['cntrct_nr'])
            p1_d["fpath_file_xls"] = os.path.join(p1_cntrct_abs_dir, filename_ext)
            if not pathlib.Path(p1_cntrct_abs_dir).exists():
                os.mkdir(p1_cntrct_abs_dir, mode = 0o700)
                # do not overwrite an existing contract file
            if not pathlib.Path(p1_d["fpath_file_xls"]).exists():
                shutil.copy(p1_d['fpath_init_xls'], p1_cntrct_abs_dir)
        # the prefix has not been checked
        else:
            print('A prefix could not be read from filename ext')
            return
        # create_a_new_label_kind 'p1_cntrct_abs_dir'
        dump_program_info_json()
    else:
        print(f'\nSelected file {filename} extension is not \'.xls\'\n')


def build_program_info_d_from_root_xls_file_or_ask_open_file():
    global p1_cntrct_abs_dir
    global prog_info_json_f
    global p1_d
    global p1_cntrct_abs_dir

    # look for a single xls contract file in the root directory
    p1_d['cntrct_nr'], p1_d['fpath_init_xls'] = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
        p0_root_abs_dir, '.xls')

    if not p1_d['cntrct_nr'] or not p1_d['fpath_init_xls']:
        select_new_contract()
        return
    else:

        p1_cntrct_abs_dir = os.path.join(p0_root_abs_dir, 'data/', p1_d['cntrct_nr'])

        # If the directory does not exist yet, create it
        if not pathlib.Path(p1_cntrct_abs_dir).exists():
            try:
                os.mkdir(p1_cntrct_abs_dir, mode = 0o700)
            except OSError:
                raise

        # If the directory pre-existed, check if it is coherently populated
        contract_nr_l, filename_source_xls_l = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
            p1_cntrct_abs_dir, '.xls')

        # check for name consistency
        if contract_nr_l:
            if contract_nr_l != p1_d['cntrct_nr']:
                print(f'\nIncorrect! The file in {p1_d["cntrct_nr"]} starts with {contract_nr_l}\n')

        # if a xls contract file does not exist in contract_dir, copy from the root xls file
        if not filename_source_xls_l:
            # make a copy in the directory that has just been created
            shutil.copy(p1_d['fpath_init_xls'], p1_cntrct_abs_dir)
            # have p1_d["fpath_file_xls"] now point to the program repository
            _, p1_d["fpath_file_xls"] = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(
                p1_cntrct_abs_dir, '.xls')
            print(f'p1: re-building from root xls contract: {p1_d["fpath_file_xls"]}')

    dump_program_info_json()


def new_put_default_contract_in_repository():
    pass


def put_default_contract_in_repository():
    global p1_cntrct_info_f
    global p1_cntrct_info_d
    global p1_cntrct_abs_dir
    global prog_info_json_f
    global p1_d

    load_o_create_program_info_d()
    # checking if a program-info.json file exists in the root directory
    if pathlib.Path(prog_info_json_f).exists():
        # then load the info it contains in p1_d dictionary
        with open(prog_info_json_f) as f:
            p1_d = json.load(f)
        # check if p1_d['cntrct_nr' helps point to a valid file,
        if p1_d:
            # then check if this one could be working data
            if p1_d['cntrct_nr']:
                p1_cntrct_abs_dir = p0_root_abs_dir + f'/data/{p1_d["cntrct_nr"]}'
                if not os.path.isdir(p1_cntrct_abs_dir):
                    os.mkdir(p1_cntrct_abs_dir)
                _, result = check_sole_cntrct_ext_file_w_o_wo_prefix_is_in_dir(p1_cntrct_abs_dir, '.xls')
                if result:
                    # create_a_new_label_kind all global variables accordingly
                    p1_d["fpath_file_xls"] = result
                # if the data from p1_d cannot be used
                else:
                    # if a valid initial file exists but is not uniquely copied in the repository
                    # todo: write with in p1_d.keys()
                    # if 'fpath_init_xls' in p1_d.keys():  # tests True even if  == ""
                    if 'fpath_init_xls' in p1_d.keys():  # tests True even if  == ""
                        if not pathlib.Path(p1_cntrct_abs_dir).exists():
                            os.mkdir(p1_cntrct_abs_dir, mode = 0o700)
                        p1_d['fpath_init_xls'] = p1_d['fpath_init_xls']
                        shutil.copy(p1_d['fpath_init_xls'], p1_cntrct_abs_dir)
                        _, filename_ext = os.path.split(p1_d['fpath_init_xls'])
                        p1_d["fpath_file_xls"] = os.path.join(p1_cntrct_abs_dir, filename_ext)
                    else:
                        # cannot do much else with this info, abandon and start-over
                        del p1_d['cntrct_nr']
                        build_program_info_d_from_root_xls_file_or_ask_open_file()
        # if program-info.json doesn't point to a valid ./data/p1_d['cntrct_nr'] and xls file, then rebuild
        else:
            build_program_info_d_from_root_xls_file_or_ask_open_file()
    # if program-info.json does not exist
    else:
        build_program_info_d_from_root_xls_file_or_ask_open_file()


# todo: load_o_create_contract_info_d
def load_contract_info_d():
    """
    Loads p1_cntrct_info_f into p1_cntrct_info_d, maybe resetting these values
    Will run p1.init() and p1.process_default_contact() if necessary
    """
    global p1_cntrct_info_d
    global p1_cntrct_info_f
    global p1_cntrct_abs_dir

    if not load_o_create_program_info_d():
        exit()
    else:
        if not p1_cntrct_abs_dir or 'cntrct_nr' not in p1_d.keys():
            # todo: why process here?
            process_default_contract()
    with open(os.path.join(p1_cntrct_abs_dir, p1_d['cntrct_nr'] + '_contract-info.json')) as fi:
        p1_cntrct_info_d = json.load(fi)
    return True


def display_or_load_output_overview():
    if load_contract_info_d():
        display()


def display():
    if p1_cntrct_info_d:
        display_p1_cntrct_info_d()
    elif p1_cntrct_info_f:
        print('trying to read_program_info from disk:')
        display_p1_program_info_f()
    else:
        print('p1 has not run or data cannot be loaded from disk:')


def delete_all_data_on_selected_contract():
    global p1_d
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
                    if drs[int(s)] == p1_d['cntrct_nr']:
                        print(
                            '\n\t!!! Erasing current directory\n'
                            '\tthis will also delete_all_data_on_selected_contract program-info.json\n'
                            '\tand start as if repository is empty !!!'
                        )
                        os.remove(os.path.join(p0_root_abs_dir, 'program-info.json'))
                        p1_d = {'cntrct_nr': ''}
                    shutil.rmtree(p0_root_abs_dir + '/data/' + drs[int(s)])
                    break
                else:
                    print('Integer, but not an option, try again')
            except ValueError:
                print('That\'s not an integer, try again')


def load_p1_all_products_to_be_processed_set():
    global p1_cntrct_info_d
    global p1_cntrct_info_f
    global p1_all_products_to_be_processed_set
    if not p1_cntrct_info_d:
        p1_cntrct_info_f = os.path.join(p1_cntrct_abs_dir, p1_d['cntrct_nr'] + '_contract-info.json')
        with open(p1_cntrct_info_f) as f1:
            p1_cntrct_info_d = json.load(f1)
    p1_all_products_to_be_processed_set = p1_cntrct_info_d['p1_all_products_to_be_processed_set']
    if p1_all_products_to_be_processed_set:
        return True


def display_p1_all_products_to_be_processed_set():
    if load_p1_all_products_to_be_processed_set():
        pprint.pprint(p1_all_products_to_be_processed_set)


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


def load_p1b_indics_from_contract_l():
    global p1b_indics_from_contract_l
    global p1_cntrct_info_d
    if not p1_cntrct_info_d:
        if not load_contract_info_d():
            print('p1 has not run successfully')
    filename = p1_cntrct_info_d['p1b_indics_from_contract_l']
    with open(os.path.join(p1_cntrct_abs_dir, filename)) as f1b:
        p1b_indics_from_contract_l = json.load(f1b)
        return True


def display_p1b_indics_from_contract_l():
    if load_p1b_indics_from_contract_l():
        pprint.pprint(p1b_indics_from_contract_l)


def display_p1c_all_relevant_data():
    global p1c_prods_w_same_key_set
    global p1_cntrct_info_d
    if not p1_cntrct_info_d:
        if not load_contract_info_d():
            print('p1 has not run successfully')
    filename = p1_cntrct_info_d['p1c_all_relevant_data']
    with open(os.path.join(p1_cntrct_abs_dir, filename)) as f1c:
        p1c_prods_w_same_key_set = f1c.read()
    print(p1c_prods_w_same_key_set)


def display_p1d_common_indics_l():
    global p1d_common_indics_l
    global p1_cntrct_info_d
    if not p1_cntrct_info_d:
        if not load_contract_info_d():
            print('p1 has not run successfully')
    filename = p1_cntrct_info_d['p1d_extract_common']
    with open(os.path.join(p1_cntrct_abs_dir, filename)) as f1d:
        p1d_common_indics_l = json.load(f1d)
    pprint.pprint(p1d_common_indics_l)


def load_p1e_specific_fields_d_of_d_n_p3_needed_vars():
    global p1e_specific_fields_d_of_d
    global p1_cntrct_info_d
    if not p1_cntrct_info_d:
        if not load_contract_info_d():
            print('p1 has not run successfully')
    filename = p1_cntrct_info_d['p1e_extract_specifics']
    with open(os.path.join(p1_cntrct_abs_dir, filename)) as f1e:
        p1e_specific_fields_d_of_d = json.load(f1e)
    if p1e_specific_fields_d_of_d:
        return True


def display_p1e_specific_fields_d_of_d():
    if load_p1e_specific_fields_d_of_d_n_p3_needed_vars():
        pprint.pprint(p1e_specific_fields_d_of_d)


def load_o_create_page_set_up():
    global p1_cntrct_abs_dir
    global p1_d
    global page_setup_d

    filename = os.path.join(p1_cntrct_abs_dir, p1_d['cntrct_nr'] + '_page_setup.json')
    if pathlib.Path(filename).exists():
        with open(filename) as f:
            page_setup_d = json.load(f)
    else:
        page_setup_d['margin_w'] = 15
        page_setup_d['margin_h'] = 15
        with open(filename, 'w') as f:
            json.dump(page_setup_d, f, ensure_ascii = False)


def dump_contract_info_json(key, filename):
    global p1_cntrct_info_d
    global p1_cntrct_abs_dir
    p1_cntrct_info_d[key] = filename
    f = os.path.join(p1_cntrct_abs_dir, p1_cntrct_info_f)
    with open(f, 'w') as fi:
        json.dump(p1_cntrct_info_d, fi, ensure_ascii = False)


def view_file_not_in_directory():
    print(f'\nThe xls file corresponding to {p1_d["cntrct_nr"]} contract is not present, exiting\n')


def display_p1_cntrct_info_d():
    global p1_cntrct_info_d
    print('~~~ Reading contract-info global value ~~~')
    pprint.pprint(p1_cntrct_info_d)
    print('~~~ Finished reading contract-info global value ~~~')


def display_p1_cntrct_info_f():
    # global p1_cntrct_info_f
    # p1_cntrct_info_f = os.path.join(p1_cntrct_abs_dir, p1_d['cntrct_nr'] + '_contract-info.json')
    if p1_cntrct_info_f:
        if os.path.isfile(p1_cntrct_info_f):
            print('~~~ Reading contract-info.json file contents ~~~')
            with open(p1_cntrct_info_f) as f:
                # print(f.read_program_info())
                pprint.pprint(f.read())
            print('~~~ File contract-info.json closed ~~~')
    else:
        print(f'\nFile {p1_cntrct_info_f} not built yet\n')


def display_p1_program_info_d():
    global p1_d
    print('~~~ Reading program-info global value ~~~')
    pprint.pprint(p1_d)
    print('~~~ Finished reading program-info global value ~~~')


def display_p1_program_info_f():
    global prog_info_json_f
    print('~~~ Reading program-info.json file contents')
    with open(prog_info_json_f) as f:
        pprint.pprint(f.read())
    print('File program-info.json closed ~~~')


def read_dirs(walk_abs_dir):
    global p1_cntrct_abs_dir

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


def process_default_contract():
    global p1_cntrct_info_f
    global p1_cntrct_info_d
    global p1_cntrct_abs_dir
    global prog_info_json_f
    global p1_d
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

    # todo: why load at this point?, that was good for intermediary process, no longer needed
    # load contract-info.json file if exists
    p1_cntrct_info_f = p1_d['cntrct_nr'] + '_contract-info.json'
    filename = os.path.join(p1_cntrct_abs_dir, p1_cntrct_info_f)
    if pathlib.Path(filename).exists():
        with open(filename) as fi:
            p1_cntrct_info_d = json.load(fi)
    else:
        p1_cntrct_info_d = {}

    # the name of the -contract.json file can now be set
    rel_path_contract_json_f = '.p1a_' + p1_d['cntrct_nr'] + '-contract.json'

    # Creating the json file from the local xls file: opening the xl file
    book = xlrd.open_workbook(p1_d["fpath_file_xls"])
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

    with open(os.path.join(p1_cntrct_abs_dir, rel_path_contract_json_f), 'w') as fc:
        json.dump(contract_json_d, fc, ensure_ascii = False)
    # populate p1_cntrct_info_d: a structure to store label information, and its corresponding json file
    p1_cntrct_info_d['p1a_contract_json'] = rel_path_contract_json_f

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
        file_indics = '.p1b_' + p1_d['cntrct_nr'] + '_indics_from_contract_l.json'

        # register in file and object
        dump_contract_info_json('p1b_indics_from_contract_l', file_indics)

        f = os.path.join(p1_cntrct_abs_dir, file_indics)
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
    p1c_file_out_f = '.p1c_' + p1_d['cntrct_nr'] + '_all_relevant_data.txt'
    f = os.path.join(p1_cntrct_abs_dir, p1c_file_out_f)
    with open(f, 'w') as f1c:
        # json.dump(p1c_prods_w_same_key_set, f1c, ensure_ascii = False) won't work
        # f1c.write(p1c_prods_w_same_key_set.__str__()) doesn't look pretty
        pprint.PrettyPrinter(indent = 2, stream = f1c).pprint(p1c_prods_w_same_key_set)

    dump_contract_info_json('p1c_all_relevant_data', p1c_file_out_f)

    # p1c_build_set_of_all_products_to_be_processed
    for prod in contract_json_d['l_i']:
        p1_all_products_to_be_processed_set.add(prod["01.TST_prod_#-需方产品编号"])
    dump_contract_info_json('p1_all_products_to_be_processed_set', sorted(list(p1_all_products_to_be_processed_set)))

    # p6_split_between p6_common_indics and p6_specific_indics
    for k, v in p1c_prods_w_same_key_set.items():
        # indic is not a  packing quantity and is common to all products
        if k[0] != 'pack_qty' and v == p1_all_products_to_be_processed_set:
            if k[3]:  # todo: check why this sometimes does not happen
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
    filename = '.p1d_' + p1_d['cntrct_nr'] + '_extract_common.json'
    f = os.path.join(p1_cntrct_abs_dir, filename)
    with open(f, 'w') as p1d_f:
        json.dump(p1d_common_indics_l, p1d_f, ensure_ascii = False)

    dump_contract_info_json('p1d_extract_common', filename)

    # indicators specific to one or more products, but not to all: print p1e_specific_fields_d_of_d
    filename = '.p1e_' + p1_d['cntrct_nr'] + '_extract_specifics.json'
    f = os.path.join(p1_cntrct_abs_dir, filename)
    with open(f, 'w') as p1e_f:
        json.dump(p1e_specific_fields_d_of_d, p1e_f, ensure_ascii = False)

    dump_contract_info_json('p1e_extract_specifics', filename)

    # define page setup
    load_o_create_page_set_up()

    # document in A1234-456_contract-info.json
    filename = os.path.join(p1_cntrct_abs_dir, p1_cntrct_info_f)
    with open(filename, 'w') as fi:
        json.dump(p1_cntrct_info_d, fi, ensure_ascii = False)


def select_contract_main_context_func():
    if load_o_create_program_info_d():
        print('~~~ Now processing contract #: ', p1_d['cntrct_nr'] if 'cntrct_nr' in p1_d.keys() else None)
        print('>>> Select action: ')
    else:
        print('|\n| File \'program-info.json\' could not be loaded,\n|')


def select_contract_debug_func():
    if load_o_create_program_info_d():
        display_dirs(p0_root_abs_dir + '/data/')
        print('~~~ Select contract / Display ~~~')
    else:
        print('File \'program-info.json\' could not be loaded')


context_func_d = {
    'select_contract': select_contract_main_context_func,
    'debug': select_contract_debug_func,
}


def init():
    # global prog_info_json_f
    # initializing globals necessary for all functions
    # prog_info_json_f = os.path.join(p0_root_abs_dir, 'program-info.json')
    # todo: put_default_contract_in_repository() here
    load_o_create_program_info_d()

    # initializing menus last, so that context functions display most recent information
    p.menu = 'select_contract'
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '0': load_o_create_program_info_d,
            '1': process_default_contract,
            '2': display_or_load_output_overview,
            '4': delete_all_data_on_selected_contract,
            '8': display_p1_program_info_d,
            '9': display_p1_program_info_f,
            'b': p.back_to_main,
            'q': p.normal_exit_正常出口,
            'd': p.debug,
        },
        'debug': {
            '1': display_p1_search_reg_ex_l,
            '2': display_p1_all_products_to_be_processed_set,
            '3': display_p1b_indics_from_contract_l,
            '4': display_p1c_all_relevant_data,
            '5': display_p1d_common_indics_l,
            '6': display_p1e_specific_fields_d_of_d,
            'b': p.back,
            'q': p.normal_exit_正常出口,
        },
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
