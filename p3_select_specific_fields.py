#!/usr/bin/env python3
import json
import math
import os
import pathlib
import pprint
import re
import shutil
import subprocess
import webbrowser

from mako.template import Template

import m_menus as m
import p1_select_contract as p1
import p2_select_templates as p2

p0_root_abs_dir = os.path.dirname(os.path.abspath(__file__))  # root directory

p3_all_specific_fields_l = []  # list of fields from p1e_specific_fields_d_of_d
p3_body_svg = ''  # contents of label_template_body.svg

# p3_default_fields_l = ['xl_prod_spec', 'u_parc']
p3_d = {}
p3_f = ''
p3_fields_rel_dir = ''  # currently working fields directory
p3_selected_fields_values_by_prod_d = {}  # field values as in .mako_input.json
page_view_box_w = 0
page_view_box_h = 0


def load_p3_all_specific_fields_l():
    global p3_all_specific_fields_l

    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d_n_p3_needed_vars()
    p3_all_specific_fields_l = list(
        next(iter(p1.p1e_specific_fields_d_of_d.values()))
    )


def save_template_info_json():
    global p3_f
    global p3_d

    p3_f = os.path.join(p1.p1_cntrct_abs_dir
                        + '/'
                        + p3_fields_rel_dir, 'template-info.json')
    with open(p3_f, 'w', encoding='utf8') as f:
        json.dump(p3_d, f, ensure_ascii = False)


def extract_svg_for_inserting(inkscape_filename, insert_filename):
    # body_svg = ''
    with open(inkscape_filename, encoding='utf8') as fr, open(insert_filename, 'w', encoding='utf8') as fw:
        write_b = False
        lines = fr.readlines()
        for i in range(len(lines) - 1):
            if r'</metadata>' in lines[i]:
                write_b = True
                continue
            if write_b:
                # body_svg += lines[i]
                fw.write(lines[i])


def create_template_header_n_body_if_not_exist(some_rel_dir):
    """
    copy header, also template if necessary, build body from template.svg copy that is in repository directory
    """
    global p3_body_svg

    from_abs_dir = os.path.join(p0_root_abs_dir + '/common', some_rel_dir)
    to_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, some_rel_dir)

    # copy the label_template if necessary
    template_fr = os.path.join(to_abs_dir, 'label_template.svg')
    if not pathlib.Path(template_fr).exists():
        shutil.copy(
            os.path.join(from_abs_dir, 'label_template.svg'),
            to_abs_dir
        )

    # create label_template_body.svg if necessary
    body_fw = os.path.join(to_abs_dir, '.label_template_body.svg')
    if pathlib.Path(body_fw).exists():
        with open(body_fw, encoding='utf8') as fr:
            p3_body_svg = fr.read()
    else:
        with open(template_fr, encoding='utf8') as fr, open(body_fw, 'w', encoding='utf8') as fw:
            write_b = False
            lines = fr.readlines()
            for i in range(len(lines) - 1):
                if r'</metadata>' in lines[i]:
                    write_b = True
                    continue
                if write_b:
                    p3_body_svg += lines[i]
                    fw.write(lines[i])

    # and copy the label_template_header there
    if not pathlib.Path(os.path.join(to_abs_dir, '.label_template_header.svg')).exists():
        shutil.copy(os.path.join(p0_root_abs_dir + '/common', '.label_template_header.svg'), to_abs_dir)


def load_o_create_p3_fields_info_f():
    global p3_f
    global p3_d
    global p3_fields_rel_dir
    # global p3_default_fields_l
    global page_view_box_w
    global page_view_box_h

    p1.load_o_create_doc_set_up()
    page_view_box_w = 210 - 2 * p1.doc_setup_d['margin_w']  # Assuming A4
    page_view_box_h = 297 - 2 * p1.doc_setup_d['margin_h']  # Assuming A4

    if p3_fields_rel_dir:
        # either read data,
        p3_f = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, 'template-info.json')
        if pathlib.Path(p3_f).exists():  # file exists, check that all default value are present, if not print a msg
            with open(p3_f, encoding='utf8') as f:
                p3_d = json.load(f)  # loads selected_fields, template_header, header_height, barcode_d
        # or populate missing fields with default information relative to the directory
        # other default information is set at variable initialization

        if 'selected_fields' not in p3_d.keys():
            p3_d['selected_fields'] = ['xl_prod_spec', 'u_parc']
        if 'partially_populated_fields' not in p3_d.keys():
            p3_d['partially_populated_fields'] = ['gm_zh']
        if 'header_height' not in p3_d.keys():
            p3_d['header_height'] = 7
        if 'template_header' not in p3_d.keys():
            p3_d['template_header'] = p3_fields_rel_dir[p3_fields_rel_dir.rfind('_') + 1:] + '唛头'
        if 'barcode_d' not in p3_d.keys():
            p3_d['barcode_d'] = {
                "coef": 0.0,
                "x1": 0, "y1": 0,
                "x2": 0, "y2": 0
            }
        if 'mako_pre_proc_d' not in p3_d.keys():
            p3_d['mako_pre_proc_d'] = {
                "empty_new_indic": {
                    "field": "",
                    "regex": "",
                    "default": ""
                }
            }
        if 'pics_d' not in p3_d.keys():
            p3_d['pics_d'] = False
        else:
            if p3_d['pics_d'] is True:
                if not p1.all_products_to_be_processed_set:
                    p1.load_p1_all_products_to_be_processed_set()
                p3_d['pics_d'] = {}
                for prod_nr in list(p1.all_products_to_be_processed_set):
                    p3_d['pics_d'][prod_nr] = {
                        'file': 'pic_0.png',
                        'x': 0,
                        'y': 0,
                        'coef': 0,
                        'width': 0,
                        'height': 0
                    }

        save_template_info_json()
        return True
    else:
        print('|\n| The contract directory does not contain subdirectories: cannot load or create labels\n|')
        return False


