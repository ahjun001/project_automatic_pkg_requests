#!/usr/bin/env python3
import os
import pathlib
import shutil
import sys
from datetime import datetime

import m_menus as m
import p1_select_contract as p1
import p2_select_templates as p2
import p3_select_specific_fields as p3


# noinspection NonAsciiCharacters,PyPep8Naming
def create_pdf_with_selected_or_default_values_运行完整演示():
    p1.process_selected_contract()
    p2.load_or_create_templates()
    p3.produce_all_previous_production_options_n_print()


def test_environment():
    print("Test environment: start")
    m.clear()
    print("Test environment: cleared")
    print("os.name = ", os.name)
    print("sys.platform = ", sys.platform)
    print("TERM = ", os.environ["TERM"])
    print("Test environment: end")


def main_menu_context_func():
    c_nr = p1.p1_d["cntrct_nr"] if "cntrct_nr" in p1.p1_d.keys() else ""
    print(f"Step 1 select a contract: " + f'{c_nr if c_nr else "None"}')
    templ_l = p2.p2_load_templates_info_l()
    print(f"Step 2 load or create templates to print: {templ_l}")
    print("Step 3 select fields to print in each template")
    print(60 * "-", "\n\n")
    print(">>> Main menu:")


context_func_d = {
    "root_menu": main_menu_context_func,
    "debug": main_menu_context_func,
}


def save_selected_contract():
    to_main_dir = os.path.join(
        os.path.join(m.root_abs_dir, "contract_samples"), p1.p1_d["cntrct_nr"]
    )

    # copy_dir = to_main_dir + '_' + str(datetime.timestamp(datetime.now()))
    copy_dir = to_main_dir + "_" + str(datetime.timestamp(datetime.now()))
    shutil.copytree(to_main_dir, copy_dir)

    shutil.copy(
        os.path.join(p1.p1_cntrct_abs_dir, p1.p1_d["cntrct_nr"] + "_doc_setup.json"),
        to_main_dir,
    )

    drs = p2.p2_load_templates_info_l()
    if drs:
        for dr in drs:
            from_abs_dr = os.path.join(p1.p1_cntrct_abs_dir, dr)
            to_abs_dr = os.path.join(to_main_dir, dr)
            if not os.path.exists(to_abs_dr):
                os.mkdir(to_abs_dr)
            filename = os.path.join(from_abs_dr, "template-info.json")
            if os.path.exists(filename):
                shutil.copy(filename, to_abs_dr)
            filename = os.path.join(from_abs_dr, "label_template.svg")
            shutil.copy(filename, to_abs_dr)
            _, sub_dirs, _ = next(os.walk(from_abs_dr))
            for sub_dir in sub_dirs:
                from_dir = os.path.join(from_abs_dr, sub_dir)
                to_dir = os.path.join(to_abs_dr, sub_dir)
                shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)


tests_l = [
    "A000001-start",
    "A000001-final",
    "A006043-001",
    "A006045-001",
    "A011001-022",
    "A911008-008",
]


# def merge_all_p1a_xxx_final_contract_json_files_in_one():
#     with open(os.path.join('data', '.p1a_all-final-contract.txt'), 'w') as fw:
#         prod_nr = 0
#         for contract_nr in tests_l:
#             rel_path_contract_json_f = os.path.join(
#                 os.path.join(
#                     'data', contract_nr), '.p1a_' + contract_nr + '-contract.json')
#             if os.path.exists(rel_path_contract_json_f):
#                 with open(rel_path_contract_json_f) as fr:
#                     tmp_struct = json.load(fr)
#                     fr.seek(0)
#                     prod_nr += len(tmp_struct['l_i'])
#                     fw.write(fr.read())
#                     fw.write('\n')
#         fw.write(f'Total: {prod_nr} products')


def run_full_demo_for_a_selection_of_contracts(save=False):
    for test_contract_nr in tests_l:
        step_1__select_a_contract_选择合同号(test_contract_nr=test_contract_nr)
        create_pdf_with_selected_or_default_values_运行完整演示()
        if save:
            save_selected_contract()  # use when a new field has been added to template-info.json
    # merge_all_p1a_xxx_final_contract_json_files_in_one()


def run_full_demo_and_save_a_selection_of_contracts():
    run_full_demo_for_a_selection_of_contracts(save=True)


# noinspection NonAsciiCharacters,PyPep8Naming
def step_1__select_a_contract_选择合同号(test_contract_nr=""):
    # p1.reset_globals()
    p3.reset_globals()
    p1.step_1__select_a_contract_选择合同号(test_contract_nr)


def init():
    m.clear()
    # assign a program
    p1.program_info_d_load_o_create()
    # menus
    m.menu = "root_menu"
    # m.mod_lev_1_menu = m.menu
    if not m.main_menu:
        m.main_menu = m.menu
    m.menus = {
        m.menu: {
            "00": run_full_demo_for_a_selection_of_contracts,
            "0": create_pdf_with_selected_or_default_values_运行完整演示,
            "1": step_1__select_a_contract_选择合同号,
            "2": p2.step_2__select_templates_to_print_选择_编辑标签类型,
            "3": p3.step_3__select_fields_to_print_for_each_template_选择每种标签类型的资料,
            "4": save_selected_contract,
            "5": p1.process_selected_contract,
            "s": run_full_demo_and_save_a_selection_of_contracts,
            "q": m.normal_exit_正常出口,
            "d": m.debug,
        },
        "debug": {
            "t": test_environment,
            "b": m.back_后退,
            "q": m.normal_exit_正常出口,
        },
    }
    # m.mod_lev_1_menus = m.menus
    if not m.main_menus:
        m.main_menus = m.menus

    if __name__ == "__main__":
        m.mod_lev_1_menu = m.menu
        m.mod_lev_1_menus = m.menus
    m.context_func_d = {**m.context_func_d, **context_func_d}

    # If the data directory does not exist, process_selected_contract it
    data_adir = os.path.join(m.root_abs_dir, "data")
    if not pathlib.Path(data_adir).exists():
        os.mkdir(data_adir, mode=0o700)


def main():
    """ Driver """
    init()
    m.run()


if __name__ == "__main__":
    main()
