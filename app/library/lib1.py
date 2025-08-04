# -*- coding: utf-8 -*-
"""
Modules used in library.lib3
Created on Sat Oct 15 10:56:01 2022

@author: Joseph Matveyenko
"""

# This function returns the combination of two STOs' nationalities
def check_natl(stos, optimals):
    
    import pandas as pd
    
    if len(optimals) == 0: return(["A_A"])
    if len(optimals) > 0:
        optimals = pd.concat(optimals)
        natl_combos = []
        for i, j in zip(optimals['sto1'],optimals['sto2']):
            sto1_row = (stos[(stos["id"]==i)])
            sto2_row = (stos[(stos["id"]==j)])
            sto1_row = sto1_row.iloc[0]
            sto2_row = sto2_row.iloc[0]
            natl_combo = sorted([sto1_row[2],sto2_row[2]])
            natl_combo = ''.join(natl_combo)
            natl_combos.append(natl_combo)
    return(natl_combos)

# This function gives weights to different nationalities in reducing
# the number of repeated pairs of STO nationalities
def natl_weights(stos,log=False,scale=1):
    
    import pandas as pd
    
    import itertools as it
    import math
    N1 = list(stos['N1'])
    N1_unique = sorted(list(set(N1)))
    N1_combos = list(it.combinations(N1_unique,r=2))

    combos_sorted=[]
    for i in N1_combos:
        combos_sorted.append(sorted(i))
    
    unique_combos = []
    for combo in combos_sorted:
        if combo not in unique_combos:
            unique_combos.append(combo)
    
    natl_counts = stos['N1'].value_counts()
    
    min_freqs = []
    j_combos = []
    for i in unique_combos:
        sto1_freq = int(natl_counts[(natl_counts.index==i[0])])
        sto2_freq = int(natl_counts[(natl_counts.index==i[1])])
        freqs = [sto1_freq,sto2_freq]
        min_freq = min(freqs)
        if log: min_freq = math.log(min_freq)+1
        min_freq = min_freq*scale
        min_freqs.append(min_freq)
        joined = ''.join(i)
        j_combos.append(joined)
    
    d = {'n':j_combos,'m_f':min_freqs}
    return pd.DataFrame(d)

        
# This function calculates the size of each group for pairing STOs 
#   to ensure that it is gradual and even across groups
# (sample size is the desired size of each group; stos_n is # of STOs)

def create_gr_sizes(sample_size,stos_n,permut_size,
                    n_groups,n_groups_div2):

    import math
    import sys

    g_s = sample_size
    seconded = stos_n

    if seconded % 2 != 0: sys.exit("Error! Odd # of STOs")
             
    permut_size = int(g_s/2)
    n_groups = math.ceil(seconded / permut_size)
    if n_groups % 2 != 0: n_groups = int(n_groups + 1)
    n_groups_div2 = int(n_groups/2)
    
    counter = 1
        
    will_1_reach = g_s*n_groups_div2 - 2*(n_groups_div2-1)
    will_1_yn = str("yes") if will_1_reach <= seconded else "no"
        
    will_2_max = g_s + (g_s-2)*(n_groups_div2-2)+(g_s-4)
    will_2_min = g_s + (g_s-2) + (g_s-4)*(n_groups_div2-2)
    
    if seconded <= will_2_max and seconded >= will_2_min:
        will_2_yn = "yes"
    else: will_2_yn = "no"
        
    will_3_max = g_s + (g_s-2) + (g_s-4)*(n_groups_div2-3)+(g_s-6)
    will_3_min = g_s + (g_s-2) + (g_s-4) + (g_s-6)*(n_groups_div2-3)
    
    if seconded <= will_3_max and seconded >= will_3_min:
        will_3_yn = "yes"
    else: will_3_yn = "no" 
    
    for att in range(n_groups_div2):
        if g_s * n_groups_div2 == seconded:
            group_sizes = [str(g_s)]*n_groups_div2
            break

        top_no = g_s
        bottom_no = g_s-2
        top_reps = n_groups_div2-counter
        bottom_reps = counter
        v_bottom_no = g_s-4
        vv_bottom_no = g_s-6
        group_sizes = []
        #print(counter, top_no*top_reps+bottom_no*bottom_reps, seconded)
        
        if will_1_yn == "yes":
            if top_no*top_reps + bottom_no*bottom_reps == seconded:
                group_sizes = [str(g_s)]*(n_groups_div2-counter)
                for ct in range(counter):
                    group_sizes.append(str(g_s-2))
                    
                break
            
        elif will_1_yn == "no" and will_2_yn == "yes":
            #print(counter, top_no+bottom_no*(counter)+v_bottom_no*(top_reps-1), seconded)
            if top_no + bottom_no*(counter) +v_bottom_no*(top_reps-1) == seconded:
                group_sizes = [str(top_no)]
                for ct in range(counter):
                    group_sizes.append(str(bottom_no))
                for tr in range(top_reps-1):
                    group_sizes.append(str(v_bottom_no))
                    #print("USED THIS") 
                break
            
        elif will_3_yn == "yes":
                
            if top_no + bottom_no + v_bottom_no*(counter)+vv_bottom_no*(top_reps-2) == seconded:
                group_sizes = [str(top_no),str(bottom_no)]
                for ct in range(counter):
                    group_sizes.append(str(v_bottom_no))
                for tr in range(top_reps-2):
                    group_sizes.append(str(vv_bottom_no))
                break
            
        else: sys.exit("ERROR") 

        group_sizes = []
        counter = counter+1
    
    group_sizes = [int(x) for x in group_sizes] 
    return group_sizes

