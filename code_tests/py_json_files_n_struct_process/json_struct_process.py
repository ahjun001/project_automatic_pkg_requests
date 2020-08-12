#!/usr/bin/env python3
import json
import os

###################################################################################################
# Structure for process output
overall_process_d = {
    'a': '',
    'b': '',
    'c': '',
    'd': '',
    'e': '',
    'f': '',
}


# This process is good to build a json struct and store it in a .json file so that we don't have to build it again
# We need a process to build directories and copy files
# We need a process that turns files into other files (svg into pdf) and (multi-pdf into unique-pdf)
# todo: remove print statements, maybe replace with assert
# todo: putting 2 processes together, put a e1, e2, e3
# todo: two kinds of processes: json to json, non-json in memory

class JsonStructProcess:  # not good for process in parallel
    def __init__(self, name, output_filename, inputs, process_in_memory, read, del_func):
        self.name = name
        self.output_filename = output_filename
        self.inputs = inputs
        self.process_in_memory = process_in_memory
        self.read = read
        self.del_func = del_func

    def load_or_create(self, force_create = False):
        print(f'load_or_create_{self.name}: start, m.result_d = {overall_process_d.values()}')
        # processing
        if overall_process_d[self.name] and not force_create:
            print(f'{self.name} already in memory and file exists: no action needed')
        else:
            # if on disk: load
            if os.path.exists(self.output_filename) and not force_create:
                with open(self.output_filename, encoding = 'utf8') as fp:
                    print(f'loading {self.output_filename} from disk')
                    overall_process_d[self.name] = json.load(fp)  # why load json.load

            # if not on disk or force_create is True: build
            else:
                # gathering input
                for k, v in self.inputs.items():
                    print(f'{self.name} calls for {k}')
                    v()

                # performing process
                print(f'Taking a long time creating {self.name}')
                for i in range(10):
                    print(f'i = {i}', end=', ')
                    self.process_in_memory(force_create = (i == 0))
                print()
                with open(f'{self.name}.json', 'w', encoding = 'utf8') as fp:
                    print(f'saving {self.name}.json to disk')
                    json.dump(overall_process_d[self.name], fp, ensure_ascii = False)

        print(f'load_or_create_{self.name}: end, m.result_d = {overall_process_d.values()}')

    def push(self):
        self.load_or_create(force_create = True)

    def delete(self):
        print(f'delete_{self.name}: start, m.result_d = {overall_process_d.values()}')
        if self.del_func():
            print(f'deleted {self.name}.json')
        else:
            print(f'cannot delete {self.name}.json, no such file in directory')
        print(f'delete_{self.name}: end, m.result_d = {overall_process_d.values()}')
