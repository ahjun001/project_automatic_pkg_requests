#!/usr/bin/env python3
import subprocess
import os
import sys

if os.name == 'posix':
    pdfunite_path = '/usr/bin/pdfunite'
    qpdf_path = r'/usr/bin/qpdf'
    foxit_path = r'/usr/bin/FoxitReader'
    xreader_path = r'/usr/bin/xreader'
elif os.name == 'nt':
    qpdf_path = r'C:\Program Files no reg\qpdf-10.0.1\bin\qpdf.exe'
    foxit_path = r'C:\Program Files (x86)\Foxit Software\Foxit Reader\FoxitReader.exe'
else:
    print('|\n| Unsupported OS\n|')
    sys.exit()

files_in = [os.path.abspath(os.path.join(os.path.join('data', 'A001'), f'.page_{i}.pdf')) for i in range(3)]
file_out = os.path.abspath(os.path.join(os.path.join('data', 'A001'), 'final.pdf'))


def ex_():
    subprocess.Popen(
        ['qpdf', '--empty', '--pages', *files_in, '--', file_out],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        executable=qpdf_path
    )
    subprocess.Popen(['FoxitReader', file_out], executable=foxit_path, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL).wait()
    # with open(os.devnull, 'wb') as DEVNULL:
    #     subprocess.Popen(['FoxitReader', file_out], executable=foxit_path, stderr=DEVNULL, stdout=None).wait()
    # subprocess.Popen(['xreader', file_out], executable=xreader_path).wait()


def ex_1():
    if os.name == 'posix':
        subprocess.Popen(['pdfunite', *files_in, file_out], executable=pdfunite_path)
    elif os.name == 'nt':
        subprocess.Popen(['qpdf', '--empty', '--pages', *files_in, '--', file_out], executable=qpdf_path)
        subprocess.Popen(['FoxitReader', file_out], executable=foxit_path)
    else:
        print('|\n| Unsupported OS\n|')


def main():
    ex_()


if __name__ == '__main__':
    main()
