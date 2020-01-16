#!/usr/bin/env python3
import json
import os
import pprint
import re
import shutil
import subprocess
import webbrowser
from mako.template import Template
import p0_menus as p
import p1_select_contract as p1
import p2_select_labels as p2

p0_root_abs_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located
p3_fields_info_d = {}  # info on fields currently being edited
p3_fields_info_f = None  # info on fields currently being edited
p3_fields_rel_dir = ''  # currently working fields directory
p3_all_specific_fields_l = []  # list of fields that are product specific, read from p1e_specific_fields_d_of_d
p3_selected_fields_l = []  # list of fields selected to be printed in the selected label (or collection of fields)
p3_default_fields = ["xl_prod_spec", "u_parc", 'plstc_bg']
p3_selected_fields_values_by_prod_d = {}  # field values for current product, as stored in mako_input.json
p3_body_svg = ''  # content of label_template_body.svg
p3_header_height = 7
p3_page_view_box_w = 170
p3_page_view_box_h = 257


def p3_select_specific_fields_context_func():
    display_specific_fields_for_all_products()
    print('~~~ Now processing contract #: ', p1.p1_contract_nr if p1.p1_contract_nr else None)
    print('~~~ Now working on label: ', p3_fields_rel_dir)
    print('~~~ Specific fields selected so far:', p3_selected_fields_l)
    print('\n>>> Select an action: ')


context_func_d = {
    'select_specific_fields': p3_select_specific_fields_context_func,
}


def init():
    # make sure p1 infrastructure is in place
    if not p1.p1_load_contract_info_d():
        print('p1 has not run successfully')
    if not p1.read_dirs(p1.p1_contract_abs_dir):
        p2.create_default_labels()

    global p3_all_specific_fields_l
    p3_all_specific_fields_l = []
    global p3_selected_fields_l
    if p3_read_fields_info_d_from_disk():
        p3_selected_fields_l = p3_fields_info_d['selected_fields']
    else:
        p3_selected_fields_l = []
        print('\nNo specific fields selected at this point\n')

    # initializing menus last, so that context functions display most recent information
    p.menu = 'select_specific_fields'
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '0': render_all_label_all_products,
            '1': process_all_labels_with_default_specific_fields,
            '2': display_or_load_output_overview,
            '3': select_a_label_n_edit_fields,
            '6': p1.display_p1_contract_info_d,
            '7': p1.display_p1_contract_info_f,
            '8': display_p3_fields_info_d,
            '9': display_p3_fields_info_f,
            'b': p.back_to_main,
            'q': p.normal_exit,
        }
    }
    if not p.main_menus:
        p.main_menus = p.menus
    if __name__ == '__main__':
        p.mod_lev_1_menu = p.menu
        p.mod_lev_1_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}


def load_p3_all_specific_fields_l():
    global p3_all_specific_fields_l

    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d()
    p3_all_specific_fields_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))


def process_all_labels_with_default_specific_fields():
    global p3_fields_rel_dir
    global p3_selected_fields_l
    global p3_fields_info_d
    global p3_all_specific_fields_l
    global p3_fields_info_f

    # p3_select_specific_fields_context_func()
    load_p3_all_specific_fields_l()

    # read existing labels
    drs = p2.p2_load_labels_info_l()
    if drs:
        # for each label that has been created as a subdir to p1.p1_contract_abs_dir
        for p3_fields_rel_dir in drs:
            if p3_read_fields_info_d_from_disk():
                p3_selected_fields_l = p3_fields_info_d['selected_fields']
            for f in p3_default_fields:
                if f in p3_all_specific_fields_l and f not in p3_selected_fields_l:
                    p3_selected_fields_l.append(f)
            save_label_info_json()
            build_template_header_n_body(p3_fields_rel_dir)
            make_mako_input_val_json(p3_fields_rel_dir)
            render_1_label_1_product()
            render_1_label_all_products()


def display_or_load_output_overview():
    global p3_fields_rel_dir
    global p3_fields_info_d

    print('~~~ Overview')
    _, drs, _ = next(os.walk(p1.p1_contract_abs_dir))
    for dr in drs:
        print(dr)
        p3_fields_rel_dir = dr
        if p3_read_fields_info_d_from_disk():
            print('\t', p3_fields_info_d['selected_fields'])
    print('~~~')


