#!/usr/bin/env python3
import json
import os
import pathlib
import pprint
import re
import shutil
import subprocess
import webbrowser

from mako.template import Template

import p0_menus as p
import p1_select_contract as p1
import p2_select_templates as p2

p0_root_abs_dir = os.path.dirname(os.path.abspath(__file__))  # root directory
p3_fields_rel_dir = ''  # currently working fields directory
p3_all_specific_fields_l = []  # list of fields from p1e_specific_fields_d_of_d
p3_selected_fields_values_by_prod_d = {}  # field values as in .mako_input.json
p3_body_svg = ''  # content of label_template_body.svg

p3_default_fields_l = ['xl_prod_spec', 'u_parc', 'plstc_bg']
p3_f = ''  # None  # info on fields directory currently being edited
p3_d = {
    "selected_fields": list(p3_default_fields_l),
    "template_header": '',
    "header_height": 7,
}
page_view_box_w = 0
page_view_box_h = 0


# todo: when change directory redo input_mako.json
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
    with open(p3_f, 'w') as f:
        json.dump(p3_d, f, ensure_ascii = False)


def if_not_exists_build_template_header_n_body(some_rel_dir):
    """
    copy header, also template if necessary, build body from template.svg copy that is in repository directory
    """
    global p3_body_svg

    from_abs_dir = os.path.join(p0_root_abs_dir + '/common', some_rel_dir)
    to_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, some_rel_dir)

    # copy the label_template if necessary
    template_fr = os.path.join(to_abs_dir, 'label_template.svg')
    if not pathlib.Path(template_fr).exists():
        shutil.copy(os.path.join(from_abs_dir, 'label_template.svg'), to_abs_dir)
    body_fw = os.path.join(to_abs_dir, '.label_template_body.svg')

    with open(template_fr) as fr, open(body_fw, 'w') as fw:
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
    global p3_default_fields_l
    global page_view_box_w
    global page_view_box_h

    p1.load_o_create_page_set_up()
    page_view_box_w = 210 - 2 * p1.page_setup_d['margin_w']  # Assuming A4
    page_view_box_h = 297 - 2 * p1.page_setup_d['margin_h']  # Assuming A4

    if p3_fields_rel_dir:
        # either read data,
        p3_f = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, 'template-info.json')
        if pathlib.Path(p3_f).exists():
            with open(p3_f) as f:
                p3_d = json.load(f)
        # or populate missing fields with default information relative to the directory
        # other default information is set at variable initialization
        else:
            p3_d['template_header'] = p3_fields_rel_dir[p3_fields_rel_dir.rfind('_') + 1:] + '唛头'
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
    print(f'Template in {p3_fields_rel_dir} uses {template_fields_set}')
    print(f'Fields selected to feed data are  {p3_d["selected_fields"]}')
    diff_set = template_fields_set - set(p3_d['selected_fields'])
    if diff_set:
        missing_in_template_l = []
        for f in template_fields_set:
            if f not in p3_d['selected_fields']:
                missing_in_template_l.append(f)
        print('The template requires the following fields but those\n'
              'were not found in the data requisition list: ', missing_in_template_l)
    else:
        print('Template fields and requested data match.  The template is operational.')
        # template_f = os.path.join(os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir), 'label_template.svg')
        # subprocess.Popen([
        #     'inkscape',
        #     template_f,
        # ]).wait()


