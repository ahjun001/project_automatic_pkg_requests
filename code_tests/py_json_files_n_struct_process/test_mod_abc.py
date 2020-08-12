#!/usr/bin/env python3
""" 
 """
import os

import json_struct_process as p
import mod_abc as abc
import menus_n_loop as m

a = p.JsonStructProcess('a', 'a.json', abc.a_inputs, abc.a_process_in_memory, abc.a_read, abc.a_delete)


def test_a_read():
    a.load_or_create()
    assert a.read()
    m.overall_proccess_d['a'] = ''
    assert not a.read()
    a.load_or_create()
    m.overall_proccess_d['a'] = '_'
    assert not a.read()

def test_delete_a():
    a.load_or_create()
    a.del_func()
    assert not os.path.exists('d.json')


def test_load_or_create_a():
    if a.read():
        a.del_func()
    assert not a.read()
    a.load_or_create()
    assert a.read()
    a.load_or_create()
    assert a.read()


def test_push_a():
    a.load_or_create()
    tmp = m.overall_proccess_d['a']
    a.push()
    r1 = m.overall_proccess_d['a'] == tmp.swapcase()
    a.push()
    r2 = m.overall_proccess_d['a'] == tmp.swapcase()
    a.push()
    r3 = m.overall_proccess_d['a'] == tmp.swapcase()
    a.push()
    r4 = m.overall_proccess_d['a'] == tmp.swapcase()
    a.push()
    r5 = m.overall_proccess_d['a'] == tmp.swapcase()
    assert r1 or r2 or r3 or r4 or r5
