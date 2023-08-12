# -*- coding: utf-8 -*-

from ctypes import *

lib = cdll.LoadLibrary("./table_to_new.so")

c_string = c_char_p

table_to_new_wrapper = lib.table_to_new_wrapper
table_to_new_wrapper.argtypes = [c_string]
table_to_new_wrapper.restype = POINTER(POINTER(c_string))

free_table = lib.free_table
free_table.argtypes = [POINTER(POINTER(c_string))]
free_table.restype = None


def c_string_array_to_list(c_array):
    result = []
    i = 0
    while c_array[i]:
        sublist = []
        j = 0
        while c_array[i][j]:
            sublist.append(c_array[i][j].decode())
            j += 1
        result.append(sublist)
        i += 1
    return result


def table_to_new(table):
    table_c = c_string(table.encode())
    table_c_array = table_to_new_wrapper(table_c)
    table_list = c_string_array_to_list(table_c_array)
    return table_list