def load_o_create_mako_input_values_json(force_recreate = False):
    global p3_fields_rel_dir
    """
    Creates a json file with variables and values necessary to mako rendering
    :return:
    """
    # will be set in this function
    global p3_selected_fields_values_by_prod_d

    check_if_template_requirements_are_met()
    # make sure global variables are initialized in all situations, outside the loop to do it once only
    filename = os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, '.mako_input.json')
    if pathlib.Path(filename).exists() and not force_recreate:
        with open(filename) as fr:
            p3_selected_fields_values_by_prod_d = json.load(fr)
    else:
        if not p1.p1b_indics_from_contract_l:
            p1.load_p1b_indics_from_contract_l()
        if not p1.all_products_to_be_processed_set:
            p1.load_p1_all_products_to_be_processed_set()
        if load_o_create_p3_fields_info_f():
            # make a skeleton for p3_selected_fields_values_by_prod_d with key = prod
            idx = 0
            temp_d = {}
            for prod in p1.all_products_to_be_processed_set:
                temp_d[prod] = {'i': str(idx + 1), 'prod_n': prod, 'gm_zh': '', 'gm_fr': ''}
                idx += 1

            # prepare to insert translations if needed
            with open(os.path.join(p0_root_abs_dir + '/common', 'zh_fr.json')) as f:
                zh_fr_d = json.load(f)

            # populate the skeleton
            for indc_d in p1.p1b_indics_from_contract_l:  # loop over the big one once
                if indc_d['prod_nr'] in p1.all_products_to_be_processed_set:
                    if indc_d['what'] in p3_d['selected_fields']:  # loop over the smaller more
                        temp_d[indc_d['prod_nr']][indc_d['what']] = indc_d['info']
                        what_zh = indc_d['what']
                        if what_zh in ['clr_zh', 'gm_zh', 'io_zh', 'lr_zh', 'spec_zh']:
                            what_fr = what_zh[:-2] + 'fr'
                            temp_d[indc_d['prod_nr']][what_fr] = zh_fr_d[indc_d['info']]
                        elif what_zh == 'xl_prod_spec':
                            temp_d[indc_d['prod_nr']]['dim'] = re.search(r"\d*x\d*\s*mm", indc_d['info']).group()
                            model = re.search(r"JC-\w*", indc_d['info'])
                            temp_d[indc_d['prod_nr']]['model'] = model.group() if model else 'ISOPLANE'

            # build the dictionary p3_selected_fields_values_by_prod_d with key = i - 1
            for v in temp_d.values():
                p3_selected_fields_values_by_prod_d[str(int(v['i']) - 1)] = v

            with open(filename, 'w') as f:
                json.dump(p3_selected_fields_values_by_prod_d, f, ensure_ascii = False)
        else:
            print('|\n| No template has been selected for display\n|')


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
    with open(template_s) as fr:
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
            os.system('clear')
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
            os.system('clear')
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
                os.system('clear')
                break
            else:
                try:
                    s_i = int(s)
                    if s_i in range(len(drs)):
                        os.system('clear')
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
                                os.system('clear')
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
        # todo: check if this code could be grouped with other render
        if_not_exists_build_template_header_n_body(p3_fields_rel_dir)
        load_o_create_mako_input_values_json()
        render_svg_1_template_1_product()
    else:
        return


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
            with open(p3_f) as f:
                pprint.pprint(f.read())
            print('~~~ File template-info.json closed ~~~')
    else:
        print(f'\nFile {p3_f} not built yet\n')


def display_pdf():
    # todo: avoid having to change directories
    os.chdir(p1.p1_cntrct_abs_dir)
    output_s = p1.p1_d["cntrct_nr"] + '.pdf'
    subprocess.Popen(['xreader', output_s, ])
    os.chdir(p0_root_abs_dir)


def svg_s_to_pdf_deliverable():
    os.chdir(p1.p1_cntrct_abs_dir)
    print_svg_l = [f for f in os.listdir(p1.p1_cntrct_abs_dir) if os.path.isfile(f)
                   and f.endswith('.svg')
                   and f[0] != '.']

    for file in print_svg_l:
        with open(file) as fr, open('.' + file, 'w') as fw:
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
            svg_out = os.path.join(p3_fields_abs_dir, '.1_template.svg')
    else:
        svg_out = os.path.join(p1.p1_cntrct_abs_dir, f'page_{page}.svg')
    fw = open(svg_out, 'w')
    fw.write(header)
    fw.write(f'<rect x="0" y="0"\n'
             f'width="210" height="297"\n'
             f'style="fill:none;stroke-width:0.5;stroke-opacity:1;stroke:#ff00ff" />\n')
    page_x = 100  # page middle - 5mm to center text, assuming A4
    page_y = int(page_view_box_h + 3 * (297 - page_view_box_h) / 4)
    fw.write(
        f"<g>\n<text transform='translate({page_x}, {page_y})' "
        f"style='font-family:{family};font-size:{size};font-style:{style}'>-- {page} --</text>\n</g>\n"
    )
    # assuming A4
    fw.write(f"<g transform='translate({p1.page_setup_d['margin_w']}, {p1.page_setup_d['margin_h']} )'>\n")
    return fw, svg_out


