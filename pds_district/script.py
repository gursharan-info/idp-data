import pandas as pd
import numpy as np
from requests.utils import requote_uri
from bs4 import BeautifulSoup
import requests
from urllib import request
from datetime import date

# Add, remove, or change the values according to your requirements
years = [2018,2019,2020]
data_file_path = "D:/idp_datasets/IDP_ISB/PDS/pds_dfso_monthly.csv"

state_name_codes = [
    {"name": "ANDAMAN & NICOBAR ISLANDS", "id": 35},
    {"name": "ANDHRA PRADESH","id":28},
    {"name": "ARUNACHAL PRADESH","id":12},
    {"name": "ASSAM","id":18},
    {"name": "BIHAR","id":10},
    {"name": "CHHATTISGARH","id":22},
    {"name": "DADRA & NAGAR HAVELI","id":26},
    {"name": "DAMAN & DIU","id":25},
    {"name": "DELHI","id":7},
    {"name": "GOA","id":30},
    {"name": "GUJARAT","id":24},
    {"name": "HARYANA","id":6},
    {"name": "HIMACHAL PRADESH","id":2},
    {"name": "JAMMU AND KASHMIR","id":1},
    {"name": "JHARKHAND","id":20},
    {"name": "KARNATAKA","id":29},
    {"name": "KERALA","id":32},
    {"name": "LADAKH","id":37},
    {"name": "LAKSHADWEEP","id":31},
    {"name": "MADHYA PRADESH","id":23},
    {"name": "MAHARASHTRA","id":27},
    {"name": "MANIPUR","id":14},
    {"name": "MEGHALAYA","id":17},
    {"name": "MIZORAM","id":15},
    {"name": "NAGALAND","id":13},
    {"name": "ODISHA","id":21},
    {"name": "PUNJAB","id":3},
    {"name": "RAJASTHAN","id":8},
    {"name": "SIKKIM","id":11},
    {"name": "TAMIL NADU","id":33},
    {"name": "TELANGANA","id":36},
    {"name": "TRIPURA","id":16},
    {"name": "UTTAR PRADESH","id":5},
    {"name": "UTTARAKHAND","id":9},
    {"name": "WEST BENGAL","id":19}    
]       

total_data = []
col_names = ['dfso','total_rice_allocated','total_wheat_allocated','total_qty_allocated',
                      'total_rice_distributed_unautomated','total_wheat_distributed_unautomated','total_qty_distributed_unautomated',
                      'percent_qty_distributed_unautomated','total_rice_distributed_automated','total_wheat_distributed_automated',
                      'total_qty_distributed_automated','percentage_qty_distributed_automated','total_qty_allocated_automated']
for year in years:
    for month in list(range(1,13)):
        for state in state_name_codes:
            # print(year,month)
            # print(state)
            # https://annavitran.nic.in/unautomatedStDetailMonthDFSOWiseRpt?m=1&y=2020&s=12&sn=ARUNACHAL%20PRADESH
            url = requote_uri(f"https://annavitran.nic.in/unautomatedStDetailMonthDFSOWiseRpt?m={month}&y={year}&s={str(state['id']).zfill(2)}&sn={state['name']}")
            # print(url)
            html_content = requests.get(url).content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            try:
                table_str = str(soup.select('table[id="example"]')[0])
                # print(table_str)
                df = pd.read_html(table_str)[0]
                df.columns = range(df.shape[1])
                df = df.replace("-", 0)
                df.drop(0, axis=1, inplace = True)
                # display(df)
                df.columns = col_names
                df = df.head(-1)
                df.insert(0, 'state_name', state['name'])
                df.insert(0, 'state_code', state['id'])
                df.insert(0, 'month_year',  date(year,month,1).strftime("%b-%Y"))
                
                num_cols = col_names[1:]
                df[num_cols] = pd.to_numeric(df[num_cols].stack()).unstack()
                df['total_rice_distributed'] = df['total_rice_distributed_unautomated'] + df['total_rice_distributed_automated'] 
                df['total_wheat_distributed'] = df['total_wheat_distributed_unautomated'] + df['total_wheat_distributed_automated'] 
                # display(df)
                # print(df.dtypes)
                total_data.append(df)
            except IndexError:
                pass

master_df = pd.concat(total_data).reset_index(drop=True)
master_df.to_csv(data_file_path, index=False)