# creates nametags for swapping section
def create_nametag(name, attribute,stos,space=False):
    if " " in name:
        pieces = name.split(" ")
        last = pieces[len(pieces)-1]
        first = pieces[0].strip()
        first_l = first[0]
        
        nametag = first_l+". "+last+" ("+attribute+")"
    else:
        nametag = name+" ("+attribute+")"
    
    names = stos["Name"]
    
    lengths = []
    for n in names:
        if " " in n:
            pieces = n.split(" ")
            last = pieces[len(pieces)-1]
            first = pieces[0].strip()
            first_l = first[0]
            
            nt = first_l+". "+last+" ("+attribute+")"
        else:
            nt = name+" ("+attribute+")"
        lengths.append(len(nt))
    
    max_length = max(lengths)
    if max_length>50: max_length=50
    
    diff = max_length - len(nametag)-4
    if diff < 1: diff = 1
    
    if space:
        for d in range(diff):
            nametag = str(nametag+" ")
    
    return nametag
    
# This function swaps STOs between groups to optimize gender diversity    
def g_swap(stos, groups, exp_diff = 0.1, mode = 0, thresh = 0,
               print_mode = 1):
    
    import warnings
    warnings.filterwarnings("ignore")
    
    
    import pandas as pd
    import numpy as np
    import statistics as st
    from operator import itemgetter
    import random
    from library.lib1 import create_nametag
    
    groups_exclude = groups
    gender_dfs = []
    m_diffs = []
    sto1_exp_avgs = []
    for i in groups:
        sto1_id = []
        sto2_id = []
        sto1_gs = []
        sto2_gs = []
        sto1_m = []
        sto1_f = []
        sto2_m = []
        sto2_f = []
        sto1_exp = []
        sto2_exp = []
        sto1_avgs = []
        for sto1, sto2 in zip(i['Low'],i['High']):
            sto1_row = (stos[(stos["id"]==sto1)])
            sto2_row = (stos[(stos["id"]==sto2)])
            sto1_row = sto1_row.iloc[0]
            sto2_row = sto2_row.iloc[0]
            sto1_g = sto1_row[4]
            sto2_g = sto2_row[4]
            sto1_gs.append(sto1_g)
            sto2_gs.append(sto2_g)
            sto1_exp.append(sto1_row[13])
            sto2_exp.append(sto2_row[13])
            if sto1_g == "M": sto1_m.append(1);sto1_f.append(0)
            elif sto1_g == "F": sto1_m.append(0);sto1_f.append(1)
            if sto2_g == "M": sto2_m.append(1);sto2_f.append(0)
            elif sto2_g =="F": sto2_m.append(0);sto2_f.append(1)
            sto1_id.append(sto1)
            sto2_id.append(sto2)
        
        m1_sum = sto1_gs.count("M")
        f2_sum = sto2_gs.count("F")

        sto1_exp_avg = np.repeat(np.array([st.mean(sto1_exp)]),len(sto1_m))
        sto2_exp_avg = np.repeat(np.array([st.mean(sto2_exp)]),len(sto1_m))
        
        m_diff = m1_sum - f2_sum #if positive, more men in col 1 and vice versa
        m_diffs.append(m_diff)
        sto1_avgs.append(sto1_exp_avg)
        d = {'STO1':sto1_id,'STO1_G':sto1_gs, 
             'STO1_EXP':sto1_exp,'STO1_EXP_AVG':sto1_exp_avg,
             'STO2':sto2_id,'STO2_G':sto2_gs, 
             'STO2_EXP':sto2_exp, 'STO2_EXP_AVG':sto2_exp_avg}
        
        sto1_exp_avgs.append(st.mean(sto1_exp))
        gender_df = pd.DataFrame(d)
        gender_dfs.append(gender_df)
   
    more_m = []
    more_f = []
    equal = []
    for i, j,k in zip(m_diffs,gender_dfs,sto1_exp_avgs):
        if i > thresh:
            more_m.append([i,j,k])
        elif i < -thresh:
            more_f.append([i,j,k])
        else:
            equal.append([i,j,k])
    
    shuffle = False
    if mode == 3:
        mode = 2
        shuffle = True
        
    selected_ms = sorted(more_m,key=itemgetter(mode),reverse=True)
    selected_fs = sorted(more_f,key=itemgetter(mode))  
    
    if shuffle:#random shuffle order
        random.shuffle(selected_ms)
        random.shuffle(selected_fs)

    s_1s = []
    s_2s = []
    for selected_m,selected_f in zip(selected_ms,selected_fs):
        if selected_m[2]<=selected_f[2]: # if m less experienced than f
            dat1 = selected_m[1]
            dat2 = selected_f[1]
            m_in_dat1 = dat1[(dat1['STO1_G']=="M")]
            most_exp_m = m_in_dat1[(m_in_dat1['STO1_EXP']==max(m_in_dat1['STO1_EXP']))]

            if len(most_exp_m.index) > 0:
                most_exp_m = most_exp_m.reset_index(drop=True)
                most_exp_m = most_exp_m.loc[0]

            f_in_dat2 = dat2[(dat2['STO1_G']=="F")]
            least_exp_f = f_in_dat2[(f_in_dat2['STO1_EXP']==min(f_in_dat2['STO1_EXP']))]
            if len(least_exp_f.index) > 0:
                least_exp_f = least_exp_f.reset_index(drop=True)
                least_exp_f = least_exp_f.loc[0]
                
            most_exp_m = pd.Series(most_exp_m)
            least_exp_f = pd.Series(least_exp_f)

            if ((float(least_exp_f['STO1_EXP']) 
                 - selected_m[2]) < exp_diff):
                swapper1 = str(most_exp_m['STO1'])
                s_1s.append(swapper1)
                swapper2 = str(least_exp_f['STO1'])
                swapper2_row = (stos[(stos["id"]==swapper2)])
                swapper2_row = swapper2_row.iloc[0]
                swapper2_n = swapper2_row[1]
                
                s_2s.append(swapper2)
                swapper1_row = (stos[(stos["id"]==swapper1)])
                swapper1_row = swapper1_row.iloc[0]
                swapper1_n = swapper1_row[1]
                
                swapper1_n = create_nametag(swapper1_n,"M",stos,space=True)
                swapper2_n = create_nametag(swapper2_n,"F",stos)
                
                if print_mode == 1:
                    print("SWAPPING   "+ swapper1_n+ "   AND   "
                          + swapper2_n)
          
        if selected_f[2]<selected_m[2]:
            dat1 = selected_f[1]
            dat2 = selected_m[1]
            f_in_dat1 = dat1[(dat1['STO1_G']=="F")]
            most_exp_f = f_in_dat1[(f_in_dat1['STO1_EXP']==max(f_in_dat1['STO1_EXP']))]
            if len(most_exp_f.index) > 0:
                most_exp_f = most_exp_f.reset_index(drop=True)
                most_exp_f = most_exp_f.iloc[0]
            m_in_dat2 = dat2[(dat2['STO1_G']=="M")]
            least_exp_m = m_in_dat2[(m_in_dat2['STO1_EXP']==min(m_in_dat2['STO1_EXP']))]
            if len(least_exp_m.index) > 0:
                least_exp_m = least_exp_m.reset_index(drop=True)
                least_exp_m = least_exp_m.iloc[0] 
            most_exp_f = pd.Series(most_exp_f)
            least_exp_m = pd.Series(least_exp_m)
           
            if ((float(least_exp_m['STO1_EXP']) - 
                 selected_f[2]) < exp_diff):
                swapper1 = str(most_exp_f['STO1'])
                s_1s.append(swapper1)
                swapper2 = str(least_exp_m['STO1'])
                s_2s.append(swapper2)
                swapper2_row = (stos[(stos["id"]==swapper2)])
                swapper2_row = swapper2_row.iloc[0]
                swapper2_n = swapper2_row[1]
                swapper1_row = (stos[(stos["id"]==swapper1)])
                swapper1_row = swapper1_row.iloc[0]
                swapper1_n = swapper1_row[1]
                
                swapper1_n = create_nametag(swapper1_n,"F",stos,space=True)
                swapper2_n = create_nametag(swapper2_n,"M",stos)
                
                if print_mode == 1:
                    print("SWAPPING   "+ swapper1_n+ "   AND   "
                          + swapper2_n)
    
    aff_groups=[]
    new_groups = groups_exclude

    for s_1,s_2 in zip(s_1s,s_2s):
        for i, j in zip(groups_exclude,range(len(groups_exclude))):
            dat = new_groups[j]
            dat_low = dat['Low'].tolist()
            if s_1 in dat_low:
                aff_groups.append(j)
                tb=i.replace(s_1,s_2)
                new_groups[j]=tb
    
            elif s_2 in dat_low:
                aff_groups.append(j)
                tb=i.replace(s_2,s_1)
                new_groups[j]=tb
    
    return [new_groups, aff_groups]
    