def select_a_label_n_edit_fields():
    global p3_fields_rel_dir
    global p3_selected_fields_l

    # read existing labels
    drs = p1.read_dirs(p1.p1_contract_abs_dir)
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
                        p3_fields_rel_dir = drs[s_i]
                        # load fields already selected for label as they are on file
                        if p3_read_fields_info_d_from_disk():
                            p3_selected_fields_l = p3_fields_info_d['selected_fields']
                        print(f'now ready to work on {p3_fields_rel_dir}')
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

        save_label_info_json()
        build_template_header_n_body(p3_fields_rel_dir)
        make_mako_input_val_json(p3_fields_rel_dir)
        render_1_label_1_product()
    else:
        return


def save_label_info_json():
    global p3_fields_info_f
    global p3_fields_info_d

    p3_fields_info_d['selected_fields'] = p3_selected_fields_l
    p3_fields_info_f = os.path.join(p1.p1_contract_abs_dir + '/' + p3_fields_rel_dir, 'label-info.json')
    with open(p3_fields_info_f, 'w') as f:
        json.dump(p3_fields_info_d, f, ensure_ascii = False)


def display_selected_fields():
    with open(os.path.join(p1.p1_contract_abs_dir, 'p4_' + p1.p1_contract_nr + '_fields_from_contract_l.json')) as f:
        p3_fields_from_contract_l = json.load(f)
    indic_val_d = {}
    for option in p3_all_specific_fields_l:
        temp_d = {}
        for indic in p3_fields_from_contract_l:
            if indic['what'] == option:
                temp_d[indic['prod_nr']] = indic['info']
        indic_val_d[option] = temp_d

    for option in p3_all_specific_fields_l:
        nr_tabs = 1 if len(option) >= 8 else 2
        print(option, nr_tabs * '\t', list(indic_val_d[option].values()))
    print('\nAlready selected: ', p3_selected_fields_l, '\n')
    print('Currently processing ', p3_fields_rel_dir)


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
    global p3_fields_rel_dir
    global p3_selected_fields_l
    global p3_all_specific_fields_l

    # if not p3_selected_fields_l:
    #     p3_selected_fields_l = ["03.Prod_spec", "pack", "total_qty"]

    # p3_select_specific_fields_context_func()
    if not p1.p1e_specific_fields_d_of_d:
        p1.load_p1e_specific_fields_d_of_d()
    p3_all_specific_fields_l = list(next(iter(p1.p1e_specific_fields_d_of_d.values())))
    # select from p3_all_specific_fields_l and put in p3_selected_fields_l
    while True:
        print(f'~~~ Already selected:\n{p3_selected_fields_l}\n~~~ Can be added:')
        not_yet_l = []
        for o in p3_all_specific_fields_l:
            if o not in p3_selected_fields_l:
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
                    p3_selected_fields_l.append(not_yet_l[s_i])
                    # break
                else:
                    print('!\n! Integer, but not an option, try again\n!')
            except ValueError:
                print('!\n! That\'s not an integer, try again\n!')
    save_label_info_json()


def del_fields():
    global p3_selected_fields_l
    global p3_fields_info_f
    global p3_fields_info_d

    while True:
        print(f'~~~ Already selected:')
        for i in range(len(p3_selected_fields_l)):
            print(f'{i}. {p3_selected_fields_l[i]}')
        print(f'~~~')
        s = input('Enter nr of indicator to delete, \'b\' to return : ')
        if s == 'b':
            os.system('clear')
            break
        else:
            try:
                s_i = int(s)
                if s_i in range(len(p3_selected_fields_l)):
                    del p3_selected_fields_l[s_i]
                    # break
                else:
                    print('!\n! Integer, but not an option, try again\n!')
            except ValueError:
                print('!\n! That\'s not an integer, try again\n!')

    save_label_info_json()


def p3_read_fields_info_d_from_disk():
    global p3_fields_info_f
    global p3_fields_info_d
    global p3_fields_rel_dir

    if p3_fields_rel_dir:
        p3_fields_info_f = os.path.join(p1.p1_contract_abs_dir + '/' + p3_fields_rel_dir, 'label-info.json')
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
    tmp_l = [8 * ' ']
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


