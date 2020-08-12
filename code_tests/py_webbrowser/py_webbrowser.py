#!/usr/bin/env python3
import subprocess
import sys
import webbrowser
import os

url0 = os.path.abspath('page_0.svg')
url1 = os.path.abspath('page_1.svg')

google_chrome_path = r'/usr/bin/google-chrome' if os.name == 'posix' else r'C:\Program Files (' \
                                                                          r'x86)\Google\Chrome\application\chrome.exe '
firefox_path = r'/usr/bin/firefox' if os.name == 'posix' else r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
inkscape_path = r'/usr/bin/inkscape' if os.name == 'posix' else r'C:\Program Files\Inkscape\bin\inkscape.exe'


def ex_6():
    ex_4()
    ex_5()


def ex_5():
    if os.name != 'posix':
        webbrowser.register('google-chrome', None, webbrowser.BackgroundBrowser(google_chrome_path))
    webbrowser.get('google-chrome').open_new_tab(url0)
    webbrowser.get('google-chrome').open_new_tab(url1)


def ex_4():
    if os.name != 'posix':
        webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))
    webbrowser.get('firefox').open_new_tab(url0)
    webbrowser.get('firefox').open_new_tab(url1)
    subprocess.Popen(['inkscape.exe', url1], executable=inkscape_path)


def ex_3c():
    subprocess.Popen(['google-chrome.exe', url0], executable=google_chrome_path)
    subprocess.Popen(['google-chrome.exe', url1], executable=google_chrome_path)


def ex_3f():
    subprocess.Popen(['firefox.exe', url0], executable=firefox_path)
    subprocess.Popen(['firefox.exe', url1], executable=firefox_path)


def ex_2():
    webbrowser.open_new_tab(url0)
    webbrowser.open_new_tab(url1)


def ex_1():
    webbrowser.open(url0)  # windows open default svg program -> inkscape
    webbrowser.open_new_tab(url1)


def normal_exit():
    print('~~~ Regular progam exit ~~~')
    sys.exit(0)


def clear():
    os.system('clear')
    # subprocess.call('clear')


def main():
    menu = {
        '1': ex_1,
        '2': ex_2,
        '3f': ex_3f,
        '3c': ex_3c,
        '4': ex_4,
        '5': ex_5,
        'c': clear,
        'q': normal_exit
    }
    while True:
        for k, v in menu.items():
            print(f'{k}. {v.__name__}')
        selection = input("\nEnter selection: ")
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f'Option {selection} selected')
        selection_func_name = menu.get(selection)
        if selection_func_name:
            selection_func_name()
        else:
            print(f'|\n| {selection} is not a valid selection\n|')


if __name__ == '__main__':
    main()