def scrap_template_for_fields():
    global p3_fields_rel_dir
    template_fields = fields_from_template()
    for x in ['t', 'i', 'prod_n']:
        if x in template_fields:
            template_fields.remove(x)
    for f in template_fields:
        if f not in p3_d['selected_fields']:
            p3_d['selected_fields'].append(f)
    print(f'Template scrapped, selected_fields: {p3_d["selected_fields"]}')
    save_template_info_json()


def check_if_template_requirements_are_met():
    global p3_fields_rel_dir
    template_fields_set = fields_from_template()
    for x in ['t', 'i', 'prod_n']:
        if x in template_fields_set:
            template_fields_set.remove(x)
    # print(f'Template in {p3_fields_rel_dir} uses {template_fields_set}')
    # print(f'Fields selected to feed data are  {p3_d["selected_fields"]}')
    diff_set = template_fields_set - set(p3_d['selected_fields'])
    if diff_set:
        missing_in_template_l = []
        for f in template_fields_set:
            if f not in p3_d['selected_fields']:
                missing_in_template_l.append(f)
        # print('The template requires the following fields but those\n'
        #       'were not found in the data requisition list: ', missing_in_template_l)
    else:
        pass
        # print('Template fields and requested data match.  The template is operational.')

        # template_f = os.path.join(os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir), 'label_template.svg')
        # subprocess.Popen([
        #     'inkscape',
        #     template_f,
        # ]).wait()


def load_o_create_mako_input_values_json(force_recreate = False):
    """
    Creates a json file with variables and values necessary to mako rendering
    :return:
    """
    global p3_fields_rel_dir
    global p3_selected_fields_values_by_prod_d

    check_if_template_requirements_are_met()
    # make sure global variables are initialized in all situations, outside the loop to do it once only
    mako_input_json_s = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, '.mako_input.json')
    if pathlib.Path(mako_input_json_s).exists() and not force_recreate:
        with open(mako_input_json_s, encoding='utf8') as fr:
            p3_selected_fields_values_by_prod_d = json.load(fr)
    else:
        if not p1.p1b_indics_from_contract_l:
            p1.load_p1b_indics_from_contract_l()
        if not p1.all_products_to_be_processed_set:
            p1.load_p1_all_products_to_be_processed_set()
        # make a skeleton for p3_selected_fields_values_by_prod_d with key = prod
        idx = 0
        temp_d = {}
        for prod in sorted(p1.all_products_to_be_processed_set):
            temp_d[prod] = {'i': str(idx + 1), 'prod_n': prod}
            for field in p3_d['partially_populated_fields']:
                temp_d[prod][field] = ''
                if field[-3:] == '_zh':
                    temp_d[prod][field[:-2] + 'fr'] = ''
            idx += 1

        # prepare to insert translations if needed
        with open(os.path.join(p0_root_abs_dir + '/common', 'zh_fr.json'), encoding='utf8') as f:
            zh_fr_d = json.load(f)

        # populate the skeleton
        for indc_d in p1.p1b_indics_from_contract_l:  # loop over the big one once
            if indc_d['prod_nr'] in p1.all_products_to_be_processed_set:
                if indc_d['what'] in p3_d['selected_fields']:  # loop over the smaller more
                    temp_d[indc_d['prod_nr']][indc_d['what']] = indc_d['info']
                    what_zh = indc_d['what']
                    # internal convention: all indics with name finishing with _zh will be translated into French
                    # with ./common/zh_fr.json
                    if what_zh[-3:] == '_zh':
                        what_fr = what_zh[:-2] + 'fr'
                        temp_d[indc_d['prod_nr']][what_fr] = zh_fr_d[indc_d['info']]

        # build the dictionary p3_selected_fields_values_by_prod_d with key = i - 1
        for v in temp_d.values():
            p3_selected_fields_values_by_prod_d[str(int(v['i']) - 1)] = v

        # save results before adding new fields being derived from existing ones
        # mako_pre_proc_json_s = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, '.mako_preproc.json')
        # with open(mako_pre_proc_json_s, 'w', encoding='utf8') as f:
        #     json.dump(p3_selected_fields_values_by_prod_d, f, ensure_ascii = False)

        # adding new fields being derived from existing ones, as defined in template-info.json
        if 'empty_new_indic' not in p3_d['mako_pre_proc_d'].keys():
            for new_field in p3_d['mako_pre_proc_d'].keys():
                for k in p3_selected_fields_values_by_prod_d.keys():
                    regex = p3_d['mako_pre_proc_d'][new_field]['regex']
                    string = p3_selected_fields_values_by_prod_d[k][p3_d['mako_pre_proc_d'][new_field]['field']]
                    out_field = re.search(regex, string)
                    default = p3_d['mako_pre_proc_d'][new_field]['default']
                    p3_selected_fields_values_by_prod_d[k][new_field] = out_field.group() if out_field else default

        with open(mako_input_json_s, 'w', encoding='utf8') as f:
            json.dump(p3_selected_fields_values_by_prod_d, f, ensure_ascii = False)


def suggest_spacing_calc(lgth, template_view_box):
    n_of_templates_per_dim = int(lgth // template_view_box)
    return min(20, int((lgth - n_of_templates_per_dim * template_view_box) / max(1, (n_of_templates_per_dim - 1))))


def display_or_load_output_overview():
    global p3_fields_rel_dir
    global p3_d

    print('~~~ Overview')
    _, drs, _ = next(os.walk(p1.p1_cntrct_abs_dir))
    for dr in drs:
        print(dr)
        p3_fields_rel_dir = dr
        if load_o_create_p3_fields_info_f():
            print('\t', p3_d['selected_fields'])
    print('~~~')


def fields_from_template():
    global p3_fields_rel_dir
    template_s = os.path.join(os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir), 'label_template.svg')
    if not pathlib.Path(template_s).exists():
        print(f"|\n| Cannot access '{os.path.join(p3_fields_rel_dir, 'label_template.svg')}': no such file\n|")
    with open(template_s, encoding='utf8') as fr:
        lines = fr.readlines()
    template_fields_set = set()
    for line in lines:
        finds = re.findall(r'(\${)(.+?)(})', line)
        for find in finds:
            template_fields_set.add(find[1])
    return template_fields_set


