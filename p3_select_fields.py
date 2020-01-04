#!/usr/bin/env python3
import json
import os

import u_global_values as g
import u_menus as m


class Controller:
    def __init__(self):  # use to be (self, p6_specific_indics_d_of_d)
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
        if g.chdir_n_p7_read():
            self.already_selected_l = g.p7_label_info_d['selected_indicators']
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

            func.__name__ = indic  # as function is not read before being called for execution
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
        g.p7_label_info_d['selected_indicators'] = self.already_selected_l

        with open(g.p7_label_info_f, 'w') as f:
            json.dump(g.p7_label_info_d, f, ensure_ascii = False)
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

            with open(g.p6_lbl_sel + '_mako_input.csv', 'w') as f:
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


def main():
    """ Driver """
    c = Controller()
    m.run(c.p7_display_selected_indicators())


if __name__ == '__main__':
    main()