def make_mako_input_val_json(some_rel_dir):
    """
    Creates a json file with variables and values necessary to mako rendering
    :param some_rel_dir:
    :return:
    """
    # will be set in this function
    global p3_selected_fields_values_by_prod_d
    # make sure global variables are set in all situations, outside the loop to do it once only
    if not p1.p1b_indics_from_contract_l:
        p1.load_p1b_indics_from_contract_l()
    if not p1.p1_all_products_to_be_processed_set:
        p1.load_p1_all_products_to_be_processed_set()

    if p3_selected_fields_l:
        # make a skeleton for p3_selected_fields_values_by_prod_d with key = prod
        idx = 0
        temp_d = {}
        for prod in p1.p1_all_products_to_be_processed_set:
            temp_d[prod] = {'i': idx + 1, 'prod_n': prod}
            idx += 1

        # populate the skeleton
        for indc_d in p1.p1b_indics_from_contract_l:  # loop over the big one once
            if indc_d['prod_nr'] in p1.p1_all_products_to_be_processed_set:
                if indc_d['what'] in p3_selected_fields_l:  # loop over the smaller more
                    temp_d[indc_d['prod_nr']][indc_d['what']] = indc_d['info']

        # build p3_selected_fields_values_by_prod_d with key = i - 1
        for v in temp_d.values():
            p3_selected_fields_values_by_prod_d[v['i'] - 1] = v

        filename = os.path.join(p1.p1_contract_abs_dir + '/' + some_rel_dir, 'mako_input.json')
        with open(filename, 'w') as f:
            json.dump(p3_selected_fields_values_by_prod_d, f, ensure_ascii = False)
    else:
        print('No label has been selected for display')


def render_1_label_1_product():
    # building the html page
    p3_fields_abs_dir = os.path.join(p1.p1_contract_abs_dir, p3_fields_rel_dir)
    filename = os.path.join(p3_fields_abs_dir, 'label_template_header.svg')
    with open(filename) as h:
        header = h.read()
    svg_out = os.path.join(p3_fields_abs_dir, 'page_0.svg')
    with open(svg_out, 'w') as f:
        f.write(header)
        filename = os.path.join(p3_fields_abs_dir, 'label_template_body.svg')
        label_template = Template(filename = filename, input_encoding = 'utf-8')
        f.write(label_template.render(**p3_selected_fields_values_by_prod_d[0]))
        f.write('</svg>')
    subprocess.Popen([r'firefox', svg_out])


def render_1_label_all_products():
    """
    Print min and max spacing depending on # of labels to be laid in rows & columns
    """
    global p3_fields_rel_dir
    global p3_selected_fields_values_by_prod_d
    global p3_fields_rel_dir

    from_abs_dir = os.path.join(p0_root_abs_dir + '/common', p3_fields_rel_dir)

    with open(os.path.join(from_abs_dir, 'label_template.svg')) as f:
        contents = f.read()
        m = re.search(r'(?<=viewBox=")(\d) (\d) (\d+.*\d*) (\d+\.*\d*)', contents)
        if m.groups()[0] != '0' or m.groups()[1] != '0':
            print("Error in building 'label_template.svg': origin is not (0, 0), exiting program ...")
            exit()

        label_view_box_w = float(m.groups()[2])
        label_view_box_h = float(m.groups()[3])  # label_view_box_h, label_view_box_h
    spacing_w = suggest_spacing_calc(p3_page_view_box_w, label_view_box_w)  # first horizontally, w = width
    spacing_h = suggest_spacing_calc(p3_page_view_box_h - p3_header_height, label_view_box_h)  # then vertically

    """
    assemble prepared svg files
    output to out.svg
    """
    p3_fields_abs_dir = os.path.join(p1.p1_contract_abs_dir, p3_fields_rel_dir)

    family = re.search(r'(?<=font-family:)([\w-]+)', p3_body_svg).groups()[0]
    size = re.search(r'(?<=font-size:)(\d+\.*\d*\w*)', p3_body_svg).groups()[0]
    style = re.search(r'(?<=font-style:)([\w-]+)', p3_body_svg).groups()[0]

    assert label_view_box_w + spacing_w <= p3_page_view_box_w, \
        "write_labels: ! label + spacing width don't fit in the page"
    assert label_view_box_h + spacing_h <= p3_page_view_box_h, \
        'write_labels: ! label + spacing height don\'t fit in the page'

    # printing labels in pages, when a page is full, open a new one
    svg_in = os.path.join(p3_fields_abs_dir, 'label_template_header.svg')
    with open(svg_in) as h:
        header = h.read()

    label_template = Template(filename = os.path.join(p3_fields_abs_dir, 'label_template_body.svg'),
                              input_encoding = 'utf-8')

    N = len(p3_selected_fields_values_by_prod_d)  # nr of products in the contract
    page = 1  # nr of page being built
    i = 0  # index of the label to print
    ox = - spacing_w + horizontal_centering_offset(label_view_box_w, spacing_w)
    oy = - spacing_h + p3_header_height

    while i < N:  # enumerating over each item in the contract
        # opening a new page
        svg_out = os.path.join(p3_fields_abs_dir, f'page_{page}.svg')
        with open(svg_out, 'w') as f:
            f.write(header)
            f.write("<g transform='translate(20, 20)'>\n")
            if page == 1:
                f.write(
                    "<g>\n<text transform='translate(0, 5)' "
                    f"style='font-family:{family};font-size:{size};font-style:{style}'>1. 外箱的唛头</text>\n</g>\n")
            while oy + label_view_box_h + spacing_h <= p3_page_view_box_h and i < N:
                while ox + label_view_box_w + spacing_w <= p3_page_view_box_w and i < N:
                    offset_x = ox + spacing_w
                    offset_y = oy + spacing_h
                    f.write(r"<g transform = 'translate(" + f"{offset_x}, {offset_y})'>\n")
                    f.write(label_template.render(**p3_selected_fields_values_by_prod_d[i]))
                    f.write('</g>\n')
                    ox += label_view_box_w + spacing_w
                    i += 1
                ox = - spacing_w + horizontal_centering_offset(label_view_box_w, spacing_w)
                oy += label_view_box_h + spacing_h
            oy = - spacing_h + p3_header_height
            f.write('\n</g>\n</svg>\n')
        webbrowser.get('firefox').open_new_tab(svg_out)
        page += 1