def check_all_templates_have_correct_fields():
    global p3_fields_rel_dir
    _, drs, _ = next(os.walk(p1.p1_cntrct_abs_dir))
    for p3_fields_rel_dir in drs:
        load_o_create_p3_fields_info_f()
        check_if_template_requirements_are_met()


def add_fields():
    global p3_f
    global p3_fields_rel_dir
    global p3_all_specific_fields_l

    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d_n_p3_needed_vars()
    p3_all_specific_fields_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))
    # select from p3_all_specific_fields_l and put in p3_d['selected_fields']
    while True:
        print(f'~~~ Already selected:\n{p3_d["selected_fields"]}\n~~~ Can be added:')
        not_yet_l = []
        for o in p3_all_specific_fields_l:
            if o not in p3_d['selected_fields']:
                not_yet_l.append(o)
        for i in range(len(not_yet_l)):
            print(str(i) + ' ' + not_yet_l[i])
        print('~~~')
        s = input('Enter nr of indicator to add, \'b\' to return : ')
        if s == 'b':
            os.system('clear' if os.name == 'posix' else 'cls')
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(not_yet_l)):
                    p3_d['selected_fields'].append(not_yet_l[s_i])
                    # break
                else:
                    print('|\n| Integer, but not an option, try again\n|')
            except ValueError:
                print('|\n| That\'s not an integer, try again\n|')
    save_template_info_json()


def del_fields():
    global p3_f

    while True:
        print(f'~~~ Already selected:')
        for i in range(len(p3_d['selected_fields'])):
            print(f'{i}. {p3_d["selected_fields"][i]}')
        print(f'~~~')
        s = input('Enter nr of indicator to delete, \'b\' to return : ')
        if s == 'b':
            os.system('clear' if os.name == 'posix' else 'cls')
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(p3_d['selected_fields'])):
                    del p3_d['selected_fields'][s_i]
                    # break
                else:
                    print('|\n| Integer, but not an option, try again\n|')
            except ValueError:
                print('|\n| That\'s not an integer, try again\n|')

    save_template_info_json()


def display_specific_fields_for_all_products():
    # make sure global variables are set in all situations, outside the loop to do it once only
    if not p1.all_products_to_be_processed_set:
        p1.load_p1_all_products_to_be_processed_set()
    if not p1.p1b_indics_from_contract_l:
        p1.load_p1b_indics_from_contract_l()

    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d_n_p3_needed_vars()
    p1e_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))

    # building the header
    tmp_l = [8 * ' ']
    for f in p1e_l:
        tmp_l.append(f)
    dsp_l = [tmp_l]

    spec_by_prod = p1.p1e_specific_fields_d_of_d

    # filling missing information with ***
    # adding 'prod_nr' to the list and sorting
    for prod in spec_by_prod.keys():
        tmp_l = [prod]
        for value in p1e_l:
            if value not in spec_by_prod[prod].keys():
                spec_by_prod[prod][value] = '***'
            tmp_l.append(spec_by_prod[prod][value])
        dsp_l.append(tmp_l)

    length = 0
    for l_l in dsp_l:
        for ls in l_l:
            length = max(length, len(str(ls)))
    s = ''
    for l_l in dsp_l:
        for ls in l_l:
            s += (length - len(str(ls))) * ' ' + str(ls)
        s += '\n'
    print(s)


def display_p3_fields_info_d():
    global p3_d
    print('~~~ Reading template-info global value ~~~')
    pprint.pprint(p3_d)
    print(p3_d)
    print('~~~ Finished reading template-info global value ~~~')


def display_p3_fields_info_f():
    global p3_f
    global p3_d

    if p3_d:
        if pathlib.Path(p3_f).exists():
            print('~~~ Reading template-info.json file contents ~~~')
            with open(p3_f, encoding='utf8') as f:
                pprint.pprint(f.read())
            print('~~~ File template-info.json closed ~~~')
    else:
        print(f'\nFile {p3_f} not built yet\n')


def display_pdf():
    # os.chdir(p1.p1_cntrct_abs_dir)
    # output_s = p1.p1_d["cntrct_nr"] + '.pdf'
    output_s = os.path.join(p1.p1_cntrct_abs_dir, p1.p1_d["cntrct_nr"] + '.pdf')
    subprocess.Popen(['xreader', output_s, ], encoding='utf8')
    # os.chdir(p0_root_abs_dir)


def svg_s_to_pdf_deliverable():
    os.chdir(p1.p1_cntrct_abs_dir)
    print_svg_l = [f for f in os.listdir(p1.p1_cntrct_abs_dir) if os.path.isfile(f)
                   and f.endswith('.svg')
                   and f[0] != '.']

    for file in print_svg_l:
        with open(file, encoding='utf8') as fr, open('.' + file, 'w', encoding='utf8') as fw:
            for line in fr:
                fw.write(line.replace('fuchsia', 'none').replace('#ff00ff', 'none'))

    print_clean_svg_l = [f for f in os.listdir(p1.p1_cntrct_abs_dir) if os.path.isfile(f)
                         and f.endswith('.svg')
                         and f[0] == '.']

    for file in print_clean_svg_l:
        filename, _ = os.path.splitext(file)
        subprocess.Popen([
            'inkscape',
            f'--export-filename={filename}.pdf',  # f'--export-file={filename}.pdf',
            file,
        ]).wait()

    output_s = p1.p1_d["cntrct_nr"] + '.pdf'

    # not workable solution: erase but doesn't create, create but doesn't erase
    # print_pdf_l = [f for f in os.listdir(p1.p1_cntrct_abs_dir) if os.path.isfile(f) and f.endswith('.pdf')]
    # if os.path.exists(output_s):
    #     subprocess.Popen(['rm', output_s, ]).wait()
    # subprocess.Popen(['pdfunite', *print_pdf_l, output_s, ]).wait()

    os.system('pdfunite .page_?.pdf ' + output_s)
    subprocess.Popen(['xreader', output_s, ])
    os.chdir(p0_root_abs_dir)


