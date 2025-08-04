# -*- coding: utf-8 -*-
"""
Matching observers
Created on Wed Oct 12 10:50:49 2022
 
@author: Joseph Matveyenko
"""

def sto_pair_df(file, sample_size, regroup, est_time, level_3_weight=0.5, 
                level_2_weight=0.2, level_1_weight=0.01, age_weight=0.15,
                gender_weight=0.5, exp_weight=0.35, dupl_n_weight=0.2,
                sto_days_limit=10, lto_days_limit=60, ct_days_limit=70, 
                sto_days_min=7, lto_days_min=50, ct_days_min=60,
                sto_w=5, lto_w=1, ct_w=1, hq_w=0.05, middle_name=False,
                first_prop=0.4, auto_run=False, print_mode=1):

    # Imorting sto_dataset script to create dataset based on STO data
    import library.lib1 as lib1
    import library.lib2 as lib2
    import library.lib5 as lib5
    from itertools import permutations
    import math
    import statistics as st
    from time import sleep
    import sys
    import pandas as pd
    from humanfriendly import format_timespan
    
    # defining function used later in script
    def flatten(l): return [item for sublist in l for item in sublist]
    
    def insert_row(idx, df, df_insert):
        dfA = df.iloc[:idx, ]
        dfB = df.iloc[idx:, ]

        df = dfA.append(df_insert,ignore_index=True).append(dfB).reset_index(drop = True)

        return df
    
    if sample_size % 2 != 0: sample_size = sample_size-1 # sample_size must be even
    
    # Calling create_stos function from sto_dataset.py file
    stos_output = lib5.create_stos(file, level_1_weight, level_2_weight,
                                   level_3_weight, sto_days_limit, lto_days_limit,
                                   ct_days_limit, sto_days_min, lto_days_min, ct_days_min, sto_w, 
                                   lto_w, ct_w, hq_w, first_prop,print_mode)

    if not auto_run: sleep(0.5)
    stos = stos_output[0] # dataset of STO indicators
    imp_combos = stos_output[1] # list of impossible STO combinations
    #raw_STO = stos_output[2] # original STO data
    
    # subset of STO dataset for inexperienced STOs
    inex_stos = stos[(stos['Missions']==0) & (stos['Non_ODIHR_EOMs']==0)]
    inex_stos = inex_stos.sort_values(by=['Age'])
    
    # list of assigned STO ids from 'stos' dataframe
    sto_ids = list(stos["id"]) 
    natl_w = lib1.natl_weights(stos,log=True,scale=3)
    
    # checking if no. of STOs is enough for the sample size
    if sample_size == 20 and len(sto_ids) < 68:
        sys.exit("Error: too few STOs for group size of 20.\nPlease try group size of 18 or 16.")
    if sample_size == 18 and len(sto_ids) < 60:
        sys.exit("Error: too few STOs for group size of 18.\nPlease try group size of 16.")
    if sample_size == 16 and len(sto_ids) < 51:
        sys.exit("Error: too few STOs for group size of 16.\nPlease try group size of 14.")
    if sample_size == 14 and len(sto_ids) < 35:
        sys.exit("Error: too few STOs for group size of 14.\nPlease try group size of 12.")
    if len(sto_ids) < 29:
         sys.exit("Error: too few STOs \nPlease try again with at least 29 STOs.")
    
    if print_mode==1 and not auto_run:
        sleep(0.5)
        print("")
        sleep(0.5)
        
    # checking if no. of STOs is odd or even
    if (len(sto_ids) % 2) != 0:
        if print_mode==1:
            print("Info - Odd number of STOs: "+ str(len(sto_ids))+"\n\n")
            if not auto_run: sleep(0.5)

        # selecting third STO team member if odd number of STOs
        
        gender = stos["Gender"]
        women_n = list(gender).count("W")
        men_n = list(gender).count("M")
        
        if men_n > women_n:
            sel_gender = "M"
            unsel_gender = "F"
        else:
            sel_gender = "F"
            unsel_gender ="M"
        
        inex_by_g = inex_stos[inex_stos.Gender==sel_gender]
        
        third = inex_by_g.iloc[0] # third STO is youngest w/o any experience of gender with most STOs
     
        third_id = str(third[0])
        third_n1 = str(third[2])
        sto_ids.remove(third_id) # removing third STO from list of STO ids
        ids_even = sto_ids
        third_yn = True
    else: 
        ids_even = sto_ids # if even no. of STOs, no changes
        third_yn = False
    

    
    #sorting stos dataframe by experience score
    stos_by_name = stos.sort_values(by=["Name"],ascending=True)
    stos_by_exp = stos_by_name.sort_values(by=["Experience Score"],ascending=True)
    sto_ids_by_exp = list(stos_by_exp["id"])
    
    # excluding third STO
    for i in sto_ids_by_exp:
        if i not in ids_even:
            sto_ids_by_exp.remove(i)
    
    # setting group size for matching
    permut_size = int(sample_size/2)
    
    # breaking stos into groups based on experience
    n_groups = math.ceil(len(sto_ids_by_exp) / permut_size) # number of groups
    if n_groups % 2 != 0: n_groups = int(n_groups + 1)
    n_groups_div2 = int(n_groups/2)
    
    # creating groups
    
    group_sizes = lib1.create_gr_sizes(sample_size,len(sto_ids_by_exp),permut_size,
                                  n_groups,n_groups_div2)
    
    sto_ids_mod = sto_ids_by_exp
    used_ids = []
    groups = []

    for g_s,i in zip(group_sizes,range(len(group_sizes))):
        if len(sto_ids_mod)>0:
            lows = sto_ids_mod[0:int(g_s/2)]
            highs = sto_ids_mod[-int(g_s/2):]
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

    
    #optimizing gender diversity by swapping stos between groups
    #some reorganization with experience
    if regroup:
        if not auto_run: sleep(0.2)
        if not auto_run: print("");sleep(0.2)
        groups = lib1.g_swap_exp(stos = stos, groups = groups,print_mode=print_mode,
                                 space = False)
        
        groups_list = lib1.g_swap(stos, groups, exp_diff=0.15,mode=0, thresh = 3,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=2, thresh = 3,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=0, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=2, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=3, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=0, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=2, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=3, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=0, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=2, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=3, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=0, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=2, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=3, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=0, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=2, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=3, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=0, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=2, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=3, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=0, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=2, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=3, thresh = 0,
                                 print_mode = print_mode)

    if regroup:
        if not auto_run: sleep(0.2)
        if not auto_run: print("");sleep(0.2)
        groups_list = lib1.g_swap_exp(stos = stos, groups = groups_list[0],print_mode=print_mode,
                                 space = False)
        
        groups_list = lib1.g_swap(stos, groups, exp_diff=0.2,mode=0, thresh = 3,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=2, thresh = 3,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=0, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=2, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=3, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=0, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=2, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=3, thresh = 2,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=0, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=2, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=3, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=0, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=2, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=3, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=0, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=2, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.25,mode=3, thresh = 1,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=0, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=2, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.15,mode=3, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=0, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=2, thresh = 0,
                                 print_mode = print_mode)
        groups_list = lib1.g_swap(stos, groups_list[0], exp_diff=0.2,mode=3, thresh = 0,
                                 print_mode = print_mode)

        groups = groups_list[0]

        if not auto_run: sleep(1)
        
        if auto_run:
            print("\n\nAUTORUNNING\n")
        else:
            print("\n\n",end="");sleep(0.3)
            print("Would you like to proceed?")
            sleep(0.3)
            print('\ntype Yes/No and hit ENTER')
            print('\n-> ',end='')
            yn_input = (str(input()))
            yn_input = yn_input.lower()
            yn_input = yn_input.strip()
            if yn_input == "no": sys.exit("User did not wish to proceed")
            elif yn_input =="yes":sleep(0.2);print("-> Ok");sleep(0.2);print("\n")
            else: 
                print("\nFailed to understand user input");sleep(0.4)
                print('Please make sure your entry is either "Yes" or "No" \n')
                print("Would you like to proceed?")
                sleep(0.8)
                print('type Yes/No and hit ENTER')
                print('\n-> ',end='')
                yn_input = (str(input()))
                yn_input = yn_input.lower()
                yn_input = yn_input.strip()
                if yn_input =="yes":sleep(0.2);print("-> Ok");sleep(0.2);print("\n")
                else: sys.exit("User did not wish to proceed or input not understood")
        
    optimals = []
    #elapsed = []
    poss_n = []
    for gr, gr_no in zip(groups,range(0,len(groups))):
        
        if len(optimals)>0: 
            opt_natl_combos = lib1.check_natl(stos,optimals)
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
        
        poss_options_n = len(combos)-len(imp_options)
        
        
        if(imp_options ==combos):break
        poss_combos = [x for x in combos if x not in imp_options]
       
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
            
        poss_n.append(len(combos)-len(imp_options))     
        optimal = poss_combos_df[compats.index(max(compats))]
        optimals.append(optimal)
    
    opt_df = pd.concat(optimals)
    
    c_pc = []
    for i in opt_df['c']:
        c_pc.append(str(str(round(i*100))+"%"))
    
    opt_df['c'] = c_pc
    
    natl_combos=[]
    g_m_same = []
    g_f_same = []
    g_m_same_ids = []
    g_f_same_ids = []
    no_exp = []
    low_exp = []
    # checking duplicate nations, same-gender pairs
    for sto1,sto2 in zip(opt_df['sto1'],opt_df['sto2']):
        sto1_row = stos[(stos['id']==sto1)]
        sto2_row = stos[(stos['id']==sto2)]
        sto1_row = sto1_row.iloc[0]
        sto2_row = sto2_row.iloc[0]
        natl_combo = sorted([sto1_row[2],sto2_row[2]])
        natl_combo = ', '.join(natl_combo)
        natl_combos.append(natl_combo)
        m_combo = (sto1_row[7],sto2_row[7])
        if m_combo[0]==0 and m_combo[1]==0:
            no_exp.append(1)
        else: no_exp.append(0)
        if m_combo[0]+m_combo[1]<4:
            low_exp.append(1)
        else: low_exp.append(0)
        if sto1_row[4] == "M" and sto2_row[4] == "M":
            g_m_same.append(1)
            g_m_same_ids.append(sto1)
            g_m_same_ids.append(sto2)
        else: g_m_same.append(0)
        if sto1_row[4] == "F" and sto2_row[4]=="F":
            g_f_same.append(1)
            g_f_same_ids.append(sto1)
            g_f_same_ids.append(sto2)
        else: g_f_same.append(0)
    
    no_exp = sum(no_exp)
    low_exp = sum(low_exp)
    g_m_same = sum(g_m_same)
    g_f_same = sum(g_f_same)
    g_same = g_m_same + g_f_same
    
    dupl = 0
    dupl_natl_combos = []
    for i in natl_combos:
        if natl_combos.count(i) > 1:
            dupl_natl_combos.append(i)
            dupl = dupl + 1
    
    frequency = {}
    # iterating over the list
    for item in dupl_natl_combos:
        # checking the element in dictionary
        if item in frequency:
            # incrementing the counr
            frequency[item] += 1
        else:
            # initializing the count
            frequency[item] = 1

    # printing the frequency
   
    opt_df = opt_df.sample(frac = 1, random_state = 1).reset_index(drop = True)     
   
    #building back the dataset sorted in pairs
    paired_df_rows = []
    for i, j, k, n in zip(opt_df["sto1"], opt_df["sto2"],
                          opt_df["c"], range(0,len(opt_df.index))):
        sto1_row = stos[(stos["id"]==i)]
        sto2_row = stos[(stos["id"]==j)]
        sto1_row = list(sto1_row.iloc[0])
        sto2_row = list(sto2_row.iloc[0])
        sto1_row.insert(0,k)
        sto2_row.insert(0,k)
        sto1_row.insert(0,str("Team"+str(n+1)))
        sto2_row.insert(0,str("Team"+str(n+1)))
        paired_df_rows.append(sto1_row)
        paired_df_rows.append(sto2_row)
    
    
    paired_df = pd.DataFrame(paired_df_rows)
    paired_df.columns=['Team_id','Compatibility Score',"id",'Full Name','N1',
                       'Age','Gender','First Mission','No Experience','ODIHR Missions','ODIHR Days',
                       'Other EOMs','Other EOM Days','Other EOM Orgs','Other EOM Multiplier',
                       'Experience Score','Experienced','How','Warnings','Citizenship',
                       'Adjusted ODIHR Days','Adjusted Other EOM Days','First Name',
                       'Last Name','Middle Name','Previous LTO',"E-Learning","Training",
                       "Adjusted Weighted ODIHR Days","Adjusted Weighted Non-ODIHR EOM Days",
                       "Total Adjusted Weighted Days",
                       "Airport","Accomodation","Arrival Date",
                       "Arrival Time","Arrival By","Arrival Flight Number",
                       "Departure Date","Departure Time","Departure By", 
                       "Departure Flight Number","Selection Procedure","Selected As",
                       "LTO Missions"]
    paired_df.drop(["N1","No Experience","Experienced","How","Other EOM Multiplier",
                    "First Mission"], axis=1, inplace=True)
    paired_df = paired_df.reindex(columns=['Team_id',
                               'Citizenship','Age','Gender','Experience Score','Compatibility Score',
                               'ODIHR Missions','ODIHR Days',
                               'Other EOMs','Other EOM Days', "Adjusted Weighted ODIHR Days",
                               "Adjusted Weighted Non-ODIHR EOM Days",
                               "Total Adjusted Weighted Days",
                               'Other EOM Orgs','Previous LTO','LTO Missions',
                               'Warnings', "E-Learning","Training","Airport",
                               "Accomodation","Arrival Date",
                               "Arrival Time","Arrival By","Arrival Flight Number",
                               "Departure Date","Departure Time","Departure By",
                               "Departure Flight Number",'First Name','Middle Name','Last Name',"Full Name",
                               "Selection Procedure","Selected As",
                               "id"])
    
    if middle_name is not True: paired_df.drop(columns=['Middle Name'],axis=1,
                                               inplace=True)
    
    exps = paired_df["Experience Score"]
    teams = paired_df["Team_id"]

    
    comb_exps = []
    for i,j,k in zip(exps,teams,range(len(exps))):
        exp1 = i
        if k == 0:
            exp2 = exps[k+1]
        elif j==teams[k-1]:
            exp2 = exps[k-1]
        else: exp2 = exps[k+1]
        comb_exp = exp1+exp2
        comb_exps.append(comb_exp)
    
    paired_df["Combined Experience"] = comb_exps
    
    #adding third team member
    team_id = False
    
    if third_yn:
        if unsel_gender=="M" and g_m_same>0:
            opp_same = g_m_same_ids
        elif unsel_gender =="F" and g_f_same>0:
            opp_same = g_f_same_ids
        else: opp_same = 0
        
        by_comb = paired_df.sort_values(["Combined Experience"],ascending = False)
        
        if opp_same != 0:
            by_comb_opp = by_comb[by_comb["id"].isin(opp_same)]
            by_comb = by_comb[~by_comb["id"].isin(opp_same)]
            frames = [by_comb_opp,by_comb]
            by_comb = pd.concat(frames)
        
        natls = by_comb["Citizenship"]
        genders = by_comb["Gender"]
        for i, j,k,g in zip(natls,range(len(by_comb.index)),by_comb["Team_id"],genders):
            if j%2==0:
                n1 = i
                n2 = natls[j+1]
                comb_ntl = [n1,n2]
                g1 = g
                g2 = genders[j+1]
                g3 = sel_gender
            if third_n1 not in comb_ntl:
                third_team = k
                if (g1 == g2) and (g1 != g3):
                    if unsel_gender=="M":
                        g_m_same = g_m_same - 1
                        g_same = g_same - 1
                    if unsel_gender=="F":
                        g_f_same = g_f_same - 1
                        g_same = g_same - 1
                break
                
    
    #building third team member row
        third = list(third)
        third.insert(0,third_team)
        third.insert(1,"NA")
        third_series = pd.Series(third,index=['Team_id','Compatibility Score',"id",'Full Name','N1',
                           'Age','Gender','First Mission','No Experience','ODIHR Missions','ODIHR Days',
                           'Other EOMs','Other EOM Days','Other EOM Orgs','Other EOM Multiplier',
                           'Experience Score','Experienced','How','Warnings','Citizenship',
                           'Adjusted ODIHR Days','Adjusted Other EOM Days','First Name',
                           'Last Name','Middle Name','Previous LTO',"E-Learning","Training",
                           "Adjusted Weighted ODIHR Days","Adjusted Weighted Non-ODIHR EOM Days",
                           "Total Adjusted Weighted Days",
                           "Airport","Accomodation","Arrival Date",
                           "Arrival Time","Arrival By","Arrival Flight Number",
                           "Departure Date","Departure Time","Departure By", 
                           "Departure Flight Number","Selection Procedure","Selected As",
                           "LTO Missions"])
        third_series.drop(["N1","No Experience","Experienced","How","Other EOM Multiplier",
                        "First Mission"],inplace=True)
        third_series = third_series.reindex(['Team_id',
                                   'Citizenship','Age','Gender','Experience Score','Compatibility Score',
                                   'ODIHR Missions','ODIHR Days',
                                   'Other EOMs','Other EOM Days', "Adjusted Weighted ODIHR Days",
                                   "Adjusted Weighted Non-ODIHR EOM Days",
                                   "Total Adjusted Weighted Days",
                                   'Other EOM Orgs','Previous LTO','LTO Missions',
                                   'Warnings', "E-Learning","Training","Airport",
                                   "Accomodation","Arrival Date",
                                   "Arrival Time","Arrival By","Arrival Flight Number",
                                   "Departure Date","Departure Time","Departure By",
                                   "Departure Flight Number",'First Name','Middle Name','Last Name',
                                   'Full Name',"Selection Procedure","Selected As",
                                   "id"])

        team_id = third_series["Team_id"]
        team_id_no = (int(team_id[4:])*2)-1
        paired_df = insert_row(team_id_no, paired_df, third_series) 
    scores = [[g_same,g_m_same,g_f_same],dupl,no_exp,low_exp]
    
    
    return [paired_df, scores, frequency, team_id]