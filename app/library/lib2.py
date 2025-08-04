# -*- coding: utf-8 -*-
"""
Timer script to predict run time
Created on Fri Oct 14 09:11:08 2022

@author: Joseph Matveyenko
"""

def estimate_time(stos,imp_combos,max_time=200,save=False,path="",auto_run=False):
    
    import warnings
    warnings.filterwarnings("ignore")
    
    import time
    import calendar
    import math
    from itertools import permutations
    import statistics as st
    from time import sleep
    from library.lib1 import check_natl, natl_weights
    import os
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression

    
    # defining function used later in script
    def flatten(l):
        return [item for sublist in l for item in sublist]
    
    p_div = max_time/10
    
    #Weights do not matter
    age_weight = 0.15
    gender_weight = 0.5
    exp_weight = 0.35
    dupl_n_weight = 0.2
    
    sample_sizes = [10, 12, 14, 16]
    # subset of STO dataset for inexperienced STOs
    inex_stos = stos[(stos['Missions']==0) & (stos['Non_ODIHR_EOMs']==0)]
    inex_stos = inex_stos.sort_values(by=['Age'])
    
    # list of assigned STO ids from 'stos' dataframe
    sto_ids = list(stos["id"])
    natl_w = natl_weights(stos,log=True,scale=3)
    
    # checking if no. of STOs is odd or even
    if (len(sto_ids) % 2) != 0:
        # selecting third STO team member if odd number of STOs
        third = inex_stos.iloc[0] # third STO is youngest w/o any experience
        third_id = str(third[0])
        sto_ids.remove(third_id) # removing third STO from list of STO ids
        ids_even = sto_ids
    else: ids_even = sto_ids # if even no. of STOs, no changes
    
    #sorting stos dataframe by experience score
    stos_by_name = stos.sort_values(by=["Name"],ascending=True)

    total_time0 = time.time()
    
    # setting group size for matching
    group_sizes = []
    poss_n = []
    times = []

    counter=0
    print("-------- estimating run time --------\n")
    if not auto_run: sleep(1)
    print("total time to run estimation: "+ str(max_time)+" seconds")
    
    
    for sample_size in sample_sizes:

        
        permut_size = int(sample_size/2)
        
        
        # creating groups
        sto_ids_mod = []
        stos_by_exp = stos_by_name.sort_values(by=["Experience Score"],ascending=True)
        sto_ids_by_exp = list(stos_by_exp["id"])
        
        # excluding third STO
        for i in sto_ids_by_exp:
            if i not in ids_even:
                sto_ids_by_exp.remove(i)
        
        # breaking stos into groups based on experience
        n_groups = math.ceil(len(sto_ids_by_exp) / permut_size) # number of groups
        if n_groups % 2 != 0: n_groups = int(n_groups + 1)
        n_groups_div2 = int(n_groups/2)
        
        sto_ids_mod = sto_ids_by_exp
        used_ids = []
        groups = []
        for i in range(0,n_groups_div2):
            # This section is for the last two remaining groups, which are smaller
            # and reserved for the observers in the middle based on experience
            if len(sto_ids_mod)<(permut_size*4) and len(sto_ids_mod)>0:
                last_amt = (len(sto_ids_mod))
                last_amt_ceil = math.ceil(last_amt/4)
                last_amt_floor = math.floor(last_amt/4)
                
                lows = sto_ids_mod[0:last_amt_ceil]
                highs = sto_ids_mod[-last_amt_ceil:]
                used_ids.append(lows)
                used_ids.append(highs)
                d = {'Low': lows, 'High': highs}
                groups.append(pd.DataFrame(d))
                for j, k in zip(lows, highs):
                    if j in sto_ids_mod: 
                        sto_ids_mod.remove(j)
                    if k in sto_ids_mod:
                        sto_ids_mod.remove(k)
                lows = sto_ids_mod[0:last_amt_floor]
                highs = sto_ids_mod[-last_amt_floor:]
                d = {'Low': lows, 'High': highs}
                groups.append(pd.DataFrame(d))
           
            # This section is for regular sized groups
            elif len(sto_ids_mod)>0:
                lows = sto_ids_mod[0:permut_size]
                highs = sto_ids_mod[-permut_size:]
                d = {'Low': lows, 'High': highs}
                groups.append(pd.DataFrame(d))
            else:
                break
            used_ids.append(lows)
            used_ids.append(highs)
            used_ids = flatten(used_ids)    
            for j in used_ids:
                 if j in sto_ids_mod: 
                     sto_ids_mod.remove(j)
        

        optimals = []
        for gr, gr_no in zip(groups,range(0,len(groups))):
            total_time1 = time.time()
            total_time = total_time1-total_time0
            
          
            for t,t2 in zip(range(0,int(max_time/p_div)),
                            range(1,int((max_time/p_div)+1))):
                if total_time >= t*p_div and total_time <= t2*p_div:
                    #print(counter)
                    if t > counter +3:
                        print('||',end='')
                    if t > counter +2:
                        print('||',end='')
                    if t > counter+1:
                        print('||'+
                              str(round(((t-1)*p_div)/max_time*100))+"%",end='')
                    if t > counter:
                        print('||'
                              +str(round((t*p_div)/max_time*100))+"%",end='')
                        counter = t
            if total_time>max_time:
                break

            if len(optimals)>0: 
                opt_natl_combos = check_natl(stos,optimals)
                opt_uniq_combos = list(set(list(opt_natl_combos)))
                opt_combo_scores = []
                for opt_c in opt_natl_combos:
                    opt_score = natl_w[(natl_w['n']==opt_c)]
                    opt_score = opt_score.iloc[0]
                    opt_score = opt_score[1]
                    opt_combo_scores.append(opt_score)
            else: opt_natl_combos = []; opt_combo_scores = [];opt_uniq_combos = []
            
            tot_natl_combos = []
            tot_natl_combos.append(opt_natl_combos)
            
            tot_natl_scores = []
            tot_natl_scores.append(opt_combo_scores)

            
            perms = permutations(gr['Low'])
            combos = []
            t0=time.time()
            for perm in perms:
                cs = []
                for i,j in zip(perm,gr['High']):
                    cs.append(str(i+"_"+j))      
                
                combos.append(cs)
        
            imp_options = []
            for i in combos:
                in_list=0
                for j in imp_combos:
                    if j in i:
                        in_list=1
                if in_list==1:
                    imp_options.append(i)
        
            if(imp_options ==combos):break
            poss_combos = [x for x in combos if x not in imp_options]
            poss_n.append(len(poss_combos))
            compats = []
            poss_combos_df = []
            for i in poss_combos:
                pair_compats = []
                sto1_ids = []
                sto2_ids = []
                natl_combos = []
                natl_combo_scores = []
                for j in i:
                    sto_pairs=j.split("_")
                    sto1_row= (stos[(stos["id"]==sto_pairs[0])])
                    sto2_row= (stos[(stos["id"]==sto_pairs[1])])
                    sto1_row= sto1_row.iloc[0]
                    sto2_row= sto2_row.iloc[0]
                    sto1_vals = [sto1_row[k] for k in [3,4,7,2]]
                    sto2_vals = [sto2_row[k] for k in [3,4,7,2]]
                    
                    g_score = 0
                    e_score = 0
                    a_score = 0
                    
                    if sto1_vals[1]==sto2_vals[1]: g_score = 0
                    else: g_score = 1
                    
                    if sto1_vals[2]<2 and sto2_vals[2]<2: e_score = 0
                    else: e_score = 1
                    
                    age_diff = abs(sto1_vals[0] - sto2_vals[0])
                    if age_diff == 0: age_diff = 1
                    a_score = 1/math.sqrt(math.sqrt(age_diff))
                    
                    natl_combo = sorted([sto1_vals[3],sto2_vals[3]])
                    natl_combo = ''.join(natl_combo)
                    natl_combo_score = natl_w[(natl_w['n']==natl_combo)]
                    natl_combo_score = natl_combo_score.iloc[0]
                    natl_combo_score = natl_combo_score[1]
                    natl_combo_scores.append(natl_combo_score)
                    natl_combos.append(natl_combo)
                    
                    compat_score = (gender_weight*g_score + 
                                    exp_weight*e_score + age_weight*a_score)
                    pair_compats.append(compat_score)
                    sto1_ids.append(sto_pairs[0])
                    sto2_ids.append(sto_pairs[1])
                
                tot_natl_combos.extend(natl_combos)
                tot_natl_scores.extend(natl_combo_scores)
                
                dupl = 0
                for n_c,n_j in zip(natl_combos,natl_combo_scores):
                    ab_natl_combos = natl_combos
                    ab_natl_combos.remove(n_c)
                    if n_c in ab_natl_combos or n_c in opt_uniq_combos:
                        dupl = dupl + (tot_natl_combos.count(n_c)/n_j)
                
                
                dupl_score = (dupl/len(natl_combos))
                
                compat = st.mean(pair_compats) - (dupl_n_weight*dupl_score)
                if len(compats)==0 or compat>max(compats):
                    compats.append( compat )
                    d = {'sto1': sto1_ids, 'sto2': sto2_ids,'c':pair_compats}
                    poss_combos_df.append(pd.DataFrame(d))
                
            t1=time.time()
            diff=t1-t0
            times.append(diff)

            group_sizes.append(len(gr))
            
            optimal = poss_combos_df[compats.index(max(compats))]
            optimals.append(optimal)
 
    group_size_fac = [math.factorial(x) for x in group_sizes]
    poss_div_theo = [p/f for p,f in zip(poss_n,group_size_fac)]

    
    d = {"group_size": group_sizes, 
         "theoretical_combos": group_size_fac,
         "possible_combos": poss_n,
         "obs_theor_ratio": poss_div_theo,
         "elapsed_time": times}
    df = pd.DataFrame(data=d)
    
    x = np.array( list(df['possible_combos']) ).reshape((-1,1))
    y = np.array( list(df['elapsed_time']) )
    model = LinearRegression(fit_intercept=False).fit(x,y)
    
    poss_div_theo_sum = sum(df['possible_combos'])/sum(df['theoretical_combos'])
    poss_div_theo_avg = st.mean(poss_div_theo)
    poss_div_theo = [poss_div_theo_sum,poss_div_theo_avg]
    
    x2 = np.array( list(df['group_size'])).reshape((-1,1))
    y2 = np.array( list(df['obs_theor_ratio']) )
    model_poss = LinearRegression().fit(x2,y2)
    coefs = [0,model.coef_,model.score(x,y)]
    coefs2 = [model_poss.intercept_,model_poss.coef_,model_poss.score(x,y)]
    print("||100%")  
    if not auto_run: sleep(1)
    print("\n----- done estimating run time -----\n")      
    if not auto_run: sleep(0.5)       

    if save:
        ts = str(calendar.timegm(time.gmtime()))
        if os.path.isdir(path+"\\exports"):
            if not auto_run: sleep(0.001) 
        else: 
            os.mkdir(path+"\\exports")
        file_name = "\\exports\\time_est"
        full_file_name=path+file_name+"_"+ts+".csv"
        df.to_csv(full_file_name,index=False)                              
    return [df,coefs,coefs2]