def horizontal_centering_offset(template_view_box_w, spacing_w):
    global page_view_box_w

    n_of_templates_per_row = int(page_view_box_w // template_view_box_w)
    result = (page_view_box_w - n_of_templates_per_row * template_view_box_w - (
        n_of_templates_per_row - 1) * spacing_w) / 2
    return result


def prod_n_to_barcode(prod_nr):
    temp_s = ''
    for char in prod_nr:
        if char.isnumeric():
            temp_s += char
    while len(temp_s) < 12:
        if (12 - len(temp_s)) % 2 == 1:
            temp_s = '3' + temp_s
        else:
            temp_s = '0' + temp_s
    return temp_s


def create_barcode_file(prod_n):
    global p3_fields_rel_dir

    brcd_tmplt = os.path.join(p0_root_abs_dir + '/common', 'barcode_template.svg')

    brcd_f = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, prod_n + '.svg')
    command = f"./render_barcode.py " + \
              f"-t='Ean13' " + \
              f"-d='{prod_n_to_barcode(prod_n)}' " + \
              f"-l='20' " + \
              f"--output='{brcd_f}' " + \
              f"'{brcd_tmplt}' "
    os.system(command)
    return brcd_f


def open_svg_for_output(header, page, only_1_temp, only_1_prod, family, size, style):
    global p3_d
    global page_view_box_h
    # assert fw == fw
    # assert svg_out == svg_out

    p3_fields_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir)
    if only_1_temp:
        if only_1_prod:
            svg_out = os.path.join(p3_fields_abs_dir, '.1_product.svg')
        else:
            svg_out = os.path.join(p3_fields_abs_dir, f'.1_template_{page}.svg')
    else:
        svg_out = os.path.join(p1.p1_cntrct_abs_dir, f'page_{page}.svg')
    fw = open(svg_out, 'w', encoding='utf8')
    fw.write(header)
    fw.write(f'<rect x="0" y="0"\n'
             f'width="210" height="297"\n'
             f'style="fill:none;stroke-width:0.5;stroke-opacity:1;stroke:#ff00ff" />\n')
    fw.write(f'<rect x="{p1.doc_setup_d["margin_w"]}" y="{p1.doc_setup_d["margin_h"]}"\n'
             f'width="{210 - 2 * p1.doc_setup_d["margin_w"]}" height="{297 - 2 * p1.doc_setup_d["margin_h"]}"\n'
             f'style="fill:none;stroke-width:0.5;stroke-opacity:1;stroke:#ff00ff" />\n')
    page_x = 100  # page middle - 5mm to center text, assuming A4
    page_y = int(page_view_box_h + 3 * (297 - page_view_box_h) / 4)
    fw.write(
        f"<g>\n<text transform='translate({page_x}, {page_y})' "
        f"style='font-family:{family};font-size:{size};font-style:{style}'>-- {page} --</text>\n</g>\n"
    )
    # assuming A4
    fw.write(f"<g transform='translate({p1.doc_setup_d['margin_w']}, {p1.doc_setup_d['margin_h']} )'>\n")
    return fw, svg_out


def close_svg_for_output(fw, svg_out):
    fw.write('\n</g>\n</svg>\n')
    fw.close()
    browser = 'firefox' if os.name == 'posix' else "C:\Program Files (x86)\Mozilla Firefox\firefox.exe %s"
    webbrowser.get(browser).open_new_tab(svg_out)
    # subprocess.Popen(['inkscape', svg_out])


