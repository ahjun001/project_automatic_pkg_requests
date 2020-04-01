#!/usr/bin/env python3
""" 
 """
import os
import subprocess

def ex_():
    os.system("./render_barcode.py --output='./drawing_o.svg' -l='20' -t='Ean13' -d='312345678901' drawing.svg")

def ex_3():
    command = [
        './render_barcode.py',
        '--output="./drawing_o.svg"',
        '-l="30"',
        '-t="Ean13"',
        '-d="312345678901"',
        'drawing.svg']
    subprocess.call(command)


def ex_2():
    subprocess.call(
        [
            './render_barcode.py',
            '--output="./drawing_o.svg"',
            '-l="30"',
            '-t="Ean13"',
            '-d="312345678901"',
            'drawing.svg'])


def ex_1():
    """ Driver """
    p = subprocess.Popen([
        './render_barcode.py',
        '--output="./drawing_o.svg"',
        '-l="20"',
        '-t="Ean13"',
        '-d="312345678901"',
        'drawing.svg'], stdout = subprocess.PIPE, shell = True)
    print(p.communicate())
    # subprocess.Popen([
    #     'ls',
    #     'drawing_o.svg'
    # subprocess.Popen([
    #     'inkscape',
    #     'drawing_o.svg'
    # ])


def main():
    ex_()


if __name__ == '__main__':
    main()
