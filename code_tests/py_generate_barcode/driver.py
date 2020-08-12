#!/usr/bin/env python3
import render_barcode as rb
import os
import sys


def ex_file():
    output = 'bcode_exec.svg'
    sys.argv = [
        "render_barcode.py",
        "-t=Ean13",
        "-d=303030300001",
        "-l=20",
        f"--output={output}",
        'barcode_template.svg'
    ]
    with open("render_barcode.py") as fp:
        exec(fp.read())
    os.system(f'inkscape {output}')


def ex_func_call():
    # rb.Barcode(text='Ean13', height='20',
    #         barcode='355555666666').run(args = ['--output', 'drawing_o.svg', 'drawing.svg']).run()
    output = 'bcode_ex_func_call.svg'
    rb.Barcode().run(args=[
        "-t=Ean13",
        "-d=303030300001",
        "-l=20",
        f"--output={output}",
        "barcode_template.svg"])
    os.system(f'inkscape {output}')
    os.system(f'rm {output}')


def ex_os_system():
    output = 'bcode_os_system.svg'
    command = f"./render_barcode.py " + \
              f"-t=Ean13 " + \
              f"-d=303030300001 " + \
              f"-l=20 " + \
              f"--output={output} " + \
              f"barcode_template.svg "
    print(command)
    os.system(command)
    os.system(f'inkscape {output}')
    os.system(f'rm {output}')


def main():
    ex_os_system()
    ex_func_call()
    # ex_file()


if __name__ == '__main__':
    main()
