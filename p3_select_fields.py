#!/usr/bin/env python3
import json
import os
import pprint

import u_global_values as g
import u_menus as m

p0_root_dir = os.path.dirname(os.path.abspath(__file__))  # root directory where the program is located

class Controller:
    def __init__(self):  # use to be (self, p1e_specific_indics_d_of_d)
        """
            if no information is in the global variable dictionary then load it from disk
            """
        self.menu = 'p7_select_specific_indicators'
        m.menu = self.menu
        self.menus = {
            self.menu: {
                '1': self.create_selected_indicators_set,
                '6': g.display_p2_labels_info_d,
                '7': g.display_p2_labels_info_f,
                '8': g.display_p7_label_info_d,
                '9': g.display_p7_label_info_f,
                'm': m.back_to_main,
                'q': m.normal_exit,
            }
        }
        m.menus = self.menus
        self.p7_specific_indics_d_of_d = {}
        self.options_l = []
        self.sample_d = {}
        if g.p2_load_labels_info_d():
            self.already_selected_l = g.p3_label_info_d['selected_indicators']
        else:
            self.already_selected_l = []
            print('\nNo p7 output at this point\n')

    def create_selected_indicators_set(self):

        with open(os.path.join(g.p1_contract_dir, g.p2_labels_info_d['p6_extract_specifics'])) as fj:
            self.p7_specific_indics_d_of_d = json.load(fj)
        self.options_l = list(next(iter(self.p7_specific_indics_d_of_d.values())))

        # function factory: defining what each label function should be doing
        def make_f(indic):
            def func():
                self.already_selected_l.append(indic)
                m.menu = self.menu
                m.menus = self.menus

            func.__name__ = indic  # as function is not read_program_info before being called for execution
            return func

        functions_d = {}
        for option in self.options_l:
            functions_d[option] = make_f(option)

        def back():
            m.menu = self.menu
            m.menus = self.menus

        assert back == back  # unless Lint would report back is not used

        m.menu = 'Select label to add'
        m.menus = {m.menu: {}}
        for i in range(len(self.options_l)):
            if self.options_l[i] not in self.already_selected_l:
                m.menus[m.menu][f'{i}'] = functions_d[self.options_l[i]]
        m.menus[m.menu]['m'] = eval('back')
        m.run(self.p7_display_selected_indicators)  # argument to give context for decision
        g.p3_label_info_d['selected_indicators'] = self.already_selected_l

        with open(g.p3_label_info_f, 'w') as f:
            json.dump(g.p3_label_info_d, f, ensure_ascii = False)
        # writing the input file for Mako
        mako_input = ''
        with open(os.path.join('..', 'p4_' + g.p1_contract_nr + '_indics_from_contract_l.json')) as f:
            p7_indcs_from_contract_l = json.load(f)
        if self.already_selected_l:
            # building the header
            mako_input += 'idx, prod_n'
            for indc in self.already_selected_l:
                mako_input += ', ' + indc
            mako_input += '\n'
            # building the body
            indc_by_prod = {}
            for prod in g.p5_all_products_to_be_processed_set:
                indc_by_prod[prod] = {}
            for indc_c in p7_indcs_from_contract_l:  # loop over the big one once
                if indc_c['what'] in self.already_selected_l:  # loop over the smaller more
                    indc_by_prod[indc_c['prod_nr']][indc_c['what']] = indc_c['info']
            idx = 0
            for prod in indc_by_prod.keys():
                mako_input += str(idx)
                mako_input += ', ' + prod
                for k in indc_by_prod[prod].keys():
                    mako_input += ', ' + str(indc_by_prod[prod][k])
                mako_input += '\n'
                idx += 1

            with open(g.p3_lbl_sel + '_mako_input.csv', 'w') as f:
                f.write(mako_input)

    def p7_display_selected_indicators(self):
        with open(os.path.join('..', 'p4_' + g.p1_contract_nr + '_indics_from_contract_l.json')) as f:
            p7_indics_from_contract_l = json.load(f)
        indic_val_d = {}
        for option in self.options_l:
            temp_d = {}
            for indic in p7_indics_from_contract_l:
                if indic['what'] == option:
                    temp_d[indic['prod_nr']] = indic['info']
            indic_val_d[option] = temp_d

        for option in self.options_l:
            nr_tabs = 1 if len(option) >= 8 else 2
            print(option, nr_tabs * '\t', list(indic_val_d[option].values()))
        print('\nAlready selected: ', self.already_selected_l, '\n')
        print('Currently in: ', os.path.relpath(os.getcwd(), os.getcwd() + '..'))
        m.display_context_in_most_cases()


p3_lbl_dir = None  # currently working label directory
p3_lbl_sel = None  # current label

p3_label_info_d = {}  # info on label currently being edited
p3_label_info_f = None  # info on label currently being edited


def display_p3_label_info_d():
    global p3_label_info_d
    print('~~~ Reading label-info global value ~~~')
    pprint.pprint(p3_label_info_d)
    print(p3_label_info_d)
    print('~~~ Finished reading label-info global value ~~~')


def display_p3_label_info_f():
    global p3_label_info_f

    if p3_label_info_d:
        if os.path.isfile(p3_label_info_f):
            print('~~~ Reading label-info.json file contents ~~~')
            with open(p3_label_info_f) as f:
                pprint.pprint(f.read())
            print('~~~ File label-info.json closed ~~~')
    else:
        print(f'\nFile {p3_label_info_f} not built yet\n')


already_selected_l = []
p7_specific_indics_d_of_d = {}
header_height = 7
page_view_box_w = 170
page_view_box_h = 257
options_l = []



