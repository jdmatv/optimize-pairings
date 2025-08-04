from fastapi import FastAPI, Body, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import pandas as pd
import math
import os

from library.lib4 import sto_deployer
from library.lib5 import create_stos

auto_run = True     # False is slower but more time and control

"""
Input preferred sample size for each group of pairs for matching algorithm:
MUST BE EVEN NUMBER
    Estimated running time:
        groups of 10 (30 seconds) - NOT RECCOMENDED
        groups of 12 (1-5 minutes)  - NOT RECCOMENDED
        groups of 14 (5-30 minutes) 
        groups of 16 (30 min - 2 hours) 
        groups of 18 (4-12 hours)
        groups of 20 (1-4 days)     - NOT RECCOMENDED
"""

regroup = False # Do you want to rearrange groups to optimize M/F pairs #should be true
est_time = 5 # of seconds to spend estimating runtime
"""

What is your threshold for the greatest proportion of first-time observers
before considering training and e-learning experience (<0.5 reccomended)
"""
first_prop = 0.46
"""

Input weights for experience other than ODIHR below:
  -Level 1 Orgs: EU, Carter Center, NATO, Council of Europe, OSCE/PA
  -Level 2 Orgs: NDI, ENEMO
  -Level 3 Orgs: Everything else
"""
level_1_weight = 0.8
level_2_weight = 0.2
level_3_weight = 0.01
"""
Input weights for following criterion for scoring potentital STO pairs: 
   -Age Weight: How important is small age difference?
   -Gender Weight: How important are m/f pairs?
   -Experience Weight: How important is no two STOs with <2 missions
"""
age_weight = 0
gender_weight = 0.7
exp_weight = 0.3

#how much to subtract for duplicate nation combos (between 0.01-0.1 reccomended)
dupl_n_weight = 0.1
"""
Input limit on maximum number of days for STO, LTO, and CT assignments
   -'sto_days_limit = 10' means maximum 10 days for each STO assignement

Input minimum of days per STO, LTO, and CT assignment
Input weights for different types of days
"""
sto_days_limit = 10
lto_days_limit = 60
ct_days_limit = 70

sto_days_min = 7
lto_days_min = 50
ct_days_min = 60

sto_w = 5
lto_w = 1
ct_w = 1
hq_w = 0.1
"""
Do you need middle names in the final table? 
    -then change 'middle_name = True'
"""
middle_name = True


app = FastAPI()
list_of_usernames = list()
templates = Jinja2Templates(directory="htmldirectory")

def generate_html_response():
    html_content = """
    <html>
        <head>
            <title>ERROR</title>
        </head>
        <body>
        <h2 style="text-family:monospace">Invalid Pin</h2>
        <p style="text-size:60%">contact admin for support </p>
        </body>
    </html
    """
    return HTMLResponse(content=html_content, status_code=200)

def generate_html_response3(nreg,reg_sizes):
    reg_sizes.reverse()
    for i,j in zip(reg_sizes,range(len(reg_sizes))):
        if i > 0:
            reg_no = str(50-j)
            reg_amt = str(i)
            break

    html_content = """
    <html>
        <head>
            <title>ERROR</title>
        </head>
        <body>
        <h2 style="text-family:monospace">ERROR: Invalid regional deployment</h2>
        <p style="text-size:60%">User selected var1 regions. Region #var2 has var3 STO teams...</b>  </p>
        </body>
    </html
    """
    html_content = html_content.replace("var1",str(nreg)).replace("var2",reg_no).replace("var3",reg_amt)
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/home",response_class=HTMLResponse)
def write_home(request: Request):
    return templates.TemplateResponse("home.html",{"request": request})