def render_all_label_all_products():
    """
    Print min and max spacing depending on # of labels to be laid in rows & columns
    """
    global p3_fields_rel_dir
    global p3_selected_fields_l
    global p3_fields_info_f
    global p3_fields_info_d
    global p3_all_specific_fields_l
    global p3_selected_fields_values_by_prod_d
    global p3_body_svg

    # load data from p1.p1e_specific_fields_d_of_d, put in a list of dicts
    load_p3_all_specific_fields_l()

    # read existing labels
    drs = p2.p2_load_labels_info_l()
    svg_out = ''
    fw = None
    if drs:
        page = 1  # nr of page being built
        for p3_fields_rel_dir in drs:
            build_template_header_n_body(p3_fields_rel_dir)
            family = re.search(r'(?<=font-family:)([\w-]+)', p3_body_svg).groups()[0]
            size = re.search(r'(?<=font-size:)(\d+\.*\d*\w*)', p3_body_svg).groups()[0]
            style = re.search(r'(?<=font-style:)([\w-]+)', p3_body_svg).groups()[0]
            # opening a new page
            p3_fields_abs_dir = os.path.join(p1.p1_contract_abs_dir, p3_fields_rel_dir)
            # printing labels in pages, when a page is full, open a new one
            svg_in = os.path.join(p3_fields_abs_dir, 'label_template_header.svg')
            with open(svg_in) as h:
                header = h.read()
            if page == 1:
                svg_out = os.path.join(p3_fields_abs_dir, f'page_{page}.svg')
                fw = open(svg_out, 'w')
                fw.write(header)
                fw.write("<g transform='translate(20, 20)'>\n")
                fw.write(
                    "<g>\n<text transform='translate(0, 5)' "
                    f"style='font-family:{family};font-size:{size};font-style:{style}'>1. 外箱的唛头</text>\n</g>\n")
            # for each label that has been created as a subdir to p1.p1_contract_abs_dir
            # read fields that were last used with this label
            if p3_read_fields_info_d_from_disk():
                p3_selected_fields_l = p3_fields_info_d['selected_fields']
            # complete the list with possibly missing default fields
            for field in p3_default_fields:
                if field in p3_all_specific_fields_l and field not in p3_selected_fields_l:
                    p3_selected_fields_l.append(field)
            # update disk version
            save_label_info_json()
            # from template build the body necessary to multiply labels  todo: make sure all fields are in place
            # build_template_header_n_body(p3_fields_rel_dir)  todo: remove all together
            # build the value input file for mako
            make_mako_input_val_json(p3_fields_rel_dir)

            # read view box values from template_body so as to compute spacings
            to_abs_dir = os.path.join(p1.p1_contract_abs_dir, p3_fields_rel_dir)
            with open(os.path.join(to_abs_dir, 'label_template.svg')) as f:
                contents = f.read()
                m = re.search(r'(?<=viewBox=")(\d) (\d) (\d+.*\d*) (\d+\.*\d*)', contents)
                if m.groups()[0] != '0' or m.groups()[1] != '0':
                    print("Error in building 'label_template.svg': origin is not (0, 0), exiting program ...")
                    exit()

                label_view_box_w = float(m.groups()[2])
                label_view_box_h = float(m.groups()[3])  # label_view_box_h, label_view_box_h
            spacing_w = suggest_spacing_calc(p3_page_view_box_w, label_view_box_w)  # first horizontally, w = width
            spacing_h = suggest_spacing_calc(p3_page_view_box_h - p3_header_height, label_view_box_h)  # then vertically

            """
            assemble prepared svg files
            output to out.svg
            """

            assert label_view_box_w + spacing_w <= p3_page_view_box_w, \
                "write_labels: ! label + spacing width don't fit in the page"
            assert label_view_box_h + spacing_h <= p3_page_view_box_h, \
                'write_labels: ! label + spacing height don\'t fit in the page'

            label_template = Template(filename = os.path.join(p3_fields_abs_dir, 'label_template_body.svg'),
                                      input_encoding = 'utf-8')

            N = len(p3_selected_fields_values_by_prod_d)  # nr of products in the contract
            i = 0  # index of the label to print
            ox = - spacing_w + horizontal_centering_offset(label_view_box_w, spacing_w)
            oy = - spacing_h + p3_header_height

            while i < N:  # enumerating over each item in the contract
                # writing horizontally while there are labels to print
                while i < N:
                    # writing vertically while there labels to print
                    while ox + label_view_box_w + spacing_w <= p3_page_view_box_w and i < N:
                        offset_x = ox + spacing_w
                        offset_y = oy + spacing_h
                        fw.write(r"<g transform = 'translate(" + f"{offset_x}, {offset_y})'>\n")
                        fw.write(label_template.render(**p3_selected_fields_values_by_prod_d[i]))
                        fw.write('</g>\n')
                        ox += label_view_box_w + spacing_w
                        i += 1
                    ox = - spacing_w + horizontal_centering_offset(label_view_box_w, spacing_w)
                    oy += label_view_box_h + spacing_h
                    # after each line check if there is still space to write the next one, if not open a new page
                    if oy + label_view_box_h + spacing_h > p3_page_view_box_h:
                        fw.write('\n</g>\n</svg>\n')
                        fw.close()
                        webbrowser.get('firefox').open_new_tab(svg_out)
                        page += 1
                        svg_out = os.path.join(p3_fields_abs_dir, f'page_{page}.svg')
                        fw = open(svg_out, 'w')
                        fw.write(header)
                        fw.write("<g transform='translate(20, 20)'>\n")
                oy = - spacing_h + p3_header_height
                fw.write('\n</g>\n</svg>\n')
                fw.close()


