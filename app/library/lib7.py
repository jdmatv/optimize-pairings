# -*- coding: utf-8 -*-
"""
Checks if necessary modules are installed
Created on Mon Oct 31 13:24:27 2022

@author: Joseph Matveyenko
"""

def pre_import(module, print_mode=0):

    import sys
    import os
    
    orig_dir = os.getcwd()
    
    def list_full_paths(directory):
        return [os.path.join(directory, file) for file in os.listdir(directory)]
    
    if module == "hf":
        try:
            import humanfriendly   
        except ModuleNotFoundError:
            sys.exit("humanfriendly not installed.")
        else:
            if print_mode == 1: print("humanfriendly is installed.")
            
    elif module == "np":
        try:
            import numpy
        except ModuleNotFoundError:
            sys.exit("numpy not installed.")
        else:
            if print_mode == 1: print("numpy is installed.")
            
    elif module == "op":
        try:
            import openpyxl
        except ModuleNotFoundError:
            sys.exit("openpyxl not installed.")
        else:
            if print_mode == 1: print("openpyxl is installed.")
            
    elif module == "sk":
        try:
            import sklearn
        except ModuleNotFoundError:
            sys.exit("sklearn not installed.")
        else:
            if print_mode == 1: print("sklearn is installed.")
    
    elif module == "pd":
        try:
            import pandas
        except ModuleNotFoundError:
            sys.exit("pandas not installed.")
        else:
            if print_mode == 1: print("pandas is installed.")
            
    else: sys.exit(module+" does not exist")

