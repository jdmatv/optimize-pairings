# -*- coding: utf-8 -*-
"""
Building STO indicators dataset used in library.lib3
Created on Sat Oct 29 12:47:26 2022

@author: Joseph Matveyenko
"""

def create_stos(file, 
                lvl1_multiplier = 0.5,lvl2_multiplier = 0.2, 
                lvl3_multiplier=0.01,
                sto_cap = 10, lto_cap = 60, ct_cap = 75,sto_days_min=7, 
                lto_days_min=50, ct_days_min=60,
                sto_w=5, lto_w=1, ct_w=1, hq_w=0.05, first_prop=0.4,
                print_mode=0):
    
    import warnings
    warnings.filterwarnings("ignore")
  
    from datetime import date
    import statistics as st
    import re
    import pandas as pd
    import numpy as np

    def remove_from_list(the_list, val):
       return [value for value in the_list if value != val]
    
    def list_duplicates_of(seq,item):
        start_at = -1
        locs = []
        while True:
            try:
                loc = seq.index(item,start_at+1)
            except ValueError:
                break
            else:
                locs.append(loc)
                start_at = loc
        return locs
    
    def age(birthdate):
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    
    multipliers = [0,lvl1_multiplier,lvl2_multiplier,lvl3_multiplier]
    file_path = file
    
    imp_combos = []
    
    raw_STO = pd.read_excel(file_path, sheet_name="ExpertTable",skiprows=3)    

    # extracting nationality data
    natl = raw_STO["Nationality"]
    natl_split = []
    for i in natl:
        natls = i.split(", ")
        natls = remove_from_list(natls, "Republic of")
        for j,k in zip(natls,range(len(natls))):
            if natls[k]=="Sverige": natls[k]="Sweden"
            
        natl_split.append(natls)
    
    natls_stripped = []
    for n in natl_split:
        n = n[0]
        n_strip = n.strip()
        natls_stripped.append(n_strip)
    
    natls = natls_stripped
    
    id_pt1 = ["STO"]*len(natls)
    id_pt2 = list(range(1,len(natls) + 1))
    ids = [k + str(l) for k, l in zip(id_pt1, id_pt2)]
    
    """Creating stos dataset, starting with nationality data"""
    stos_d = {"id":ids,"N1":natls}
    stos = pd.DataFrame(stos_d)
    
    # Creating unique IDs for every STO    
    # Checking for shared citizenship
    for  m, n in zip(stos["id"], stos["N1"]):
        same_n = list_duplicates_of(list(stos["N1"]), n)

        # extracting elements of same_n list - simplifying structure
        same_n_org = []
        for q in same_n:
            if isinstance(q, int): 
                same_n_org.append(q)
            else: 
                for r in q:
                    if isinstance(r, int):
                        same_n_org.append(r)
                    else: 
                        for s in r:
                            same_n_org.append(s)
                         
        same_n = list(set(same_n_org))
        
        same_n_lb = []
        for t in same_n:
            n = str(t+1)
            same_n_lb.append("STO"+n)
        
        # adding same citizenship pairs to imp_combos list
        for u in same_n_lb:
            imp_combos.append(m+"_"+u)
    
    # Creating name column using first, middle, last name data
    names = []
    for i, j, k in zip(raw_STO["First Name"], raw_STO["Middle Name"], raw_STO["Last Name"]):
        if pd.isna(i): i = ""
        if pd.isna(j): j = ""
        if pd.isna(k): k = ""
        name = i+" "+j+" "+k
        name = name.replace("  "," ")
        name = name.replace("  "," ")
        names.append(name)
    
    stos.insert(1, "Name", names)
    
    # Calculating age based on DOB and adding to stos dataset
    ages = []
    for i in raw_STO["Date of birth"]:
        ages.append(age(i))
    
    # Adding ODIHR training, e-learning
    odihr_elearning = raw_STO["ODIHR e-learning"]
    odihr_training = raw_STO["ODIHR Training"]
    training = []
    for o_tr in odihr_training:
        if o_tr>0: training.append("Yes")
        else: training.append("No")
    
    any_training = []
    for el,tr in zip(odihr_elearning,training):
        if el=="Yes" or tr=="Yes":
            any_training.append("Yes")
        else: any_training.append("No")
        
    """
    Creating the following experience indicators:
        -First mission (Yes/No)
        -# of ODIHR missions (CT/LTO/STO/HQ)
        -# of days on ODIHR missions (CT/STO/LTO/HQ)
        -# of weighted days on ODIHR missions (CT/STO/LTO/HQ)
        -# of other EOMs (CT/LTO/STO) [note: does not include HQ column]
        -# of days on other EOMs (CT/LTO/STO) [note: does not include HQ column]
        -# of weighted days on other EOMs
        -Adjusted # of days on ODIHR missions (CT/STO/LTO/HQ)
        -Adjusted # of days on other EOMs (CT/STO/LTO)
    """
    firsts = []
    missions = []
    days = []
    w_days = []
    o_missions = []
    o_days = []
    w_o_days = []
    adj_days = []
    adj_o_days = []
    warnings = []
    prev_lto = []
    lto_ms = []
    for tot_m,o_ct, o_lto, o_sto, ct_n, lto_n, sto_n, hq_n,ind in zip(raw_STO["ODIHR"],
                          raw_STO["Total 1"], raw_STO["Total 2"],
                          raw_STO["Total 3"], raw_STO["ODIHR 1"], raw_STO["ODIHR 2"],
                          raw_STO["ODIHR 3"],raw_STO["ODIHR 4"],range(len(raw_STO["ODIHR"]))):

        # Splitting missions and days into separate values
        o_ct_d = o_ct.split("(",1)[1]
        o_lto_d = o_lto.split("(",1)[1]
        o_sto_d = o_sto.split("(",1)[1]
        ct_d = ct_n.split("(",1)[1]
        lto_d = lto_n.split("(",1)[1]
        sto_d = sto_n.split("(",1)[1]
        hq_d = hq_n.split("(",1)[1]
        
        o_ct_d = int(o_ct_d[:-2])
        o_lto_d = int(o_lto_d[:-2])
        o_sto_d = int(o_sto_d[:-2])
        ct_d = int(ct_d[:-2])
        lto_d = int(lto_d[:-2])
        sto_d = int(sto_d[:-2])
        hq_d = int(hq_d[:-2])
        
        ct_m = int(ct_n.split("(",1)[0])
        lto_m = int(lto_n.split("(",1)[0])
        sto_m = int(sto_n.split("(",1)[0])
        hq_m = int(hq_n.split("(",1)[0])
        
        m_n = ct_m + lto_m + sto_m +hq_m
        d = ct_d + lto_d + sto_d + hq_d

        missions.append(m_n)
        days.append(d)
        
        o_ct_d = o_ct_d - ct_d
        o_lto_d = o_lto_d - lto_d
        o_sto_d = o_sto_d - sto_d
        
        
        # Adding total mission days and subtracting ODIHR days to obtain other days
        o_ds = (o_ct_d + o_lto_d + o_sto_d)
        
        o_ct_m = int(o_ct.split("(",1)[0])
        o_lto_m = int(o_lto.split("(",1)[0])
        o_sto_m = int(o_sto.split("(",1)[0])
        ct_m = int(ct_n.split("(",1)[0])
        lto_m = int(lto_n.split("(",1)[0])
        sto_m = int(sto_n.split("(",1)[0])
        hq_m = int(hq_n.split("(",1)[0])        
        
        
        o_ct_m = o_ct_m - ct_m
        o_lto_m = o_lto_m - lto_m
        o_sto_m = o_sto_m - sto_m
        o_ms = (o_ct_m + o_lto_m + o_sto_m)
        
        o_missions.append(o_ms)
        o_days.append(o_ds)
        
        lto_ms.append(lto_m)
        
        # adjusting number of days based on number of missions
        warning = []

        if sto_m==0: 
            if sto_d>0: lto_d=0; warning.append("STO too many days")
        elif sto_d/sto_m > sto_cap:
            sto_d = sto_m*sto_cap
            warning.append("STO too many days")

        if lto_m==0: 
            if lto_d>0: lto_d=0; warning.append("LTO too many days")
        elif lto_d/lto_m > lto_cap:
            lto_d = lto_m*lto_cap
            warning.append("LTO too many days")
        
        if ct_m==0: 
            if ct_d>0: ct_d=0; warning.append("CT too many days")
        elif ct_d/ct_m > ct_cap:
            ct_d = ct_m*ct_cap
            warning.append("CT too many days")
           
        if o_sto_m==0:
            if o_sto_d>0: o_sto_d=0; warning.append("External STO excess days")
        elif o_sto_d/o_sto_m > sto_cap:
            o_sto_d = o_sto_m*sto_cap
            warning.append("External STO excess days")

        if o_lto_m==0:
            if o_lto_d>0: o_lto_d=0; warning.append("External LTO excess days")
        elif o_lto_d/o_lto_m > lto_cap:
            o_lto_d = o_lto_m*lto_cap
            warning.append("External LTO excess days")

        if o_ct_m==0:
            if o_ct_d>0: o_ct_d=0; warning.append("External CT excess days")
        elif o_ct_d/o_ct_m > ct_cap:
            o_ct_d = o_ct_m*ct_cap
            warning.append("External CT excess days")

        # If too few days per mission
        if sto_m > 0 and sto_d/sto_m < sto_days_min: 
            sto_d = sto_m*sto_days_min
            warning.append("STO too few days")
        
        if lto_m > 0 and lto_d/lto_m < lto_days_min: 
            lto_d = lto_m*lto_days_min
            warning.append("LTO too few days")
            
        if ct_m > 0 and ct_d/ct_m < ct_days_min: 
            ct_d = ct_m*ct_days_min
            warning.append("CT too few days")
          
        warnings.append(warning)
        adj_d = sto_d + lto_d + ct_d + hq_d

        adj_o_d = o_sto_d + o_lto_d + o_ct_d   

        adj_days.append(adj_d)
        adj_o_days.append(adj_o_d)
            
        adj_w_d = round(ct_w*ct_d + lto_w*lto_d + sto_w*sto_d + hq_w*hq_d)
        adj_w_o_ds = round((ct_w*o_ct_d + lto_w*o_lto_d + sto_w*o_sto_d))
        
        w_o_days.append(adj_w_o_ds)
        w_days.append(adj_w_d)
        
        if(adj_w_o_ds <0):
            print(ids[ind])
            print(adj_w_d,d,adj_w_o_ds,o_ds,warning,"\n")
            print(sto_days_min,lto_days_min,ct_w)
        
        if m_n == 0:
            firsts.append("Yes")
        else: 
            firsts.append("No")
        
        if lto_d > 1 and lto_m > 0:
            prev_lto.append("Yes")
        else:
            prev_lto.append("No")
        
    # Extracting and manipulating details on where other missions took place
    mission_loc = []
    lvls = []
    for i, j in zip(raw_STO["Full Details 2"], o_missions):
        lvl = 0
        if j>0: 
            i=i.split("\n")
            non_ODIHR = []
            lvl = 3
            orgs = []
            for k in i:
                if k[0:10] != "OSCE/ODIHR": 
                    non_ODIHR.append(k)
                    if k[0:2]=="EU" or k[0:14]=="European Union": lvl = 1; orgs.append("EU")
                    if k[0:4]=="E.U.": lvl = 1; orgs.append("EU")
                    if k[0:16]=="European Council": lvl = 1; orgs.append("European Council")
                    if k[0:19]=="European Parliament" or k[0:13]=="Parliamentary": lvl = 1; orgs.append("European Parliament")
                    if k[0:6]=="Carter" or k[0:10]=="The Carter": lvl = 1; orgs.append("TCC")
                    if k[0:4]=="NATO": lvl = 1; orgs.append("NATO")
                    if k[0:8]=="Congress": lvl = 1; orgs.append("Congress of Local and Regional Authorities")
                    if lvl == 3:
                        if k[0:3]=="NDI" or k[0:10]=="National D": lvl = 2; orgs.append("NDI")
                        if k[0:5]=="ENEMO" or k[0:16]=="European Network": lvl = 2; orgs.append("ENEMO")
                    else:
                        if k[0:3]=="NDI" or k[0:10]=="National D": orgs.append("NDI")
                        if k[0:5]=="ENEMO" or k[0:16]=="European Network": orgs.append("ENEMO")
                    if lvl == 3: orgs.append("Other")
            orgs = list(set(orgs))
            orgs = ', '.join(orgs)
            mission_loc.append(orgs)
        else: mission_loc.append("None")
        lvls.append(lvl)
    
    multiplier = [multipliers[i] for i in lvls]
    
    abs_no_exp = []
    for x,y,z,z2 in zip(firsts, any_training,o_missions,o_days):
        if y == "Yes":
            abs_no_exp.append("No")
        elif x == "No":
            abs_no_exp.append("No")
        elif z > 0:
            abs_no_exp.append("No")
        elif z2 > 0:
            abs_no_exp.append("No")
        else:
            abs_no_exp.append("Yes")
    
    no_of_firsts = firsts.count("Yes")
    if no_of_firsts / (len(firsts)) < first_prop:
        firsts_or = firsts
    else: 
        firsts_or = abs_no_exp
        if print_mode==1:
            print("Warning: too many STOs without ODIHR experience")
            print("Utilizing training, e-learning, and other EOM data\n")
        
    # adding first mission pairs to imp_combos list
    for i, m in zip(firsts_or, stos["id"]):
        inex = []
        if i=="Yes":
            inex.append(list_duplicates_of(firsts_or, i))
        
        # simplifying structure of inex list
        inex_org = []
        for q in inex:
            if isinstance(q, int): 
                inex_org.append(q)
            else: 
                for r in q:
                    if isinstance(r, int):
                        inex_org.append(r)
                    else: 
                        for s in r:
                            inex_org.append(s)
    
        inex_n = list(set(inex_org))
        
        inex_n_lb = []
        for t in inex_n:
            n = str(t+1)
            inex_n_lb.append("STO"+n)
        
        for u in inex_n_lb:
            imp_combos.append(m+"_"+u)
            
    imp_combos = list(set(imp_combos))
    
    """
    The distribution of EOM days is decreasing exponential with mode and min of 0
    Natural log of tot_days is used to obtain a normal-like distribution
    """    
    # tot_days is total days on EOM missions (using non ODIHR multiplier)
    # Using adjusted days
    tot_days = [i + (mult*j) for i, j, mult in zip(w_days,w_o_days,multiplier)]
    tot_days_log = []
    for i in tot_days:
        if i <= 0.5: i = 0.5
        tot_days_log.append(np.log(i))
   
    """
    Assigning experience scores to STOs (range: 0.00-1.00):
    -Experience score is natural log of STOs EOM days 
        divided by 96th percentile of natural log EOM days
        for STOs on the mission.
    -Artificial upper limit of 1 and lower limit of 0
    """    
    tot_days_pc = []
    for i in tot_days_log:
        exp_score = i/np.percentile(tot_days_log, 96) # how exp_score is calculated
        if exp_score >= 1: tot_days_pc.append(1) # upper limit
        elif exp_score >=0: tot_days_pc.append(round(exp_score, 2))
        else: tot_days_pc.append(0) # lower limit
    
    mean_exp = round(st.mean(tot_days_pc),2)
    median_exp = st.median(tot_days_pc)
    
    if mean_exp>median_exp: mean_exp=median_exp
    
    experienced = []
    dev = []
    for i in tot_days_pc:
        if i >= mean_exp: experienced.append("YES")
        if i < mean_exp: experienced.append("NO")
        dev.append(abs(i - mean_exp))
    
    warnings_flat = []
    for i in warnings:
        if len(i)==0: warnings_flat.append('None')
        else: warnings_flat.append(', '.join(i))
    
    # processing Selection column
    
    sel_ass = []
    sel_procs = []
    
    selected_col = raw_STO["Selection"]
    for sel in selected_col:
        sel = re.sub("\n","",sel)
        if "Position:" in sel:
            s1 = sel.split("Position:",1)
            s1_pt1 = s1[0]
            if "Selection procedure:" in s1_pt1:
                sel_proc = re.sub("Selection procedure:","",s1_pt1)
                sel_proc = sel_proc.strip()
            else: sel_proc = ""
            s1_pt2 = s1[1]
            
            if "Selected as:" in s1_pt2:
                s2 = s1_pt2.split("Selected as:")
                s2_pt2 = s2[1]
                sel_as = re.sub("Selected as:","",s2_pt2)
                sel_as = sel_as.strip()
                if "Selected for:" in sel_as:
                    sel_as_pt1 = sel_as.split("Selected for:",1)
                    sel_as = sel_as_pt1[0]
                    sel_as = sel_as.strip()
            else: sel_as = ""
        else:
            sel_as = ""
            sel_proc = ""
        
        sel_ass.append(sel_as)
        sel_procs.append(sel_proc)
    
    a_date = raw_STO["Arrival Date and Time (Date)"]
    a_time = raw_STO["Arrival Date and Time (Time)"]
    dep_date = raw_STO["Departure Date and Time (Date)"]
    dep_time =  raw_STO["Departure Date and Time (Time)"]
    
    a_d = []
    a_t = []
    d_d = []
    d_t = []
    for ad,at,dd,dt in zip(a_date,a_time,dep_date,dep_time):
        if isinstance(ad,pd.Timestamp): a_d.append(ad.date())
        else: a_d.append("")
        if isinstance(at,pd.Timestamp):
            a_t.append(at.time())
        else: a_t.append("")
        if isinstance(dd,pd.Timestamp): d_d.append(dd.date())
        else: d_d.append("")
        if isinstance(dt,pd.Timestamp): d_t.append(dt.time())
        else: d_t.append("")
    
    
    t1s=[]
    t2s=[]
    for t1,t2,plane_a,plane_d in zip(a_t,d_t,raw_STO["Arrival By"],
                              raw_STO["Departure By"]):
        if plane_a == "Plane" and t1 !="":
            t1s.append(1)
        elif plane_a =="Plane" and t1 =="":
            t1s.append(0)
        elif plane_a != "Plane":
            t1s.append(0.5)
        else: t1s.append(0)

        if plane_d == "Plane" and t2 !="":
            t2s.append(1)
        elif plane_d =="Plane" and t2 =="":
            t2s.append(0)
        elif plane_d != "Plane":
            t2s.append(0.5)
        else:
            t2s.append(0)
   
    if st.mean(t1s) <0.5: a_t = a_time
    if st.mean(t2s)<0.5: d_t = dep_time
    
   
    # adding columns to stos dataset
    stos["Age"] = ages #3
    stos["Gender"] = raw_STO["Gender"]
    stos["First"] = firsts #5
    stos["Abs No Experience"] = abs_no_exp
    stos["Missions"] = missions
    stos["Days"] = days
    stos["Non_ODIHR_EOMs"] = o_missions
    stos["Non-ODIHR EOM Days"] = o_days
    stos["Non-ODIHR EOM Org"] = mission_loc
    stos["Non-ODIHR Multiplier"] = multiplier 
    stos["Experience Score"] = tot_days_pc
    stos["Experienced"] = experienced
    stos["How (In)experienced"] = dev
    stos["Warnings"] = warnings_flat
    stos["Nationality"] = natls
    stos["Adjusted Days"] = adj_days
    stos["Adjusted Other EOM Days"] = adj_o_days
    stos["First Name"] = raw_STO["First Name"]
    stos["Last Name"] = raw_STO["Last Name"]
    stos["Middle Name"] = raw_STO["Middle Name"]
    stos["Previous LTO"] = prev_lto
    stos["E-Learning"] = odihr_elearning
    stos["Training"]= odihr_training
    stos["Adjusted Weighted ODIHR Days"]= w_days
    stos["Adjusted Weighted Non-ODIHR EOM Days"]= w_o_days
    stos["Total Adjusted Weighted Days"]= tot_days
    stos["Airport"] = raw_STO["Airport of departure and return"]
    stos["Accomodation"] = raw_STO["Accommodation Assistance"]
    stos["Arrival Date"] = a_d
    stos["Arrival Time"] = a_t
    stos["Arrival By"] = raw_STO["Arrival By"]
    stos["Arrival Flight Number"] = raw_STO["Arrival Flight Number"]
    stos["Departure Date"] = d_d
    stos["Departure Time"] = d_t
    stos["Departure By"] = raw_STO["Departure By"]
    stos["Departure Flight Number"] = raw_STO["Departure Flight Number"]
    stos["Selection Procedure"] = sel_procs
    stos["Selected As"] = sel_ass
    stos["LTO Missions"] = lto_ms

    return [stos, imp_combos,raw_STO]