def create():
    create_or_update()


def update():
    create_or_update(False)


def create_or_update(default=True):
    global already_selected_l
    global options_l
    global p7_specific_indics_d_of_d

    drs = read_dirs(p1.p1_contract_dir)
    if not drs:
        create_label_dirs(standard_labels_l)
    # documenting in memory but not on disk, so as to keep the option of editing out of program
    # then p1.p1_labels_info_d and p1.p1_labels_info_f will look different
    # p1.p1_labels_info_d['p6_label_l'] = read_dirs(p1.p1_contract_dir)

    # process_default_contract canonical p3_lbl_dir and p3_lbl_sel
    for dr in drs:
        os.chdir(p1.p1_contract_dir + '/' + dr)
        g.p3_lbl_sel = dr
        g.p3_lbl_dir = os.path.join(p1.p1_contract_dir, g.p3_lbl_sel)
        # g.write_in_mem_n_on_disk()
        if g.p2_load_labels_info_d():
            already_selected_l = g.p3_label_info_d['selected_indicators']

        if default and not already_selected_l:
            already_selected_l = ["03.Prod_spec", "pack", "total_qty"]

        # process_default_contract selected indicators set
        if not default:
            proc_2_context()
            with open(os.path.join(p1.p1_contract_dir, p1.p1_labels_info_d['p6_extract_specifics'])) as fj:
                p7_specific_indics_d_of_d = json.load(fj)
            options_l = list(next(iter(p7_specific_indics_d_of_d.values())))
            # select from options_l and put in already_selected_l
            while True:
                print(f'~~~ already selected ~~~\n{already_selected_l}\n~~~~~~')
                not_yet_l = []
                for o in options_l:
                    if o not in already_selected_l:
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
                            already_selected_l.append(not_yet_l[s_i])
                            # break
                        else:
                            print('Integer, but not an option, try again')
                    except ValueError:
                        print('That\'s not an integer, try again')

        g.p3_label_info_d['selected_indicators'] = already_selected_l

        with open(g.p3_label_info_f, 'w') as f:
            json.dump(g.p3_label_info_d, f, ensure_ascii=False)

        make_mako()


def make_mako():
    # writing the input file for Mako
    mako_input = ''
    with open(os.path.join('..', 'p4_' + p1.p1_contract_nr + '_indics_from_contract_l.json')) as f:
        p7_indcs_from_contract_l = json.load(f)  # todo: replace by mem pointer if it exists
    if already_selected_l:
        # building the header
        mako_input += 'idx, prod_n'
        for indc in already_selected_l:
            mako_input += ', ' + indc
        mako_input += '\n'
        # building the body
        indc_by_prod = {}
        for prod in g.p5_all_products_to_be_processed_set:
            indc_by_prod[prod] = {}
        for indc_c in p7_indcs_from_contract_l:  # loop over the big one once
            if indc_c['what'] in already_selected_l:  # loop over the smaller more
                indc_by_prod[indc_c['prod_nr']][indc_c['what']] = indc_c['info']
        idx = 0
        for prod in indc_by_prod.keys():
            mako_input += str(idx)
            mako_input += ', ' + prod
            for k in indc_by_prod[prod].keys():
                mako_input += ', ' + str(indc_by_prod[prod][k])
            mako_input += '\n'
            idx += 1

        with open('mako_input.csv', 'w') as f:
            f.write(mako_input)


def create_selected_indicators_set():
    pass


def p7_display_selected_indicators():

    with open(os.path.join(p1.p1_contract_dir, 'p4_' + p1.p1_contract_nr + '_indics_from_contract_l.json')) as f:
        p7_indics_from_contract_l = json.load(f)
    indic_val_d = {}
    for option in options_l:
        temp_d = {}
        for indic in p7_indics_from_contract_l:
            if indic['what'] == option:
                temp_d[indic['prod_nr']] = indic['info']
        indic_val_d[option] = temp_d

    for option in options_l:
        nr_tabs = 1 if len(option) >= 8 else 2
        print(option, nr_tabs * '\t', list(indic_val_d[option].values()))
    print('\nAlready selected: ', already_selected_l, '\n')
    print('Currently in: ', os.path.relpath(os.getcwd(), os.getcwd() + '..'))
    # m.display_context_in_most_cases()


def p2_load_labels_info_d():
    global p3_label_info_f
    global p3_label_info_d

    p3_label_info_f = os.path.join(p3_lbl_dir, 'label-info.json')
    if os.path.isfile(p3_label_info_f):
        with open(p3_label_info_f) as f:
            p3_label_info_d = json.load(f)
            if p3_label_info_d:
                return True
    return False



def init_2():
    p.menu = 'p6_set_up_label_dirs_n_infos'
    p.mod_lev_1_menu = p.menu
    if not p.main_menu:
        p.main_menu = p.menu
    p.menus = {
        p.menu: {
            '1': create,
            '2': read_n_display,
            '3': update,
            '4': delete,
            '7': create_selected_indicators_set,
            '8': p7_display_selected_indicators,
            '9': cd_to_selected_dir,
            'm': p.back_to_main,
            'q': p.normal_exit,
        },
    }
    p.mod_lev_1_menus = p.menus
    if not p.main_menus:
        p.main_menus = p.menus
    p.context_func_d = {**p.context_func_d, **context_func_d}

    # make sure p1 infrastructure is in place
    # if not p1._read():
    #     p1.Controller(p1.View())

    p1.p1_load_p1_labels_info_d()
    os.chdir(p1.p1_contract_dir)


def main():
    """ Driver """
    c = Controller()
    m.run()


if __name__ == '__main__':
    main()