def render_svg_all_templates_all_products(only_1_temp = False, only_1_prod = False):
    """

    """
    global p3_fields_rel_dir
    global p3_d
    global p3_all_specific_fields_l
    global p3_selected_fields_values_by_prod_d
    global p3_body_svg
    global page_view_box_h
    global page_view_box_w

    # load p1.p1e_specific_fields_d_of_d, put in a list of dicts
    load_p3_all_specific_fields_l()

    # read existing templates
    drs = [p3_fields_rel_dir] if only_1_temp else p2.p2_load_templates_info_l()
    oy = 0
    if drs:
        svg_out = ''  # svg output filename
        fw = None  # and its file handler
        template_nr = 0  # number templates so as to make headers
        page = 1  # nr of page being built
        for p3_fields_rel_dir in drs:  # looping on templates

            # check that, if pictures need to be inserted, a directory for picture files does exist
            load_o_create_p3_fields_info_f()
            p3_fields_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir)  # dir for header & body
            # if type(p3_d['pics_d']) != 'bool' and p3_d['pics_d']:
            #     dir_s = os.path.join(p3_fields_abs_dir, 'pics')
            #     if not pathlib.Path(dir_s).exists():
            #         print(
            #             f'|\n| Cannot access {dir_s} : No such directory\n| '
            #             'Create one manually and put picture files as indicated by template-info.json\n| '
            #             'Exiting program ...\n|'
            #         )
            #         exit()

            create_template_header_n_body_if_not_exist(p3_fields_rel_dir)
            with open(os.path.join(p3_fields_abs_dir, '.label_template_header.svg'), encoding='utf8') as h:
                header = h.read()
            template_nr += 1
            # loading data previously used with this template
            load_o_create_p3_fields_info_f()

            # opening a new page, printing header template in 'page_#.svg'
            # printing body template in page_# svg
            # family = re.search(r'(?<=font-family:)([\w-]+)', p3_body_svg).groups()[0]
            # size = re.search(r'(?<=font-size:)(\d+\.*\d*\w*)', p3_body_svg).groups()[0]
            # style = re.search(r'(?<=font-style:)([\w-]+)', p3_body_svg).groups()[0]
            family = 'sans-serif'
            size = '3.6px'
            style = 'normal'
            if page == 1:
                # open the first web page, it will be closed when there is no space left, then a new one will be opened
                fw, svg_out = open_svg_for_output(
                    header, page, only_1_temp, only_1_prod,
                    family, size, style
                )
            # from the editable template, build the 'label_template.svg' that will be used to multiply templates
            load_o_create_mako_input_values_json(force_recreate = True)
            # read view box values from template_body so as to compute spacings
            to_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir)
            with open(os.path.join(to_abs_dir, 'label_template.svg'), encoding='utf8') as f:
                mako_template = Template(
                    filename = os.path.join(p3_fields_abs_dir, '.label_template_body.svg'),
                    input_encoding = 'utf-8'
                )
                contents = f.read()
                measures = re.search(r'(?<=viewBox=")(\d) (\d) (\d+.*\d*) (\d+\.*\d*)', contents)
                if measures.groups()[0] != '0' or measures.groups()[1] != '0':
                    print("Error in building 'label_template.svg': origin is not (0, 0), exiting program ...")
                    exit()
                template_view_box_w = float(measures.groups()[2])
                template_view_box_h = float(measures.groups()[3])
            spacing_w = suggest_spacing_calc(page_view_box_w, template_view_box_w)
            spacing_h = suggest_spacing_calc(page_view_box_h - p3_d['header_height'], template_view_box_h)
            assert template_view_box_w + spacing_w <= page_view_box_w, \
                "write_templates: ! template width + spacing width don't fit in the page"
            assert template_view_box_h + spacing_h <= page_view_box_h, \
                'write_templates: ! template height + spacing height don\'t fit in the page'

            # write the header for this template
            if page == 1:
                oy = p1.doc_setup_d['page_1_vert_offset'] - spacing_h

            fw.write(
                f'<svg width="{page_view_box_w}" height="{p3_d["header_height"]}" '
                f'x="0" y="{oy + spacing_h}">\n'
                f'<rect x="0" y="0"\n'
                f'width="100%" height="100%"\n'
                f'style="fill:none;stroke-width:0.5;stroke-opacity:1;stroke:#ff00ff" />\n'
                f'<text x="0%" y="100%" dominant-baseline="text-after-edge" '
                f'style="font-family:{family};font-size:{size};font-style:{style}">'
                f'{template_nr}. {p3_d["template_header"]}</text>\n</svg>\n'
            )
            # run mako.template.Template
            ox = - spacing_w + horizontal_centering_offset(template_view_box_w, spacing_w)
            oy += p3_d['header_height']
            lngth = len(p3_selected_fields_values_by_prod_d)  # nr of products in the contract
            i = 0  # index of the template to print

            while i < (1 if only_1_prod else lngth):
                # writing horizontally while there templates to print
                while ox + template_view_box_w <= page_view_box_w and i < (1 if only_1_prod else lngth):
                    fw.write(r"<g transform = 'translate(" + f"{ox + spacing_w}, {oy + spacing_h})'>\n")

                    # link a picture file if there is one to link
                    if type(p3_d['pics_d']) != 'bool' and p3_d['pics_d']:
                        prod_nr = p3_selected_fields_values_by_prod_d[str(i)]['prod_n']
                        if prod_nr in p3_d['pics_d'].keys():
                            filename = os.path.join(p3_fields_abs_dir + '/pics', p3_d['pics_d'][prod_nr]['file'])
                            # filename = os.path.join(p3_fields_abs_dir, p3_d['pics_d'][prod_nr]['file'])
                            if pathlib.Path(filename).exists():
                                _, ext = os.path.splitext(filename)
                                if ext == '.svg':
                                    i_filename = os.path.join(p3_fields_abs_dir, '.' + p3_d['pics_d'][prod_nr]['file'])
                                    if not pathlib.Path(i_filename).exists():
                                        extract_svg_for_inserting(filename, i_filename)
                                    with open(i_filename, encoding='utf8') as f:
                                        fw.write(  # todo: change into a list
                                            f"<g transform = 'matrix("
                                            f"{p3_d['pics_d'][prod_nr]['coef']},0,0,{p3_d['pics_d'][prod_nr]['coef']},"
                                            f"{p3_d['pics_d'][prod_nr]['x']},{p3_d['pics_d'][prod_nr]['y']}"
                                            ")'>\n")
                                        fw.write(f.read())
                                        fw.write(
                                            f"</g>\n"
                                        )
                                        os.remove(i_filename)
                                else:
                                    fw.write(
                                        f"<svg x='{p3_d['pics_d'][prod_nr]['x']}' "
                                        f"y='{p3_d['pics_d'][prod_nr]['y']}' "
                                        f"width='{p3_d['pics_d'][prod_nr]['width']}' "
                                        f"height='{p3_d['pics_d'][prod_nr]['height']}' >\n"
                                        f"<image xlink:href='{f'{p3_fields_abs_dir}/'}"
                                        f"{p3_d['pics_d'][prod_nr]['file']}' "
                                        "x='0' y='0' width='100%' height='100%' />\n"
                                        f"</svg>\n"
                                    )
                            else:
                                print(
                                    f'|\n| Cannot access {filename}: No such file \n'
                                    '| Make sure it exists as indicated by template-info.json'
                                )
                                exit()

                    # create the path to a potential barcode file
                    barcode_f = os.path.join(
                        os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir),
                        p3_selected_fields_values_by_prod_d[str(i)]['prod_n'] + '.svg'
                    )

                    # a blank template to write barcodes is systematically in template-info.json
                    # so check if blank fields have been populated.
                    brcd_d = dict(p3_d['barcode_d']) if not math.isclose(
                        p3_d['barcode_d']['coef'], 0.0, abs_tol = 0.001
                    ) else {}

                    if brcd_d:
                        if pathlib.Path(create_barcode_file(
                            p3_selected_fields_values_by_prod_d[str(i)]['prod_n']
                        )).exists():
                            with open(barcode_f, encoding='utf8') as f:
                                fw.write(  # todo: change into a list
                                    f"<g transform = 'matrix("
                                    f"{brcd_d['coef']},0,0,{brcd_d['coef']},"
                                    f"{brcd_d['x1']},{brcd_d['y1']}"
                                    ")'>\n")
                                fw.write(f.read())
                                fw.write(
                                    "</g>\n"
                                    f"<g transform = 'matrix("
                                    f"{brcd_d['coef']},0,0,{brcd_d['coef']},"
                                    f"{brcd_d['x2']},{brcd_d['y2']}"
                                    f")'>\n"
                                )
                                fw.write(f.read())
                                fw.write("</g>\n")

                    # print(  # for debug purposes
                    #     f'{p3_fields_rel_dir} page: {page} ',
                    #     f'ox: {ox:3.1f}, oy: {oy:3.1f}',
                    #     f"idx: {p3_selected_fields_values_by_prod_d[str(i)]['i']}",
                    #     f"prod_nr: {p3_selected_fields_values_by_prod_d[str(i)]['prod_n']}"
                    # )
                    print(  # for debug purposes
                        p1.p1_d['cntrct_nr'], template_nr, i, end = ', '
                    )
                    tmp_l = [k for k in list(p3_selected_fields_values_by_prod_d[str(i)].keys())[:8]]
                    for k in tmp_l:
                        print(  # for debug purposes
                            ', ', k, p3_selected_fields_values_by_prod_d[str(i)][k], end = ''
                        )
                    print()

                    fw.write(mako_template.render(
                        contract_n = p1.p1_d["cntrct_nr"],
                        t = template_nr,
                        **p3_selected_fields_values_by_prod_d[str(i)])
                    )
                    fw.write('</g>\n')
                    ox += template_view_box_w + spacing_w
                    i += 1
                ox = - spacing_w + horizontal_centering_offset(template_view_box_w, spacing_w)
                oy += template_view_box_h + spacing_h
                # print(  # for debug purposes
                #     f'ox: {ox:3.1f} ox: {oy:3.1f}  test: {oy + template_view_box_h + spacing_h} > {page_view_box_h}'
                # )
                # check if there is still space to write the next one, if not open a new page
                if oy + template_view_box_h + spacing_h > page_view_box_h:
                    # to avoid printing a blank page when no data left
                    if i < (1 if only_1_prod else lngth) or template_nr != len(drs):
                        close_svg_for_output(fw, svg_out)
                        page += 1
                        fw, svg_out = open_svg_for_output(
                            header, page, only_1_temp, only_1_prod,
                            family, size, style
                        )
                        if i == lngth:  # if at end of a list, then oy = 0
                            oy = 0
                        else:
                            oy = - spacing_h
            # after last item is written, write the next header if needed
        close_svg_for_output(fw, svg_out)  # close the last file without opening a new one
    else:
        print('No template directory found, go back to general menu and create one or more templates')


