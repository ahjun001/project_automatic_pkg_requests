#!/usr/bin/env python3
# p994_make_all_computational_classes.py
"""
CRUD class for the Json part of the cpl (Contract-Products-Labels)

A Contract is made of:
    - a json number
    - its corresponding xls file
    - its corresponding JSON file
 """
# todo: redefine objects and for all a Create function, maybe a Read, no U, maybe a Delete

import csv
import json
import os
import pprint
import re
import subprocess
import sys
from collections import OrderedDict
import pandas as pd
from mako.template import Template
from xlrd import open_workbook

# from p2_build_directory_n_copy_xls_file import CDirAlreadyExists
import p0g_global_values as g
import p0u_utils as u


class Json:
    def __init__(self):
        u.re_init()
        self.contract_dir_json = os.path.join(g.contract_dir, g.contract_nr + '.json')

        self.menus = {
            "main_menu": {
                '1': self.create,
                '2': self.read_driver_func,
                '4': self.delete,
                '9': self.scenarii,
                'q': self.normal_exit,
            },
            'scenarii': {
                '1': self.scenario_crud_run_n_normal_exit,
                '2': self.scenario_create_existing_directory_exception,
                '3': self.scenario_read_non_existing_directory_exception,
                '4': self.scenario_read_non_existing_json_exception,
                '5': self.scenario_read_too_many_xls_jsons_exception,
                '7': self.scenario_delete_non_existing_json_exception,
                '9': self.back,
                'q': self.normal_exit,
            },
        }
        self.menu = "main_menu"

    def create(self):
        """
            Creating the json file from the local xls file
            """
        contract_dir_xls = os.path.join(g.contract_dir, g.filename_xls)

        if os.path.exists(contract_dir_xls):

            book = open_workbook(contract_dir_xls)
            sheet = book.sheet_by_index(0)

            row = 0
            while not sheet.col_values(0, 0)[row]:  # getting to last row before D1 in col. A
                row += 1

            # get global info
            if sheet.cell(1, 7).value[0:4] == '合同编号':
                contract_in = {'合同编号': sheet.cell(1, 7).value[5:].strip()}  # select data from cell 'H2'
            else:
                sys.exit("Error reading contract XLS file:  expecting to select 合同编号 in cell 'H2'")

            non_decimal = re.compile(r'[^\d.]+')  # necessary to clean formatting characters in XLS cells

            contract_in['l_i'] = []
            while sheet.col_values(0, 0)[row]:  # looping while there is product information
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
                contract_in['l_i'].append(dict(tmp_dict))
                row += 3

            with open(self.contract_dir_json, 'w') as f:
                json.dump(contract_in, f, ensure_ascii = False)

        else:
            raise self.JsonXlsDoesNotExist(f'\nLocal XLS source file {contract_dir_xls} not found\n')

    def read(self):
        """
            read_json() checks if an eligible json file is present in directory,
            then returns a pointer to its data
            """

        if os.path.exists(self.contract_dir_json):
            # list all files and directories present in the cntrct_nr directory
            files_l = os.listdir(g.contract_dir)
            # make the sublist of the files only
            files = []
            for f in files_l:
                if os.path.isfile(os.path.join(g.contract_dir, f)):
                    files.append(f)
            # make the sublist of the files that have an '.xls' extension
            json_file_l = []
            for file in files:
                filename, ext = os.path.splitext(file)
                if ext == '.json':
                    json_file_l.append(file)
            # this sublist should only have one file: copy of the initial source file
            if len(json_file_l) == 1:
                prefix = re.match(r'\w+-\d+', json_file_l[0]).group()
                # check that this file name begin with cntrct_nr
                if prefix == g.contract_nr:
                    with open(self.contract_dir_json) as fr:
                        data = json.load(fr)
                    return data
                else:
                    raise self.JsonFilenamePrefixInconsistentWithDirectory(
                        f'\nIncorrect! The file in {g.contract_nr} starts with {prefix}\n')
            # but there maybe no xls file in the cntrct_nr directory
            elif len(json_file_l) == 0:
                raise self.JsonFileNotInDirectory(
                    f'\nThe xls file corresponding to {g.contract_nr} json is not present, exiting\n')
            # or there maybe more than one, which would not be the canonical situation
            else:
                raise self.JsonTooManyJsonFilesInDirectory(
                    f'\n{len(json_file_l)} json files are present, that\'s too many, exiting\n')

        else:
            raise self.JsonFDoesNotExist(f'\nLocal XLS source file {self.contract_dir_json} not found\n')

    def delete(self):

        """
            Erase cntrct_nr directory and all existing json information that had been build by the program,
            leaves the initial source file intact
            """
        # If the file exist
        if os.path.exists(self.contract_dir_json):
            try:
                # erase it
                os.remove(self.contract_dir_json)
            except OSError:
                raise
        # if the directory does not exist, raise an error and exit program
        else:
            raise self.JsonFileNotInDirectory(f'\nCannot delete file {g.contract_nr}: does not exist\n')

    ####################
    # Exceptions
    ####################
    class JsonXlsDoesNotExist(Exception):
        pass

    class JsonTooManyJsonFilesInDirectory(Exception):
        pass

    class JsonFileNotInDirectory(Exception):
        pass

    class JsonFilenamePrefixInconsistentWithDirectory(Exception):
        pass

    class JsonFDoesNotExist(Exception):
        pass

    ####################
    # Driver functions
    ####################
    def run(self):

        while True:
            print(f'Currently working on: {g.contract_nr}\n')
            # display menu with data from menus dict
            for k, v in self.menus.get(self.menu).items():
                print(f'{k}. {v.__name__}')
            choice = input("\nEnter an option: ")
            action = self.menus[self.menu].get(choice)
            if choice in []:
                action(self)
            else:
                if action:
                    action()
                else:
                    print(f'\n{choice} is not a valid choice\n')

    def read_driver_func(self):
        data = self.read()
        if data:
            # print(f'data is of type {type(data)}')
            print(data)
        else:
            print('Read error')

    def back(self):
        os.system('clear')
        print('Returning to main menu ---')
        self.menu = 'main_menu'

    @staticmethod
    def normal_exit():
        os.system('clear')
        print('Exiting program ---')
        sys.exit(0)

    def scenarii(self):
        os.system('clear')
        print('Entering scenarii ---')
        self.menu = 'scenarii'

    def scenario_crud_run_n_normal_exit(self):
        self.create()
        self.read()
        self.delete()

    def scenario_create_existing_directory_exception(self):
        self.create()
        self.create()

    def scenario_read_non_existing_directory_exception(self):
        if self.read():
            self.delete()
        self.read()

    def scenario_read_non_existing_json_exception(self):
        # create only the directory
        if not os.path.exists(g.contract_dir):
            try:
                # create it
                os.mkdir(g.contract_dir, mode = 0o700)  # create drctry for user only, excluding group & everyone else
                # if the initial source file is present
            except OSError:
                raise
        # if the directory exists, raise an error and exit program
        else:
            # raise CDirAlreadyExists(f"\nCannot create directory {g.cntrct_nr}: already exists\n")
            pass
        # then try to select json, should raise an exception
        self.read()

    def scenario_read_too_many_xls_jsons_exception(self):
        self.create()
        file_in_place = os.path.join(g.contract_dir, 'temp.xls')
        # create a second xls file in directory
        with open(file_in_place, 'w'):
            os.utime(file_in_place, None)
        # try to select, creating an exception
        self.read()

    def scenario_delete_non_existing_json_exception(self):
        self.delete()
        self.delete()


