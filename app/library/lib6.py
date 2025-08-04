# -*- coding: utf-8 -*-
"""
Distributes STO teams by region
Created on Fri Oct 28 02:35:42 2022

@author: Joseph Matveyenko
"""
# Criteria 1: equal distribution of nationalities, 
# Criteria 2: at least one previous LTO per region
def distribute_natls(selected_dat,reg_dat):
    
    import math
    import sys
    import pandas as pd
    
    if not reg_dat:
        selected_dat["Region Number"] = [str("") for x in range(len(selected_dat.index))]
        selected_dat["Backup LTO"] = [str("") for x in range(len(selected_dat.index))]
    
        selected_dat = selected_dat.sort_values(["Team_id","Last Name"])
        selected_dat = selected_dat.drop(["id"],axis=1)
    
        return selected_dat
    
    else:

        def flatten(l): return [item for sublist in l for item in sublist]
        
        def split(df, group):
            gb = df.groupby(group)
            return [gb.get_group(x) for x in gb.groups]


        def replaceDuplicates(names):
            hash = {}
            for i in range(0, len(names)):
                if names[i] not in hash:
                    hash[names[i]] = 1
                # Otherwise
                else:
                    count = hash[names[i]]
                    hash[names[i]] += 1
                    names[i] += str(count)

            return(names)
        
        n1 = selected_dat["Citizenship"]
        all_teams = split(selected_dat,"Team_id")
        
        
        reg_n = reg_dat["Region Name"]
        reg_size = reg_dat["STO Teams"]
        reg_no = [x+1 for x in range(len(reg_n))]
        no_of_regs = len(reg_n)
        
        if len(all_teams) != (sum(reg_size)/2):
            sys.exit("Number of STO teams does not match deployment plan.")
        
        all_natls = list(set(list(n1)))
        no_of_natls = len(all_natls)
        
        ntl_count = []
        for ntl in all_natls:
            ntl_count.append(list(n1).count(ntl))
        
        ntl_d = {"ntl":all_natls,"count":ntl_count}
        ntl_df = pd.DataFrame(ntl_d)
        ntl_df = ntl_df.sort_values("count",ascending=False)
        
        reg_props=[]
        ltos_max = []
        ltos_ct = []
        for x,y,z in zip(reg_n,reg_size,reg_no):
            reg_prop = round(y/sum(reg_size),3)
            reg_props.append(reg_prop)
            ltos_max.append(1)
            ltos_ct.append(0)
        
        r_d = {"no":reg_no,"nm":reg_n,"sz":reg_size,"pc":reg_props,
            "lto_max":ltos_max,"lto_ct":ltos_ct,
            "ids":[""]*len(reg_no),"ntls":[""]*len(reg_no)}
        reg_dat = pd.DataFrame(r_d)
        reg_dat = reg_dat.sort_values("pc",ascending=False)
        reg_dat = reg_dat.reset_index(drop=True)
        
        
        for ntl, ct in zip(ntl_df["ntl"],ntl_df["count"]):
            max_n = []
            for pc in r_d["pc"]:
                max_n.append(math.ceil(pc*ct))
            reg_dat[ntl] = max_n
            
        for ntl, ct in zip(ntl_df["ntl"],ntl_df["count"]):
            current_n = []
            for pc in r_d["pc"]:
                current_n.append(0)
            reg_dat[str(ntl+"_ct")]=current_n    
        
        all_natls_wno = list(ntl_df["ntl"])
        all_natls_wno.insert(0,"nm")
        all_natls_wno.insert(1,"sum")
    
        team_vecs = []
        
        for rep in range(10000):
            if len(all_teams) == 0:
                break
            
            if rep == 1:
                new_lto_m = []
                for lto_c,lto_m in zip(reg_dat["lto_ct"],reg_dat["lto_max"]):
                    new_lto_m.append(100)
                reg_dat["lto_max"] = new_lto_m
            
            elif rep>1:
                for ntl, ct in zip(ntl_df["ntl"],ntl_df["count"]):
                    max_n = []
                    for pc in r_d["pc"]:
                        max_n.append(math.ceil(pc*ct)+(rep-1))
                    reg_dat[ntl] = max_n

            
            for sel_ntl in ntl_df["ntl"]:
                
                shuffled_rgs = reg_dat.sample(frac=1).reset_index(drop=True)
                
                rel_tms = []
                rel_ids = []
                rel_ntls = []
                rel_ltos = []
                team_inds = []
                rel_lto_ms = []
                rel_lto_ids = []
                rel_tawds = []
                rel_tawd_ids = []
                for tm, team_ind in zip(all_teams,range(len(all_teams))):
                    team_ntls = list(tm["Citizenship"])
                    rel_team_id = list(tm["Team_id"])
                    rel_prev_lto = list(tm["Previous LTO"])
                
                    if sel_ntl in team_ntls:
                        rel_tms.append(tm)
                        rel_ids.append(rel_team_id[0])
                        rel_ntls.append(team_ntls)
                        team_inds.append(team_ind)
                        
                        lto_counter = 0
                        for rel_stos in rel_prev_lto:
                            if rel_stos == "Yes":
                                lto_counter = 1
                        
                        if lto_counter == 1:
                            rel_ltos.append("Yes")
                        else: rel_ltos.append("No")
        
                        tm = tm.sort_values(by=["LTO Missions","Total Adjusted Weighted Days"],
                                            ascending=False)
                        rel_lto_ms.append(list(tm["LTO Missions"])[0])
                        rel_lto_ids.append(list(tm["id"])[0])
                        
                        tm = tm.sort_values(by=["Total Adjusted Weighted Days"],ascending=False)
                        rel_tawds.append(list(tm["Total Adjusted Weighted Days"])[0])
                        rel_tawd_ids.append(list(tm["id"])[0])                    
                        
                if len(rel_tms) > 0:
        
                    set_used_teams = []
                    for df_idx in range(len(shuffled_rgs.index)):
                        
                        used_teams = []
                        rel_used_teams = []
                        for rel_tm, rel_idx in zip(rel_tms, range(len(rel_tms))):
                            sel_rgn = shuffled_rgs.iloc[df_idx]
                            sel_rgn_nm = sel_rgn[1]
                            sel_rgn_no = sel_rgn[0]
                            
                            rel_tm = rel_tm
                            rel_id = rel_ids[rel_idx]
                            rel_ntl = rel_ntls[rel_idx]
                            rel_ntl_str = "; ".join(rel_ntl)
                            rel_lto = rel_ltos[rel_idx]
                            rel_lto_m = rel_lto_ms[rel_idx]
                            rel_lto_id = rel_lto_ids[rel_idx]
                            rel_tawd = rel_tawds[rel_idx]
                            rel_tawd_id = rel_tawd_ids[rel_idx]
                            team_ind = team_inds[rel_idx]
                            max_str1 = rel_ntl[0]
                            max_str2 = rel_ntl[1]
                            count_str1 = rel_ntl[0]+"_ct"
                            count_str2 = rel_ntl[1]+"_ct"
                            
                            m1 = sel_rgn[max_str1]
                            m2 = sel_rgn[max_str2]
                            c1 = sel_rgn[count_str1]
                            c2 = sel_rgn[count_str2]
                        
                            rgn_count = sum(sel_rgn[-no_of_natls:])
                            rgn_max = sel_rgn["sz"] 
                            
                            rgn_lto_max = sel_rgn["lto_max"]
                            rgn_lto_ct = sel_rgn["lto_ct"]
                            
                            if rel_lto == "Yes":
                                c_lto = 1
                            else: c_lto = 0
                            
                            if (c1 < m1 and c2 < m2) and (rgn_count < rgn_max and 
                                                        (c_lto + rgn_lto_ct <= rgn_lto_max)):
                                a = list(shuffled_rgs[shuffled_rgs.no==sel_rgn_no].iloc[0])
                                b = list(shuffled_rgs[shuffled_rgs.nm==sel_rgn_nm].iloc[0])
                                c = list(reg_dat[reg_dat.no==sel_rgn_no].iloc[0])
                                d = list(reg_dat[reg_dat.nm==sel_rgn_nm].iloc[0])
                                if (a[13] != b[13] or b[11] != c[11]) or  (c[9] != d[9] or b[10] != c[10]):
                                    print("INDEX ERROR")
                                    
                                shuffled_f = shuffled_rgs[shuffled_rgs.nm==sel_rgn_nm]
                                reg_dat_f = reg_dat[reg_dat.nm==sel_rgn_nm]
                                
                                sh_i = int(shuffled_f.index.values[0])
                                r_d_i = int(reg_dat_f.index.values[0])
                                cs1 = count_str1
                                cs2 = count_str2
                        
                                
                                shuffled_rgs.at[sh_i,cs1] = int(int(shuffled_rgs.loc[sh_i,cs1]) + 1)
                                shuffled_rgs.at[sh_i,cs2] = int(int(shuffled_rgs.loc[sh_i,cs2]) + 1)
                                reg_dat.at[r_d_i,cs1] = int(int(reg_dat.loc[r_d_i,cs1]) + 1)
                                reg_dat.at[r_d_i,cs2] = int(int(reg_dat.loc[r_d_i,cs2]) + 1)
                                reg_dat.at[r_d_i,"lto_ct"] = int(int(reg_dat.loc[r_d_i,"lto_ct"]) + c_lto)
                                shuffled_rgs.at[sh_i,"lto_ct"] = int(int(shuffled_rgs.loc[sh_i,"lto_ct"]) + c_lto)
                                
                                if (reg_dat.loc[r_d_i,"ids"] == ""):
                                    reg_dat.at[r_d_i,"ids"] = rel_id
                                else:
                                    reg_dat.at[r_d_i,"ids"] = str(str(reg_dat.loc[r_d_i,"ids"])+"; "+str(rel_id))
                                
                                if (reg_dat.loc[r_d_i,"ntls"] == ""):
                                    reg_dat.at[r_d_i,"ntls"] = rel_ntl_str
                                else: 
                                    reg_dat.at[r_d_i,"ntls"] = str(str(reg_dat.loc[r_d_i,"ntls"])+"; "+str(rel_ntl_str))
        
                                
                                team_vec = pd.Series({'team_id':rel_id, 'ntl':rel_ntl_str,'rg_nm':sel_rgn_nm,
                                                    'rg_no':sel_rgn_no,'lto_exp':rel_lto,
                                                    'lto_m':rel_lto_m, 'tawd':rel_tawd,
                                                    'lto_m_id':rel_lto_id,'tawd_id':rel_tawd_id})
            
                                used_teams.append(team_inds[rel_idx])
                                rel_used_teams.append(rel_idx)
                                team_vecs.append(team_vec)
                                
                        set_used_teams.append(used_teams)
                    
                    
                        for unw in sorted(rel_used_teams,reverse=True):
                            del rel_tms[unw]
                            del rel_ids[unw]
                            del rel_ntls[unw]
                            del team_inds[unw]
                            del rel_lto_ms[unw]
                            del rel_lto_ids[unw]
                            del rel_tawds[unw]
                            del rel_tawd_ids[unw]
                            
                    set_used_teams = flatten(set_used_teams)
                    
                    for unw in sorted(set_used_teams,reverse=True):
                        del all_teams[unw]            
            
            
        teams_by_reg = pd.DataFrame(team_vecs).sort_values(["rg_no","team_id"])
        team_no_counter = 0
        rgn_numbers = list(teams_by_reg["rg_no"])
        new_team_nos = []
        for nos,ind in zip(teams_by_reg["rg_no"],range(len(teams_by_reg.index))):

            if ind>0:
                if nos != rgn_numbers[ind-1]:
                    team_no_counter = 0
            
            team_no_counter = team_no_counter + 1
            
            rg_no = nos
            if rg_no < 10: 
                rg_no = str(str(0)+str(rg_no))
            else:
                rg_no = str(rg_no)

            tm_dig = team_no_counter
            
            if tm_dig<10:
                tm_dig = str(str(0)+str(tm_dig))
            else:
                tm_dig = str(tm_dig)
            new_team_no = str(str(rg_no)+str(tm_dig))
            new_team_nos.append(new_team_no)
        
        teams_by_reg["new_team_no"] = new_team_nos
        
        teams_sp = split(teams_by_reg, "rg_no")

            
        lto_exp = 0
        lto_replacements = []
        for rg in teams_sp:
            exp_counter = 0
            if "Yes" in list(rg["lto_exp"]):
                exp_counter = 1
            lto_exp = lto_exp + exp_counter
            rg = rg.sort_values(["lto_m","tawd"],ascending=False)
            best = rg.iloc[0]
            if best["lto_m"]==0:
                most_exp_sto = best["tawd_id"]
            else: 
                most_exp_sto = best["lto_m_id"]
            lto_replacements.append(most_exp_sto)
            
            
            
            
                
                #if exp_counter == 0:
        sto_rgn_nm = []
        sto_rgn_no = []
        replacement_yn = []
        sto_team_no = []           
        for team_id,sto_id in zip(selected_dat["Team_id"],selected_dat["id"]):
            for reg_tid,rgn_nm,rgn_no,team_no in zip(teams_by_reg["team_id"],
                                            teams_by_reg["rg_nm"],
                                            teams_by_reg["rg_no"],
                                            teams_by_reg["new_team_no"]):
                if team_id == reg_tid:
                    sto_rgn_nm.append(rgn_nm)
                    sto_rgn_no.append(rgn_no)
                    sto_team_no.append(team_no)
            if sto_id in lto_replacements:
                replacement_yn.append("Yes")
            else:
                replacement_yn.append("No")
            
        print("\n"+str(lto_exp)+"/"+str(no_of_regs)+" regions have an LTO")
        
        #selected_dat["Region Number"] = sto_rgn_no
        selected_dat["Region Number"] = sto_rgn_nm
        selected_dat["Backup LTO"] = replacement_yn
        selected_dat["Team_id"] = sto_team_no
        
        selected_dat = selected_dat.sort_values(["Team_id","Last Name"])
        selected_dat = selected_dat.drop(["id"],axis=1)
        
        return selected_dat


def nice_naming(selected_dat):
    import pandas as pd
    import numpy as np
    from unidecode import unidecode
    
    fst = selected_dat["First Name"]
    lst = selected_dat["Last Name"]

    fst_nice = []
    lst_nice = []
    for f, l in zip(fst, lst):
        fst_nice.append(unidecode(f).upper())
        lst_nice.append(unidecode(l).upper())

    selected_dat.insert(1,"First",fst_nice)
    selected_dat.insert(2, "Last",lst_nice)

    selected_dat = selected_dat.replace(r'^\s*$', np.nan, regex=True)


    return selected_dat.reset_index(drop=True)
    