@app.post("/submitform")
async def handle_form(pin: str = Form(...), STO_List_file: UploadFile = File(...),
gender: str = Form(...), exp: str = Form(...), age: str = Form(...), priority: str = Form(...), out: str = Form(...),
time: str = Form(...),nreg: str = Form(...),r1: str = Form(...),r2: str = Form(...),r3: str = Form(...), r4: str = Form(...), r5: str = Form(...), r6: str = Form(...), r7: str = Form(...), r8: str = Form(...), r9: str = Form(...), r10: str = Form(...), r11: str = Form(...), r12: str = Form(...), r13: str = Form(...), r14: str = Form(...), r15: str = Form(...), r16: str = Form(...), r17: str = Form(...), r18: str = Form(...), r19: str = Form(...), r20: str = Form(...), r21: str = Form(...), r22: str = Form(...), r23: str = Form(...), r24: str = Form(...), r25: str = Form(...), r26: str = Form(...), r27: str = Form(...), r28: str = Form(...), r29: str = Form(...), r30: str = Form(...), r31: str = Form(...), r32: str = Form(...), r33: str = Form(...), r34: str = Form(...), r35: str = Form(...), r36: str = Form(...), r37: str = Form(...), r38: str = Form(...), r39: str = Form(...), r40: str = Form(...), r41: str = Form(...), r42: str = Form(...), r43: str = Form(...), r44: str = Form(...), r45: str = Form(...), r46: str = Form(...), r47: str = Form(...), r48: str = Form(...), r49: str = Form(...), r50: str = Form(...)):
    if pin == "Ahmad":

        content_STO_List = await STO_List_file.read()
        pref_out = out
        no_stos = len(create_stos(content_STO_List)[0].index)
        #print("# of STOs", no_stos)
        no_teams = math.floor(no_stos/2)
        #print("# of teams", no_teams)


        if int(nreg)==0:
            reg_dep_yn = False
            rel_reg_sizes = 0
        else: 
            reg_dep_yn = False # should be true
            reg_sizes = [int(r1), int(r2), int(r3), int(r4), int(r5), int(r6), int(r7), int(r8), int(r9), int(r10), int(r11), int(r12), int(r13), int(r14), int(r15), int(r16), int(r17), int(r18), int(r19), int(r20), int(r21), int(r22), int(r23), int(r24), int(r25), int(r26), int(r27), int(r28), int(r29), int(r30), int(r31), int(r32), int(r33), int(r34), int(r35), int(r36), int(r37), int(r38), int(r39), int(r40), int(r41), int(r42), int(r43), int(r44), int(r45), int(r46), int(r47), int(r48), int(r49), int(r50)]
            rel_reg_sizes = reg_sizes[0:int(nreg)]
            for xy,ind_no in zip(rel_reg_sizes,range(len(rel_reg_sizes))):
                if xy==0:
                    return "ERROR: Region #"+str(ind_no+1)+" has 0 STO teams"
            if sum(reg_sizes)!=sum(rel_reg_sizes):
                return generate_html_response3(nreg,reg_sizes)
            if no_teams != sum(rel_reg_sizes):
                if no_teams>sum(rel_reg_sizes): 
                    action="add "
                    action2="to"
                    diff=str(no_teams-sum(rel_reg_sizes))
                else: 
                    action="remove "
                    action2="from"
                    diff=str(sum(rel_reg_sizes)-no_teams)
                return str("ERROR: Invalid regional deployment. "+str(no_stos)+" STOs in master list ("+str(no_teams)+" teams). "+str(sum(rel_reg_sizes))+" team(s) inputted by user. "+action+diff+" STO teams "+action2+" regional deployment.")

        if gender=="high" and exp == "med":
            gender_weight = 0.7
            exp_weight = 0.3
        elif gender == exp:
            gender_weight = 0.6
            exp_weight = 0.4
        elif gender == "low":
            gender_weight = 0.5
            exp_weight = 0.5
        else:
            gender_weight = 0.7
            exp_weight = 0.3
    
        if age == "true":
            gender_weight = gender_weight - 0.05
            exp_weight = exp_weight - 0.05
            age_weight = 0.1
        else: age_weight = 0
        
        if priority == "Least same-gender pairs":
            p = 1
        if priority == "Diversity in nationality pairings":
            p = 2
        else:
            p = 3
        
        if time == "high":
            sample_size = 12
        else: sample_size =10

        
        sto_dep_out = sto_deployer(content_STO_List,regroup,est_time,
             sample_size, int(nreg), rel_reg_sizes, reg_dep_yn,
             p, level_3_weight, 
             level_2_weight, level_1_weight, age_weight,
             gender_weight, exp_weight, dupl_n_weight,
             sto_days_limit, lto_days_limit, ct_days_limit, 
             sto_days_min, lto_days_min, ct_days_min,
             sto_w, lto_w, ct_w, hq_w, middle_name, first_prop,
             auto_run)

        dat_sto = sto_dep_out[0]
        dat_sto_sc = sto_dep_out[1]

        file_path = str(str(os.getcwd())+"/output.xlsx")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except: print("couldn't remove file")
        print(file_path)
        if pref_out == "file":
            try:
                writer = pd.ExcelWriter(file_path,engine='xlsxwriter')
                dat_sto.to_excel(writer,index=False, sheet_name="Deployment Plan")
                dat_sto_sc.to_excel(writer,index=False, sheet_name="Performance Indicators")
                writer.save()
            except: print("Couldn't Save")
        if os.path.exists(file_path) and pref_out != "html":
            return FileResponse(file_path, media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                filename="Deployment_Plan.xlsx")
        else:
            output = dat_sto.to_html(index = False).replace('<td>', '<td align="center">').replace('<th>','<th align="center">')
            output = output.replace("<table ",
             "<table style='font-size:15%; border-collapse: collapse; table-layout: fixed' ")
            #print(output)
            return HTMLResponse(content=output, status_code=200)
    else: 
        return generate_html_response()