class Indicators:
    def __init__(self):
        self.filename = os.path.join(g.root_dir + '/common', 'indicators.csv')
        if not os.path.exists(self.filename):
            raise self.IndicatorsFileNotFound(f'\nDid not find {self.filename}\n')

    def read(self):
        return pd.read_csv(self.filename, quoting = csv.QUOTE_NONE)

    class IndicatorsFileNotFound(Exception):
        pass


class AllIndctrs:
    def __init__(self, data_d, cators_df):
        self.data_d = data_d
        self.cators_df = cators_df

    def read(self):
        c_l = []
        c2_d = {}  # make a dictionary key= info, value = sets of prods with that key

        # Harvesting all indicators possibly available in the self.data_d
        for (index, row_indic) in self.cators_df.iterrows():  # looping by indicators -- things to be looked for
            what = row_indic['what']
            info_kind = row_indic['info_kind']
            how = row_indic['how']
            for prod in self.data_d['l_i']:  # inspecting products one by one
                tmp_dct = {  # adding 03.Prod_spec-产品规则 info
                    'info_kind': 'spec',
                    'what': '03.Prod_spec',
                    'where': '05.Quantity-数量',
                    'prod_nr': prod['01.TST_prod_#-需方产品编号'],
                    'info': prod["03.Prod_spec-产品规格"]
                }
                c_l.append(tmp_dct)
                tmp_dct = {  # adding 05.Quantity-数量 info
                    'info_kind': 'pack_qty',
                    'what': 'total_qty',
                    'where': '05.Quantity-数量',
                    'prod_nr': prod['01.TST_prod_#-需方产品编号'],
                    'info': int(prod['05.Quantity-数量'])
                }
                c_l.append(tmp_dct)
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
                                c_l.append(tmp_dct)
            c_l.sort(key = lambda item: item['prod_nr'])
            # c_df.sort_values(by = ['prod_nr'])  # todo: redundant remove
            # c2_d = {}  # make a dictionary key= info, value = sets of prods with that key
            for row in c_l:
                # for index, row in c_df.iterrows():  # index is not used
                if (row['info_kind'], row['what'], row['where'], row['info']) not in c2_d.keys():
                    c2_d[(row['info_kind'], row['what'], row['where'], row['info'])] = set()
                c2_d[(row['info_kind'], row['what'], row['where'], row['info'])].add(row['prod_nr'])
        return c2_d

    def display(self):
        pprint.PrettyPrinter(indent = 2).pprint(self.read())


