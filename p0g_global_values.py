#!/usr/bin/env python3
# p0g_global_values.py
"""
    Global variables
     """
import json
import os

import pathlib
import re

"""
    Setting variables to be updated
    """
program_info_d = {}  # directory containing information on last run and progress in building the label set
filename_source_xls = None  # full path of source xls file
contract_nr = None  # prefix of the contract xls source file
contract_dir = None  # directory where a copy of the xls contract file and contract extracted data is
filename_xls = None  # relative path of contract xls filename in cntrct_nr directory
filename = None  # filename that include chinese char description, without extension
contract_dir_xls = None  # full path of the copy of the xls file located in the contract_dir directory

lbl_dir = None  # currently working label directory
lbl_lst = None  # list of labels
lbl_sel = None  # current label

process = None
menu = None
menus = None
entry_level_menu = None
entry_level_menus = None

header_height = 7

page_view_box_w = 170
page_view_box_h = 257

"""
    View functions to check_one_n_only_one_file_exists(ext)
    """


def viewDirDoesNotExist():
    print(f"\nCan't select {contract_nr}: no such file or directory\n")


def viewTooManyExtFileInDirectory(xls_file_l, ext):
    print(f"\n{len(xls_file_l)} {ext} files are present, that's too many, exiting\n")


def viewFilenamePrefixInconsistentWithDirectory(cntrct_nr, prfx):
    print(f'\nIncorrect! The file in {cntrct_nr} starts with {prfx}\n')


def viewFileNotInDirectory():
    print(f'\nThe xls file corresponding to {contract_nr} contract is not present, exiting\n')


"""
    General util functions
    """


def check_a_unique_contract_ext_file_w_o_wo_prefix_exists_in_dir(g_dir, ext, check_prefix = True):
    # if the cntrct_nr directory os.path.exists
    p = pathlib.Path(g_dir)
    if p.exists():
        # make the sublist of the files that have an '.xls' extension
        ext_file_l = [fl.name for fl in p.glob('*' + ext)]
        if len(ext_file_l) == 1:
            if check_prefix:
                # check that this file name begin with cntrct_nr
                s = re.match(r'\w+-\d+', ext_file_l[0])
                if s:
                    prfx = s.group()
                    if prfx == contract_nr:
                        return prfx, ext_file_l[0]
                    else:
                        viewFilenamePrefixInconsistentWithDirectory(contract_nr, prfx)
                        return False
                else:
                    return False
            else:
                return True
        # but also there maybe no ext file in the cntrct_nr directory
        elif len(ext_file_l) == 0:
            viewFileNotInDirectory()
            return False
        # or there maybe more than one, which would not be the canonical situation
        else:
            viewTooManyExtFileInDirectory(ext_file_l, ext)
            return False
    # if the cntrct_nr directory does not exist, return False
    else:
        viewDirDoesNotExist()
        return False


"""
    Making sure minimum infrastructure is in place on first run
    """
root_dir = os.path.dirname(os.path.abspath(__file__))  # directory where the program is located
program_info_f = os.path.join(root_dir, 'program-info.json')
if pathlib.Path(program_info_f).exists():
    with open(program_info_f) as f:
        program_info_d = json.load(f)
else:
    prefix, result = check_a_unique_contract_ext_file_w_o_wo_prefix_exists_in_dir(root_dir, '.xls')
    program_info_d = {'contract_root': prefix}
    with open(program_info_f, 'w') as f:
        json.dump(program_info_d, f, ensure_ascii = False)