def g_swap_exp(groups, stos,print_mode,space=False):
    
    import pandas as pd
    from library.lib1 import create_nametag
    
    groups_exclude = groups
    
    sto2_id = []
    sto2_exp = []
    sto2_m = []
    sto2_names = []
    indeces = []
    
    for i,ind in zip(groups,range(len(groups))):
        
        for sto2 in i['High']:
            sto2_row = (stos[(stos["id"]==sto2)])
            sto2_row = sto2_row.iloc[0]
            sto2_id.append(sto2_row[0])
            sto2_exp.append(sto2_row[13])
            sto2_m.append(sto2_row[7])
            sto2_names.append(sto2_row[1])
            indeces.append(ind)
    
    d = {"id":sto2_id,"exp":sto2_exp,"missions":sto2_m,"gr":indeces,
         "name":sto2_names}
    twos = pd.DataFrame(d)
    to_swap = twos[(twos["missions"]==0)]
    to_swap_ids = list(to_swap["id"])

    twos_sorted = twos[(twos["missions"]>0)]
    twos_sorted = twos_sorted.sort_values(["gr","exp"],ascending=False)
    compls = list(twos_sorted["id"])
    compls = compls[0:len(to_swap_ids)]
    
    remove_to = []
    remove_comp = []
    for x, y in zip(to_swap_ids,compls):
        sto1_row = twos[twos["id"]==x]
        sto2_row = twos[twos["id"]==y]
        sto1_row = sto1_row.iloc[0]
        sto2_row = sto2_row.iloc[0]
        sto1_gr = sto1_row[3]
        sto2_gr = sto2_row[3]
        sto1_n = sto1_row[4]
        sto2_n = sto2_row[4]
        
        sto1_ms = str(sto1_row[2])+" Missions"
        sto2_ms = str(sto2_row[2])+" Missions"
        
        sto1_n = create_nametag(sto1_n,sto1_ms,stos,space=space)
        sto2_n = create_nametag(sto2_n,sto2_ms,stos)
        
        if sto2_gr<=sto1_gr:
            remove_to.append(x)
            remove_comp.append(x)
            to_swap_ids.remove(x)
            compls.remove(y)
        else:
            if print_mode == 1:
                print("SWAPPING "+ sto1_n+ " AND "
                  + sto2_n)
    
    s_1s = to_swap_ids
    s_2s = compls
    
    aff_groups=[]
    new_groups = groups_exclude

    for s_1,s_2 in zip(s_1s,s_2s):
        for i, j in zip(groups_exclude,range(len(groups_exclude))):
            dat = new_groups[j]
            dat_high = dat['High'].tolist()
            if s_1 in dat_high:
                aff_groups.append(j)
                tb=i.replace(s_1,s_2)
                new_groups[j]=tb
    
            elif s_2 in dat_high:
                aff_groups.append(j)
                tb=i.replace(s_2,s_1)
                new_groups[j]=tb
     
    return new_groups