class ProdSet:
    def __init__(self, data):
        self.c2b = set()
        for prod in data['l_i']:
            self.c2b.add(prod["01.TST_prod_#-需方产品编号"])

    def read(self):
        return self.c2b

    def display(self):
        pprint.PrettyPrinter(indent = 2).pprint(self.read())


class CommonIndctrs:
    def __init__(self):
        self.c3a = []

    def write_to_file(self):

        # indicators common to all products
        filename = './data/' + g.contract_nr + '/' + g.contract_nr + '_2_extract_common.txt'
        with open(filename, 'w') as c3a_f:
            for line in self.c3a:
                # c3a_f.write(line.__str__() + '\n')
                for w in line:
                    c3a_f.write('{:_<22}'.format(w))
                c3a_f.write('\n')

        subprocess.Popen(['ls', '-l', filename])
        subprocess.Popen(['cat', filename])


class SpecificIndctrs:
    def __init__(self):
        self.c3b = {}

    def write_to_file(self):
        header = []
        p_list = ['total_qty', 'parc', 'u_parc', 'pack']
        for k, v in self.c3b.items():
            for h in v.keys():
                if h not in p_list:
                    if h not in header:
                        header.append(h)
        header = ['prod_n'] + p_list + sorted(header)

        # indicators specific to one or more products, but not all
        filename = './data/' + g.contract_nr + '/' + g.contract_nr + '_3_extract_prods.csv'
        with open(filename, 'w') as c3b_f:
            for h in header:
                c3b_f.write('{:_<12}'.format(h) + ',')
            c3b_f.write('\n')
            for k, v in self.c3b.items():
                c3b_f.write('{:<12}'.format(k) + ',')
                for h in header[1:]:
                    c3b_f.write('{:<12}'.format(str(v[h])) + ',')
                c3b_f.write('\n')

        # todo: get this to work as well
        # filename = './data/' + g.cntrct_nr + 'info_prod.csv'
        # with open(filename, 'w') as c3b_f:
        #     writer = csv.writer(c3b_f)
        #     for k, v in c3b.items():
        #         writer.writerow([k, v
        # c3b_df = pd.DataFrame.from_dict(data = c3b, orient='index')
        # filename = './data/' + g.cntrct_nr + 'info_prod.csv'
        # c3b_df.to_csv(filename, index = False)

        subprocess.Popen(['ls', '-l', filename])
        subprocess.Popen(['cat', filename])


