# -*- coding: utf-8 -*-
"""
Running lib3 multiple times and UX/communication
Created on Fri Oct 21 12:49:34 2022

@author: Joseph Matveyenko
"""

def sto_deployer(file, regroup, est_time, sample_size, no_regs, reg_sizes,
                regional_deployment, priority=3, level_3_weight=0.5, 
                level_2_weight=0.2, level_1_weight=0.01, age_weight=0.15,
                gender_weight=0.5, exp_weight=0.35, dupl_n_weight=0.2,
                sto_days_limit=10, lto_days_limit=60, ct_days_limit=70, 
                sto_days_min=7, lto_days_min=50, ct_days_min=60,
                sto_w=5, lto_w=1, ct_w=1, hq_w=0.05, middle_name=False,
                first_prop = 0.4,auto_run=True):

    from library.lib7 import pre_import
    import sys
    from library.lib3 import sto_pair_df
    from library.lib6 import distribute_natls, nice_naming
    from time import sleep
    import os
    import re
    import math
    import pandas as pd
 
    def flatten(l): return [item for sublist in l for item in sublist]
    
    def get_valid_filename(s):
        s = str(s).strip().replace(' ', '_')
        return re.sub(r'(?u)[^-\w.]', '', s)

    
    times_vec = ["0","0.5","3","15","80"]
    dupl_vals = [0.01, 0.05, 0.1]
    pms = [1,0,0]

    reps = (sample_size - 8)/2
    if reps % 1 != 0:
        sys.exit("Error: Sample size is not even.")
    if sample_size <10:
        sys.exit("Error: Sample size is less than or equal to 10.")
    
    print("\n\n          ---- PART 1/2 ----\n\nPlease wait for initial testing - can take up to "+
          times_vec[int(reps)-1]+" minutes or longer depending on # of STOs \n")
    if not auto_run: sleep(0.9)
    
    options = []    
    for i in range(0,int(reps)):
        new_ss = int(10+i*2)
        
        
        #print(new_ss)
        #print(sample_size)
        if new_ss < sample_size:
            print("1."+str(i+1)+" / 1." +str(int(reps)-1))
            for tr in range(3):
                print(str(tr+1)+"/3")
                low_opt = sto_pair_df(file, new_ss, regroup,
                                        est_time, level_3_weight, 
                                        level_2_weight, level_1_weight, age_weight,
                                        gender_weight, exp_weight, dupl_vals[tr],
                                        sto_days_limit, lto_days_limit, ct_days_limit, 
                                        sto_days_min, lto_days_min, ct_days_min,
                                        sto_w, lto_w, ct_w, hq_w, middle_name,
                                        first_prop, auto_run,print_mode=0)
                options.append(low_opt)
        if new_ss == sample_size:
            print("\n\n          ---- PART 2/2 ----\n")
            for tr2 in range(3):
                print(str(tr2+1)+"/3")
                reg_opt = sto_pair_df(file, sample_size, regroup,
                                        est_time, level_3_weight, 
                                        level_2_weight, level_1_weight, age_weight,
                                        gender_weight, exp_weight, dupl_vals[tr2],
                                        sto_days_limit, lto_days_limit, ct_days_limit, 
                                        sto_days_min, lto_days_min, ct_days_min,
                                        sto_w, lto_w, ct_w, hq_w, middle_name,
                                        first_prop, auto_run,pms[tr2])
                options.append(reg_opt)
    
    opt_scores = []
    opt_full_scores = []
    for opt in options:
        print(opt[1])
        print("\n")
        opt_full_scores.append([opt[1][0][0],opt[1][0][1],opt[1][0][2],opt[1][1],opt[1][2],opt[1][3]])
        if priority == 1:
            opt_scores.append(opt[1][0][0])
        if priority == 2:
            opt_scores.append(opt[1][1])
        if priority == 3:
            opt_scores.append(opt[1][0][0]+opt[1][1]+opt[1][2]+opt[1][3])
    
    low_score = min(opt_scores)

    for sc, opt,opt_full in zip(opt_scores, options,opt_full_scores):
        if sc == low_score:
            selected_opt = opt
            sc_full = opt_full

    opt_full_scores.remove(sc_full)
    opt_full_scores.insert(0,sc_full)
    opt_full_scores.insert(0,["Same-gender pairs","M-M pairs","F-F pairs","Repeat combinations of nationalities","Pairs without any experience","Pairs with low experience"])

    print(opt_full_scores)

    sc_col_names = []
    for i in range(len(opt_full_scores)):
        if i==0:
            sc_col_names.append("Indicator")
        elif i==1:
            sc_col_names.append("Selected")
        else:
            sc_col_names.append(str("Alt"+str(i-1)))
    
    sc_df = pd.DataFrame(list(zip(*opt_full_scores)), columns = sc_col_names)

    print("Selectd Opt")
    print(selected_opt[1])

    selected_dat = selected_opt[0]

    if regional_deployment:
        n_regions = no_regs

        region_names = []
        region_sizes = reg_sizes
        for reg in range(n_regions):
            if (reg+1)<10:
                reg_name = str(0)+str(reg+1)
            else:
                reg_name = str(reg+1)
                    
            if (n_regions)<10:
                max_reg_name = str(0)+str(n_regions)
            else:
                max_reg_name = str(n_regions)                
            region_names.append(reg_name)
        
        region_sizes_adj = []
        for rs in region_sizes:
            region_sizes_adj.append(rs*2)
                
        reg_d = {"Region Name":region_names,"STO Teams":region_sizes_adj}
        reg_dat = pd.DataFrame(reg_d)
            
        region_sizes_adj_div2 = [int(x/2) for x in region_sizes_adj]
        reg_dat_print = pd.DataFrame({"Region Name":region_names,
                                    "STO Teams":region_sizes_adj_div2}) 
        print(reg_dat_print.to_string(index=False))
        print("\nNow the STO teams will be randomly distributed across the regions\n")
        selected_dat = distribute_natls(selected_dat = selected_dat,reg_dat = reg_dat)
    else:
        selected_dat = distribute_natls(selected_dat = selected_dat, reg_dat = False) 

    selected_dat = nice_naming(selected_dat)  
    
    print(sc_df)


    return [selected_dat,sc_df]