def build_template_header_n_body(some_rel_dir = None):
    """
    copy header, build body from template svg
    :param some_rel_dir:
    :return:
    """

    from_abs_dir = os.path.join(p0_root_abs_dir + '/common', some_rel_dir if some_rel_dir else '1.Outer_box_外箱')
    to_abs_dir = os.path.join(p1.p1_contract_abs_dir, some_rel_dir if some_rel_dir else '1.Outer_box_外箱')

    # copy the label_template if necessary
    template_fr = os.path.join(to_abs_dir, 'label_template.svg')
    if not os.path.exists(template_fr):
        shutil.copy(os.path.join(from_abs_dir, 'label_template.svg'), to_abs_dir)
    body_fw = os.path.join(to_abs_dir, 'label_template_body.svg')

    global p3_body_svg
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
    if not os.path.exists(os.path.join(to_abs_dir, 'label_template_header.svg')):
        shutil.copy(os.path.join(p0_root_abs_dir + '/common', 'label_template_header.svg'), to_abs_dir)


def suggest_spacing_calc(lgth, label_view_box):
    n_of_labels_per_dim = int(lgth // label_view_box)
    return min(10, int((lgth - n_of_labels_per_dim * label_view_box) / max(1, (n_of_labels_per_dim - 1))))


def horizontal_centering_offset(label_view_box_w, spacing_w):
    n_of_labels_per_row = int(p3_page_view_box_w // label_view_box_w)
    result = (p3_page_view_box_w - n_of_labels_per_row * label_view_box_w - (n_of_labels_per_row - 1) * spacing_w) / 2
    return result


def main():
    """ Driver """
    init()
    p.run()


if __name__ == '__main__':
    main()