class Splitter:
    def __init__(self, c2, c2b):  # todo: maybe integrate c2b as it is only used here
        self.c2 = c2
        self.c2b = c2b
        self.c3a = []
        self.c3b = {}

        for k, v in c2.items():
            if k[0] != 'pack_qty' and v == self.c2b:  # indic is not a  packing quantity and is common to all products
                if k[3]:  # todo: check why this sometimes not happens
                    self.c3a.append(k)
            else:
                for prod in v:
                    if self.c3b.get(prod) is None:
                        self.c3b[prod] = {}
                    self.c3b[prod][k[1]] = k[3]  # prod_n : 'what' = indic

        # Checking that numbers are coherent  Todo: put in a different function
        for k, v in self.c3b.items():
            # Checking that packing quantities info are coherent with total_quantity, if not: exit with a message
            if v['total_qty'] != int(v['parc']) * int(v['u_parc']):  # * int(float(v['pack'])):
                print(60 * '*' + '\nIncoherent quantities in xls contract in product: ' + k + '\n' + 60 * '*')
                exit()
            # Checking that under_packing are multiple of parcels (boxes are full), if not: exit the program with a
            # message
            if int(v['u_parc']) % int(float(v['pack'])) != 0:
                print(60 * '*' + '\nUnder-parcels not full in xls contract in product: ' + k + '\n' + 60 * '*')
                exit()

    def display(self):
        print('Splitter c3a:)')
        pprint.PrettyPrinter(indent = 2).pprint(self.c3a)
        print('Splitter c3b:)')
        pprint.PrettyPrinter(indent = 2).pprint(self.c3b)

    def read(self):
        return self.c3a, self.c3b


class ChooseSpecificIndicators:
    def __init__(self, c3b):
        self.c3b = c3b
        self.selection = []
        self.select()  # Todo: definitely fix this, not in place
        columns = ['prod_n'] + self.selection
        self.c4_df = pd.DataFrame(columns = columns)
        cators_df_ = 0
        for k, v in c3b.items():
            lst = [k]
            for c in self.selection:
                lst += [v[c]]
            self.c4_df.loc[cators_df_] = lst
            cators_df_ += 1

    def display(self):
        for index, rows in self.c4_df.iterrows():
            print(index, rows)

    def write_to_file(self):
        self.c4_df.rename(columns = {'03.Prod_spec': 'prod_spec'},
                          inplace = True)  # Mako takes col. header as variables
        filename = os.path.join(g.lbl_dir, 'c4_df.csv')
        self.c4_df.sort_values(by = ['prod_n'], inplace = True)
        self.c4_df.reset_index(drop = True, inplace = True)
        self.c4_df.to_csv(filename, index_label = 'idx')
        # os.system(f'gnome-terminal --window-with-profile="labels" -- less csvtool readable {filename}')

    def select(self):
        # Select which indicators are needed and write in a dedicated json file
        # choices = list(c3b[list(c2b)[1]].keys())
        # questions = [
        #     inquirer.Checkbox('individual specs',
        #                       message = "Select specs to be printed on label, then proceed with 'Enter'",
        #                       choices = choices,
        #                       ),
        # ]
        # answers = inquirer.prompt(questions)['individual specs']
        self.selection = ['03.Prod_spec', 'u_parc', 'plstc_bg']

    def read(self):
        return self.c4_df


def f40_df_to_dct(c4_df):
    """
        This is required to simplify writing more RegEx searches and link them to the Mako template
        The dict contains entries for all searches, most of them not performed but, if no new search is
        added to /data/common/indicators.csv, this allow to write in the Mako template without having to
        re-write code.
    """
    c4_df['idx'] = range(1, len(c4_df) + 1)
    # print(c4_df)
    c4_dct = OrderedDict(c4_df.to_dict('index'))
    # build a list of indicators to complement the dict being built
    cators_df = pd.read_csv(os.path.join(g.root_dir + '/common', 'indicators.csv'))
    with open(os.path.join(g.root_dir + '/common', 'code.txt'), 'w') as f:
        for i in cators_df.index:
            ndc = cators_df['what'][i]
            if ndc not in c4_df.columns:
                f.write(f"{ndc} = v['{ndc}'],\n")
                for v in c4_dct.values():
                    v[ndc] = 0
    return c4_dct


def f50_present_one_reference_label_svg(c4_dct):
    """
    Printing one label so that it can be checked before printing many
    """
    # todo: isolate the separate function, remove body from repository
    with open(os.path.join(g.lbl_dir, 'label_template_header.svg')) as h:
        header = h.read()
    svg_out = os.path.join(g.lbl_dir, 'page_0.svg')
    with open(svg_out, 'w') as f:
        f.write(header)
        label_template = Template(filename = os.path.join(g.lbl_dir, 'label_template_body.svg'),
                                  input_encoding = 'utf-8')
        f51_write_data_in_label_template_item(f, label_template, c4_dct[0])
        f.write('</svg>')
    # subprocess.Popen([r'/usr/bin/google-chrome', '--disable-gpu', '--disable-software-rasterizer', svg_out])
    # subprocess.Popen([r'google-chrome', svg_out])
    subprocess.Popen([r'firefox', svg_out])
    # subprocess.Popen(['cat', os.path.join(g.lbl_dir, f'page_0.svg')])