def close_svg_for_output(fw, svg_out):
    fw.write('\n</g>\n</svg>\n')
    fw.close()
    webbrowser.get('firefox').open_new_tab(svg_out)
    # subprocess.Popen(['inkscape', svg_out])


def horizontal_centering_offset(template_view_box_w, spacing_w):
    global page_view_box_w

    n_of_templates_per_row = int(page_view_box_w // template_view_box_w)
    result = (page_view_box_w - n_of_templates_per_row * template_view_box_w - (
        n_of_templates_per_row - 1) * spacing_w) / 2
    return result


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
    oy = None
    if drs:
        svg_out = ''  # svg output filename
        fw = None  # and its file handler
        template_nr = 0  # number templates so as to make headers
        page = 1  # nr of page being built
        for p3_fields_rel_dir in drs:  # looping on templates
            p3_fields_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir)  # dir for header & body
            if_not_exists_build_template_header_n_body(p3_fields_rel_dir)
            with open(os.path.join(p3_fields_abs_dir, '.label_template_header.svg')) as h:
                header = h.read()
            template_nr += 1
            # loading data previously used with this template
            load_o_create_p3_fields_info_f()

            # opening a new page, printing header template in 'page_#.svg'
            # printing body template in page_# svg
            family = re.search(r'(?<=font-family:)([\w-]+)', p3_body_svg).groups()[0]
            size = re.search(r'(?<=font-size:)(\d+\.*\d*\w*)', p3_body_svg).groups()[0]
            style = re.search(r'(?<=font-style:)([\w-]+)', p3_body_svg).groups()[0]
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
            with open(os.path.join(to_abs_dir, 'label_template.svg')) as f:
                mako_template = Template(
                    filename = os.path.join(p3_fields_abs_dir, '.label_template_body.svg'),
                    input_encoding = 'utf-8'
                )
                contents = f.read()
                m = re.search(r'(?<=viewBox=")(\d) (\d) (\d+.*\d*) (\d+\.*\d*)', contents)
                if m.groups()[0] != '0' or m.groups()[1] != '0':
                    print("Error in building 'label_template.svg': origin is not (0, 0), exiting program ...")
                    exit()
                template_view_box_w = float(m.groups()[2])
                template_view_box_h = float(m.groups()[3])
            spacing_w = suggest_spacing_calc(page_view_box_w, template_view_box_w)
            spacing_h = suggest_spacing_calc(page_view_box_h - p3_d['header_height'], template_view_box_h)
            assert template_view_box_w + spacing_w <= page_view_box_w, \
                "write_templates: ! template width + spacing width don't fit in the page"
            assert template_view_box_h + spacing_h <= page_view_box_h, \
                'write_templates: ! template height + spacing height don\'t fit in the page'

            # write the header for this template
            fw.write(
                f'<svg width="{page_view_box_w}" height="{p3_d["header_height"]}" x="0" y="{oy}">\n'
                f'<rect x="0" y="0"\n'
                f'width="100%" height="100%"\n'
                f'style="fill:none;stroke-width:0.5;stroke-opacity:1;stroke:#ff00ff" />\n'
                f'<text x="0%" y="100%" dominant-baseline="text-after-edge" '
                f'style="font-family:{family};font-size:{size};font-style:{style}">'
                f'{template_nr}. {p3_d["template_header"]}</text>\n</svg>\n'
            )
            if not oy:  # vertical positioning in page_view_box_h
                oy = - spacing_h
                if page == 1:
                    oy = 150

            # run mako.template.Template
            ox = - spacing_w + horizontal_centering_offset(template_view_box_w, spacing_w)
            oy += p3_d['header_height']
            lngth = len(p3_selected_fields_values_by_prod_d)  # nr of products in the contract
            i = 0  # index of the template to print
            while i < (1 if only_1_prod else lngth):
                # writing horizontally while there templates to print
                while ox + template_view_box_w <= page_view_box_w and i < (1 if only_1_prod else lngth):
                    offset_x = ox + spacing_w
                    offset_y = oy + spacing_h
                    fw.write(r"<g transform = 'translate(" + f"{offset_x}, {offset_y})'>\n")
                    barcode_f = os.path.join(
                        os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir),
                        prod_n_to_barcode(p3_selected_fields_values_by_prod_d[str(i)]['prod_n'])
                    )
                    if pathlib.Path(barcode_f).exists():
                        fw.write("<g transform = 'translate(41,17)'>\n")
                        with open(barcode_f) as f:
                            fw.write(f.read())
                        fw.write("</g>\n")
                        fw.write("<g transform = 'translate(41,55)'>\n")
                        with open(barcode_f) as f:
                            fw.write(f.read())
                        fw.write("</g>\n")
                    # print(  # for debug purposes
                    #     p3_selected_fields_values_by_prod_d[str(i)]['i'],
                    #     p3_selected_fields_values_by_prod_d[str(i)]['prod_n']
                    # )
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
                # check if there is still space to write the next one, if not open a new page
                if oy + template_view_box_h + spacing_h > page_view_box_h:
                    if i != lngth or template_nr != len(drs):  # to avoid printing a blank page when no data left
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
        close_svg_for_output(fw, svg_out)
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


