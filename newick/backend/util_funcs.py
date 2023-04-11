"""
This file defines some helper functions that may be used
by several other modules. 
"""


def format_float(num:float) -> str:
    return format(num, 'f').rstrip('0').rstrip('.')

def format_int(num:int) -> str:
    return format(num, 'd')