def render_svg_1_template_1_product():
    global p3_fields_rel_dir

    if not p3_fields_rel_dir:
        drs = p1.read_dirs(p1.p1_cntrct_abs_dir)
        p3_fields_rel_dir = drs[0]
    render_svg_all_templates_all_products(only_1_temp = True, only_1_prod = True)


def render_svg_1_template_all_products():
    global p3_fields_rel_dir

    if not p3_fields_rel_dir:
        drs = p1.read_dirs(p1.p1_cntrct_abs_dir)
        p3_fields_rel_dir = drs[0]
    render_svg_all_templates_all_products(only_1_temp = True)


def render_svg_all_n_print():
    render_svg_all_templates_all_products()
    svg_s_to_pdf_deliverable()


def render_cover_page():
    global p3_fields_rel_dir
    global p3_d
    global p3_selected_fields_values_by_prod_d

    # load data from p1.p1e_specific_fields_d_of_d, put in a list of dicts
    p3_fields_rel_dir = p2.p2_load_templates_info_l()[0]
    load_o_create_p3_fields_info_f()
    load_p3_all_specific_fields_l()

    # print(  # for debug purposes
    #     f"From '..._doc_setup.json': cover_page = {p1.doc_setup_d['cover_page']}"
    # )
    # if p1.doc_setup_d['cover_page']:
    #     print("The label used for the cover page is from the layer 'label' in label_template.svg")

    # copy first label on cover page template
    p3_fields_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir)
    svg_in = os.path.join(p3_fields_abs_dir, '.1_product.svg')
    if svg_in:
        with open(svg_in, encoding='utf8') as fr:
            lines = fr.readlines()
        balance = 0
        keep_l = []
        tmp_l = []
        i = 0
        good_n = 0
        for line in lines:
            res1 = re.match(r'\s*<g', line)
            if res1:
                balance += 1
            res2 = re.match(r'\s*</g>', line)
            if balance >= 3:
                tmp_l.append(line)
            if res2:
                if balance == 3:
                    keep_l.append(tmp_l)
                    i += 1
                    tmp_l = []
                balance -= 1
            if 'label="label"' in line:
                good_n = i
        with open(os.path.join(p0_root_abs_dir + '/common/.cover_page_template.svg'), encoding='utf8') as fr:
            lines = fr.readlines()
        svg_out = os.path.join(p1.p1_cntrct_abs_dir, '.cover_page_template.svg')
        with open(svg_out, 'w', encoding='utf8') as fw:
            for i in range(len(lines) - 1):
                fw.writelines(lines[i])
            fw.write('<g transform="matrix(1,0,0,1,15,45)">\n')
            for good in keep_l[good_n]:
                fw.write(good)
            # fw.writelines(keep_l[good_n])
            fw.write('</g>\n')
            fw.write('<g transform="matrix(.25,0,0,.25,22,167)">\n')
            for good in keep_l[good_n]:
                fw.write(good)
            # fw.writelines(keep_l[good_n])
            fw.write('</g>\n')
            fw.writelines(lines[len(lines) - 1])

        # run mako.template.Template
        mako_template = Template(
            filename = svg_out,
            input_encoding = 'utf-8'
        )

        if not p3_selected_fields_values_by_prod_d:
            load_o_create_mako_input_values_json()
        cover_s = os.path.join(p1.p1_cntrct_abs_dir, 'page_0.svg')
        with open(cover_s, 'w', encoding='utf8') as fw:
            fw.write(mako_template.render(
                contract_n = p1.p1_d["cntrct_nr"],
                **p3_selected_fields_values_by_prod_d['0']
            ))
        browser = 'firefox' if os.name == 'posix' else "C:\Program Files (x86)\Mozilla Firefox\firefox.exe %s"
        webbrowser.get(browser).open_new_tab(cover_s)
    else:
        print(f'{svg_in}: no such file, should be build before cover page')