def render_title_page():
    global p3_fields_rel_dir
    global p3_d
    global p3_selected_fields_values_by_prod_d

    # load data from p1.p1e_specific_fields_d_of_d, put in a list of dicts
    p3_fields_rel_dir = p2.p2_load_templates_info_l()[0]
    load_o_create_p3_fields_info_f()
    load_p3_all_specific_fields_l()

    # copy first label on cover page template
    p3_fields_abs_dir = os.path.join(p1.p1_cntrct_abs_dir, p3_fields_rel_dir)
    svg_in = os.path.join(p3_fields_abs_dir, '.1_product.svg')
    if svg_in:
        with open(svg_in) as fr:
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
        with open(os.path.join(p0_root_abs_dir + '/common/.title_page_template.svg')) as fr:
            lines = fr.readlines()
        svg_out = os.path.join(p1.p1_cntrct_abs_dir, '.title_page_template.svg')
        with open(svg_out, 'w') as fw:
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
        with open(cover_s, 'w') as fw:
            fw.write(mako_template.render(
                contract_n = p1.p1_d["cntrct_nr"],
                **p3_selected_fields_values_by_prod_d['0']
            ))
        webbrowser.get('Firefox').open_new_tab(cover_s)
    else:
        print(f'{svg_in}: no such file, should be build before cover page')


def display_all():
    global p3_fields_rel_dir
    # read existing templates
    drs = p2.p2_load_templates_info_l()
    if drs:
        # for each template that has been created as a subdir to p1.p1_cntrct_abs_dir
        for p3_fields_rel_dir in drs:
            # use data on disk, if not on disk create with default values
            if load_o_create_p3_fields_info_f():
                render_svg_1_template_1_product()
                if p3_fields_rel_dir == drs[0]:
                    render_title_page()
                render_svg_1_template_all_products()
    render_svg_all_templates_all_products()
    svg_s_to_pdf_deliverable()


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
            os.system('clear')
            break
        elif s == 'a':
            add_fields()
        elif s == 'd':
            del_fields()
        else:
            print(f'{s} is not an option, try again')

    # todo: check what template suggest and is missing
    save_template_info_json()
    # if_not_exists_build_template_header_n_body(p3_fields_rel_dir)
    load_o_create_mako_input_values_json(force_recreate = True)
    # render_svg_1_template_1_product()


def select_a_template_for_editing():
    global p3_fields_rel_dir

    print('~~~ select a template to edit ~~~')
    p.mod_lev_1_menu = p.menu
    p.menu = 'select_a_template_for_editing'
    # select_specific_fields_context_func()
    drs = p1.read_dirs(p1.p1_cntrct_abs_dir)
    if drs:
        for i in range(len(drs)):
            print(str(i) + '. ' + drs[i][2:])
        while True:
            s = input('\nEnter nr of template to be edited, \'b\' to return : ')
            if s == 'b':
                os.system('clear')
                p.menu = p.mod_lev_1_menu
                break
            else:
                try:
                    s_i = int(s)
                    if s_i in range(len(drs)):
                        os.system('clear')
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


