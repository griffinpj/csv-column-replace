#!/usr/local/bin/python
import csv
import sys
import asyncio

def prepare_write_filename(f_name):
    return f_name[:-4] + '-modified.csv'

def requires_writing(f_name, func, obj):
    if obj == -1: 
        print('Skipping write for %s' % (f_name))
        return False
    with open(prepare_write_filename(f_name), 'w+') as f:
        return func(csv.writer(f), obj)

def requires_reading(f_name, func):
    with open(f_name) as f:
        return func(csv.reader(f))

async def loop_on_file(f_name, col_name, val):
    def write(w, obj):
        for row in obj:
            w.writerow(row); 

    def read(l):
        times = 0
        col_idx = -1
        new_obj = []
        skip = False
        no_changes = True
        for row in l:
            if times == 0: 
                for i, x in enumerate(row):
                    if x == col_name:
                        new_obj.append(row)
                        col_idx = i
                        break
                if col_idx == -1:
                    # Doesn't have the desired column name
                    skip = True
            else:
                to_add = []
                for i, x in enumerate(row):
                    if i == col_idx and row[col_idx] != val:
                        no_changes = False
                        to_add.append(val)
                    else:
                        to_add.append(x)
                new_obj.append(to_add);
            if skip == True:
                return -1
            times += 1
        if no_changes == True: 
            return -1
        return new_obj

    return requires_writing(f_name, write, requires_reading(f_name, read)) 

async def main():
    sliced_args = sys.argv[1::]
    if sliced_args[0] == '-h' or len(sliced_args) < 3:
        print('Usage: python modify.py [-h] [column] [value] [file ...]')
        return

    column_name = sliced_args[0]
    new_value = sliced_args[1]
    files = sliced_args[2::]

    print('For the given file(s): %s ' % (', '.join(files)))
    print('Searching for column: \'%s\'' % (column_name))
    print('Replace values with: \'%s\'' % (new_value))

    tasks = []
    for f in files:
        tasks.append(asyncio.create_task(
            loop_on_file(f, column_name, new_value)))

    for t in tasks:
        await t
    return

asyncio.run(main())