def display_all():
    global p3_fields_rel_dir
    # read existing templates
    drs_l = p2.p2_load_templates_info_l()
    if drs_l:
        # for each template that has been created as a subdir to p1.p1_cntrct_abs_dir
        for p3_fields_rel_dir in drs_l:
            # use data on disk, if not on disk create with default values
            if load_o_create_p3_fields_info_f():
                print('Rendering 1 template, 1 product')
                render_svg_1_template_1_product()
                if p1.doc_setup_d['cover_page'] and p3_fields_rel_dir == drs_l[0]:
                    print('Rendering cover page')
                    render_cover_page()
                print('Rendering 1 template, all products')
                render_svg_1_template_all_products()
    print('Rendering all templates, all products, and print')
    render_svg_all_n_print()


def edit_fields():
    global p3_fields_rel_dir

    # select_specific_fields_context_func(prompt = False)
    # print('\n>>> Select template to edit: ')

    while True:
        # select_specific_fields_context_func(prompt = False)
        # print('\n>>> Select template to edit: ')
        print('~~~ Now working on template: ', p3_fields_rel_dir if p3_fields_rel_dir else 'None selected')
        s = input('\'a\' to add a field\n'
                  '\'d\' to delete a field\n'
                  '\'b\' to go back_后退\n'
                  '~~~\n')
        if s == 'b':
            os.system('clear' if os.name == 'posix' else 'cls')
            break
        elif s == 'a':
            add_fields()
        elif s == 'd':
            del_fields()
        else:
            print(f'{s} is not an option, try again')

    save_template_info_json()
    # create_template_header_n_body_if_not_exist(p3_fields_rel_dir)
    load_o_create_mako_input_values_json(force_recreate = True)
    # render_svg_1_template_1_product()


def select_a_template_for_editing():
    global p3_fields_rel_dir

    print('~~~ select a template to edit ~~~')
    m.mod_lev_1_menu = m.menu
    m.menu = 'select_a_template_for_editing'
    # select_specific_fields_context_func()
    drs = p1.read_dirs(p1.p1_cntrct_abs_dir)
    if drs:
        for i in range(len(drs)):
            print(str(i) + '. ' + drs[i][2:])
        while True:
            s = input('\nEnter nr of template to be edited, \'b\' to return : ')
            if s == 'b':
                os.system('clear' if os.name == 'posix' else 'cls')
                m.menu = m.mod_lev_1_menu
                break
            else:
                try:
                    s_i = int(s)
                    if s_i in range(len(drs)):
                        os.system('clear' if os.name == 'posix' else 'cls')
                        p3_fields_rel_dir = drs[s_i]
                        # load fields already selected for template as they are on file
                        load_o_create_p3_fields_info_f()
                        break
                    else:
                        print('|\n| Integer, but not an option, try again\n|')
                except ValueError:
                    print('|\n| That\'s not an integer, try again\n|')


def edit_label_template_svg():
    global p3_fields_rel_dir

    body_file = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, '.label_template_body.svg')
    if pathlib.Path(body_file).exists():
        os.remove(os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, '.label_template_body.svg'))
    label_template_file = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, 'label_template.svg')
    if pathlib.Path(label_template_file).exists():
        subprocess.Popen(['inkscape', label_template_file]).wait()


def select_specific_fields_context_func(prompt = True):
    print('~~~ Step 3: Selecting fields to print for each template ~~~\n')
    display_specific_fields_for_all_products()
    print('~~~ Now processing contract #: ', p1.p1_d["cntrct_nr"] if p1.p1_d["cntrct_nr"] else None)
    print('~~~ Now working on template: ', p3_fields_rel_dir if p3_fields_rel_dir else 'None selected')
    print('~~~ Specific fields selected so far:', p3_d['selected_fields'])
    print(60 * '-', '\n\n')
    if prompt:
        print('\n>>> Select an action: ')