def select_specific_fields_context_func(prompt = True):  # todo: check it this could be different from next function
    print('~~~ Step 3: Selecting fields to print for each template ~~~\n')
    display_specific_fields_for_all_products()
    print('~~~ Now processing contract #: ', p1.p1_d["cntrct_nr"] if p1.p1_d["cntrct_nr"] else None)
    print('~~~ Now working on template: ', p3_fields_rel_dir if p3_fields_rel_dir else 'None selected')
    print('~~~ Specific fields selected so far:', p3_d['selected_fields'])
    print(60 * '-', '\n\n')
    if prompt:
        print('\n>>> Select an action: ')


def select_edit_context_func():
    print('~~~ Step 3: Selecting fields to print for each template / Edit a template ~~~\n')
    display_specific_fields_for_all_products()
    print('~~~ Now processing contract #: ', p1.p1_d["cntrct_nr"] if p1.p1_d["cntrct_nr"] else None)
    print('~~~ Now working on template: ', p3_fields_rel_dir if p3_fields_rel_dir else 'None selected')
    print('~~~ Specific fields selected so far:', p3_d['selected_fields'])
    print(60 * '-', '\n\n')
    print('\n>>> Select an action: ')


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
    return temp_s + '.svg'


def generate_barcode_files():
    prod_l = list(p1.p1_cntrct_info_d['all_products_to_be_processed_set'])
    # make a list of files with 12 digits based on stripped prod_nr
    ean_prod_l = []
    for prod in prod_l:
        ean_prod_l.append(prod_n_to_barcode(prod))
    # pprint.pprint(ean_prod_l)
    return ean_prod_l


def create_barcode_files():
    global p3_fields_rel_dir
    for filename in generate_barcode_files():
        shutil.copy(
            os.path.join(p0_root_abs_dir + '/common', 'empty_bar_code_file.svg'),
            os.path.join(p1.p1_cntrct_abs_dir + '/' + p3_fields_rel_dir, filename)
        )


context_func_d = {
    'select_specific_fields': select_specific_fields_context_func,
    'select_a_template_for_editing': select_specific_fields_context_func,
    'debug': select_specific_fields_context_func,
}


def step_3__select_fields_to_print_for_each_template_选择每种标签类型的资料():
    global p3_fields_rel_dir
    # make sure p1 infrastructure is in place
    if not p1.load_contract_info_d():
        print('p1 has not run successfully')
    if not p1.read_dirs(p1.p1_cntrct_abs_dir):
        p2.create_default_templates()
    if not p3_fields_rel_dir:
        drs = p1.read_dirs(p1.p1_cntrct_abs_dir)
        p3_fields_rel_dir = drs[0]

    # initializing menus last, so that context functions display most recent information
    p.menu = 'select_specific_fields'
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '66': svg_s_to_pdf_deliverable,
            '1': select_a_template_for_editing,
            '2': render_svg_all_templates_all_products,
            '3': display_all,
            '4': check_all_templates_have_correct_fields,
            'b': p.back_to_main_退到主程序,
            'q': p.normal_exit_正常出口,
            'd': p.debug,
        },
        'select_a_template_for_editing': {
            '55': create_barcode_files,
            '44': edit_label_template_svg,
            '0': scrap_template_for_fields,
            '1': check_if_template_requirements_are_met,
            '2': edit_fields,
            '3': p1.process_selected_contract,
            '4': edit_paragraph_headers,
            '5': render_svg_1_template_1_product,
            '6': render_title_page,
            '7': render_svg_1_template_all_products,
            'b': p.back_后退,
            'q': p.normal_exit_正常出口,
        },
        'debug': {
            '44': render_title_page,
            '2': display_or_load_output_overview,
            '6': p1.display_p1_cntrct_info_d,
            '7': p1.display_p1_cntrct_info_f,
            '8': display_p3_fields_info_d,
            '9': display_p3_fields_info_f,
            'b': p.back_后退,
            'q': p.normal_exit_正常出口,
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
    step_3__select_fields_to_print_for_each_template_选择每种标签类型的资料()
    p.run()


if __name__ == '__main__':
    main()