def f51_write_data_in_label_template_item(f, label_template, v):
    f.write(label_template.render(
        i = v['idx'],
        prod_n = v['prod_n'],
        prod_spec = v['prod_spec'],
        u_parc = v['u_parc'],
        plstc_bg = v['plstc_bg'],
        pack = v['pack'],
        parc = v['parc'],
        brandk = v['brandk'],
        brandd = v['brandd'],
        branddp = v['branddp'],
        kg = v['kg'],
        mm = v['mm'],
        v_Hz = v['v_Hz'],
        r_power = v['r_power'],
        l_flux = v['l_flux'],
        c_tmp = v['c_tmp'],
        c_idx = v['c_idx'],
        b_ang = v['b_ang'],
        p_size = v['p_size'],
        prot_lev = v['prot_lev'],
        serv_lif = v['serv_lif'],
        q_ass = v['q_ass'],
        nut_grade = v['nut_grade'],
        material1 = v['material1'],
        nut_norm = v['nut_norm'],
        material2 = v['material2'],
        nut_spec = v['nut_spec'],
        bg_pr_crgtd_bx = v['bg_pr_crgtd_bx'],
        bg_pr_o_bx = v['bg_pr_o_bx'],
    ))


def f60_suggest_hor_n_vert_spacings_between_labels():
    """
    Print min and max spacing depending on # of labels to be laid in rows & columns
    """
    label_view_box_w, label_view_box_h = f61_get_label_view_box_from_template()
    w = f62_suggest_spacing_calc(g.page_view_box_w, label_view_box_w, 'w')  # first horizontally, w = width
    # print()
    h = f62_suggest_spacing_calc(g.page_view_box_h - g.header_height, label_view_box_h, 'h')  # then vertically
    return label_view_box_w, label_view_box_h, w, h


def f61_get_label_view_box_from_template():
    with open(os.path.join(g.lbl_dir, 'label_template.svg')) as f:
        contents = f.read()
        m = re.search(r'(?<=viewBox=")(\d) (\d) (\d+.*\d*) (\d+\.*\d*)', contents)
        if m.groups()[0] != '0' or m.groups()[1] != '0':
            print("Error in building 'label_template.svg': origin is not (0, 0), exiting program ...")
            exit()
        return float(m.groups()[2]), float(m.groups()[3])  # label_view_box_h, label_view_box_h