def edit_paragraph_headers():
    global p3_fields_rel_dir

    # list existing directories, each containing a template
    drs = p1.read_dirs(p1.p1_cntrct_abs_dir)
    if drs:
        # giving a default directory if none has been set before
        if not p3_fields_rel_dir:
            p3_fields_rel_dir = drs[0]
        print(f'~~~ Now processing contract #: {p1.p1_d["cntrct_nr"]}')
        print('>>> Select template to edit:\n')
        for i in range(len(drs)):
            print(str(i) + '. ' + drs[i][2:])
        while True:
            s = input('\nEnter nr of template to be edited, \'b\' to return : ')
            if s == 'b':
                os.system('clear' if os.name == 'posix' else 'cls')
                break
            else:
                try:
                    s_i = int(s)
                    if s_i in range(len(drs)):
                        os.system('clear' if os.name == 'posix' else 'cls')
                        p3_fields_rel_dir = drs[s_i]
                        # load fields already selected for template as they are on file
                        if load_o_create_p3_fields_info_f():
                            print(f'now ready to work on {p3_fields_rel_dir}')
                        while True:
                            select_specific_fields_context_func()
                            s = input('\'m\' to use a multi-lines header\n'
                                      '\'d\' to use a single line default header\n'
                                      '\'b\' to go back_后退\n'
                                      '~~~\n')
                            if s == 'b':
                                os.system('clear' if os.name == 'posix' else 'cls')
                                break
                            elif s == 'm':
                                # multi-lines header
                                p3_d['template_header'] = "<tspan x='5' y='10'>Lorem ipsum dolor sit amet, " \
                                                          "consectetur adipiscing elit, sed do eiusmod " \
                                                          "tempor</tspan><tspan x='5' y='15'>incididunt ut labore et " \
                                                          "dolore magna aliqua. Ut enim minim veniam, quis nostrud " \
                                                          "exercitation ullamco laboris nisi</tspan> <tspan x='5' " \
                                                          "y='20'>ut aliquip ex commodo consequat. Duis aute irure " \
                                                          "dolor in reprehenderit in voluptate velit esse cillum " \
                                                          "dolore eu</tspan> "
                                p3_d['header_height'] = 20
                            elif s == 'd':
                                # single line header
                                p3_d['template_header'] = p3_fields_rel_dir[p3_fields_rel_dir.rfind('_') + 1:] + '唛头'
                                p3_d['header_height'] = 7
                            else:
                                print(f'{s} is not an option, try again')
                        break
                    else:
                        print('|\n| Integer, but not an option, try again\n|')
                except ValueError:
                    print('|\n| That\'s not an integer, try again\n|')

        save_template_info_json()
        create_template_header_n_body_if_not_exist(p3_fields_rel_dir)
        load_o_create_mako_input_values_json()
        render_svg_1_template_1_product()
    else:
        return


def test_mako():
    load_o_create_mako_input_values_json(force_recreate = True)
    filename = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, '.mako_input.json')
    subprocess.call(['jq', '.', filename])
    # subprocess.call(['/usr/bin/xed', filename])
    # with open(filename, encoding='utf8') as f:
    #     pprint.pprint(f.read())


context_func_d = {
    'select_specific_fields': select_specific_fields_context_func,
    'select_a_template_for_editing': select_specific_fields_context_func,
    'debug': select_specific_fields_context_func,
}


def reset_globals():
    global p3_all_specific_fields_l
    global p3_body_svg
    global p3_d
    # global p3_default_fields_l
    global p3_f
    global p3_fields_rel_dir
    global p3_selected_fields_values_by_prod_d
    global page_view_box_h
    global page_view_box_w

    p3_all_specific_fields_l = []
    p3_body_svg = ''
    # p3_default_fields_l = ['xl_prod_spec', 'u_parc']
    # p3_d = {
    #     "selected_fields": list(p3_default_fields_l),
    #     "template_header": '',
    #     "header_height": 7,
    # }
    p3_d = {}
    p3_f = ''
    p3_fields_rel_dir = ''
    p3_selected_fields_values_by_prod_d = {}
    page_view_box_h = 0
    page_view_box_w = 0


def step_3__select_fields_to_print_for_each_template_选择每种标签类型的资料():
    global p3_fields_rel_dir
    # make sure p1 infrastructure is in place
    if not p1.load_contract_info_d():
        print('p1 has not run successfully')
    if not p1.read_dirs(p1.p1_cntrct_abs_dir):
        p2.create_default_templates()
    # read existing p3 infrastructure
    if not p3_fields_rel_dir:
        drs = p1.read_dirs(p1.p1_cntrct_abs_dir)
        p3_fields_rel_dir = drs[0]
    if not p3_d:
        load_o_create_p3_fields_info_f()

    # initializing menus last, so that context functions display most recent information
    m.menu = 'select_specific_fields'
    if not m.main_menu:
        m.main_menu = m.menu
    m.menus = {
        m.menu: {
            '1': render_svg_1_template_1_product,
            '2': render_svg_1_template_all_products,
            '3': render_svg_all_n_print,
            '4': display_all,
            '5': render_cover_page,
            '11': select_a_template_for_editing,
            '22': test_mako,
            '33': check_all_templates_have_correct_fields,
            'b': m.back_to_main_退到主程序,
            'q': m.normal_exit_正常出口,
            'd': m.debug,
        },
        'select_a_template_for_editing': {
            '44': edit_label_template_svg,
            '0': scrap_template_for_fields,
            '1': check_if_template_requirements_are_met,
            '2': edit_fields,
            '3': p1.process_selected_contract,
            '4': edit_paragraph_headers,
            'b': m.back_后退,
            'q': m.normal_exit_正常出口,
        },
        'debug': {
            '55': render_cover_page,
            '66': svg_s_to_pdf_deliverable,
            '2': display_or_load_output_overview,
            '6': p1.display_p1_cntrct_info_d,
            '7': p1.display_p1_cntrct_info_f,
            '8': display_p3_fields_info_d,
            '9': display_p3_fields_info_f,
            'b': m.back_后退,
            'q': m.normal_exit_正常出口,
        }
    }
    if not m.main_menus:
        m.main_menus = m.menus
    if __name__ == '__main__':
        m.mod_lev_1_menu = m.menu
        m.mod_lev_1_menus = m.menus
    m.context_func_d = {**m.context_func_d, **context_func_d}


def main():
    """ Driver """
    step_3__select_fields_to_print_for_each_template_选择每种标签类型的资料()
    m.run()


if __name__ == '__main__':
    main()