def f62_suggest_spacing_calc(lgth, label_view_box, orientation):
    n_of_labels_per_dim = int(lgth // label_view_box)

    # if orientation == 'w':
    #     print(f'Labels width: {label_view_box}')
    #     print("# of labels spacing min,       max")
    # else:
    #     print(f'Labels height: {label_view_box}')

    for i in range(1, n_of_labels_per_dim + 1):
        x = f63_suggest_spacing_func(lgth, label_view_box, i)
        if i == n_of_labels_per_dim:
            m = 0
        else:
            m = f63_suggest_spacing_func(lgth, label_view_box, i + 1) + 1

        # print("{:>11d} {:>10d} {:>10d} ".format(i, m, x))
    return min(10, f63_suggest_spacing_func(lgth, label_view_box, n_of_labels_per_dim))


def f63_suggest_spacing_func(lgth, label_view_box, i):
    return int((lgth - i * label_view_box) / max(1, (i - 1)))


def f64_horizontal_centering_offset(label_view_box_w, spacing_w):
    n_of_labels_per_row = int(g.page_view_box_w // label_view_box_w)
    result = (g.page_view_box_w - n_of_labels_per_row * label_view_box_w - (n_of_labels_per_row - 1) * spacing_w) / 2
    return result


def f70_assemble_all_labels_into_svg(c4_dct, label_view_box_w, label_view_box_h, spacing_w, spacing_h):
    """
    assemble prepared svg files
    output to out.svg
    """
    # from label_template.svg , build header and body templates
    with open(os.path.join(g.lbl_dir, 'label_template.svg')) as f:
        header, sentinel, body = f.read().partition('</metadata>\n')
    # Todo: Label template header should be generated from a file with correct page_view_box w & h
    # with open(os.path.join(g.lbl_dir, 'label_template_header.svg'), 'w') as f:
    #    f.write(header)
    #    f.write(sentinel)
    with open(os.path.join(g.lbl_dir, 'label_template_body.tmp'), 'w') as f:
        f.write(body)
        family = re.search(r'(?<=font-family:)([\w-]+)', body).groups()[0]
        size = re.search(r'(?<=font-size:)(\d+\.*\d*\w*)', body).groups()[0]
        style = re.search(r'(?<=font-style:)([\w-]+)', body).groups()[0]

    with open(os.path.join(g.lbl_dir, 'label_template_body.tmp')) as fr:
        lines = fr.readlines()
    with open(os.path.join(g.lbl_dir, 'label_template_body.svg'), 'w') as fw:
        for i in range(len(lines) - 1):
            fw.write(lines[i])
    os.remove(os.path.join(g.lbl_dir, 'label_template_body.tmp'))

    assert label_view_box_w + spacing_w <= g.page_view_box_w, \
        "write_labels: ! label + spacing width don't fit in the page"
    assert label_view_box_h + spacing_h <= g.page_view_box_h, \
        'write_labels: ! label + spacing height don\'t fit in the page'

    # printing labels in pages, when a page is full, open a new one
    svg_in = os.path.join(g.lbl_dir, 'label_template_header.svg')
    with open(svg_in) as h:
        header = h.read()

    label_template = Template(filename = os.path.join(g.lbl_dir, 'label_template_body.svg'), input_encoding = 'utf-8')

    N = len(c4_dct)  # of products in the contract
    page = 1  # nr of page being built
    i = 0  # index of the label to print
    ox = - spacing_w + f64_horizontal_centering_offset(label_view_box_w, spacing_w)
    oy = - spacing_h + g.header_height

    while i < N:  # enumerating over each item in the contract
        # opening a new page
        svg_out = os.path.join(g.lbl_dir, f'page_{page}.svg')
        with open(svg_out, 'w') as f:
            f.write(header)
            f.write("<g transform='translate(20, 20)'>\n")
            if page == 1:
                f.write(
                    "<g>\n<text transform='translate(0, 5)' "
                    f"style='font-family:{family};font-size:{size};font-style:{style}'>1. 外箱的唛头</text>\n</g>\n")
            while oy + label_view_box_h + spacing_h <= g.page_view_box_h and i < N:
                while ox + label_view_box_w + spacing_w <= g.page_view_box_w and i < N:
                    offset_x = ox + spacing_w
                    offset_y = oy + spacing_h
                    f.write(r"<g transform = 'translate(" + f"{offset_x}, {offset_y})'>\n")
                    f51_write_data_in_label_template_item(f, label_template, c4_dct[i])
                    f.write('</g>\n')
                    ox += label_view_box_w + spacing_w
                    i += 1
                ox = - spacing_w + f64_horizontal_centering_offset(label_view_box_w, spacing_w)
                oy += label_view_box_h + spacing_h
            oy = - spacing_h + g.header_height
            f.write('\n</g>\n</svg>\n')
        # subprocess.Popen(['cat', os.path.join(g.lbl_dir, f'page_{page}.svg')])
        # subprocess.Popen([r'/usr/bin/google-chrome', '--disable-gpu', '--disable-software-rasterizer', svg_out])
        # PYCHARM TURN OFF Run / Edit configurations / Emulate terminal in output console
        subprocess.Popen([r'firefox', svg_out])
        page += 1


def main():
    """ Driver """
    j = Json()
    j.create()  # todo: not necessary to print file
    data = j.read()  # todo: a select function, a print function

    # reading from file the strings of info to be looked for
    cators_df_ = Indicators()
    cators_df = cators_df_.read()

    # First scrape all information that could be relevant
    c2_ = AllIndctrs(data, cators_df)
    c2 = c2_.read()

    # build the reference set of product numbers in the contract to identify indicators common to all
    c2b_ = ProdSet(data)
    c2b = c2b_.read()

    # Split between common and specific indicators
    s = Splitter(c2, c2b)
    c3a, c3b = s.read()

    # Select indicators to be used & extract corresponding information for each product
    c = ChooseSpecificIndicators(c3b)
    c.select()
    c.write_to_file()
    c4_df = c.read()
    c4_dct = f40_df_to_dct(c4_df)
    f50_present_one_reference_label_svg(c4_dct)
    label_view_box_w, label_view_box_h, spacing_w, spacing_h = f60_suggest_hor_n_vert_spacings_between_labels()
    f70_assemble_all_labels_into_svg(c4_dct, label_view_box_w, label_view_box_h, spacing_w, spacing_h)
    print()


if __name__ == '__main__':
    main()
