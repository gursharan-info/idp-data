import re
import camelot
import pandas as pd
import numpy as np


start_column_names = ['center','labour_category','labour_type','gender','july','august','september','october','november','december','january',
              'february','march','april','may','june','annual_average']


def parse_wages_pdf(filepath, start_page, end_page, column_names):
    year_regex = re.compile('[a-zA-Z]')
    year = year_regex.sub('', filepath.split("/")[-1].split(".")[0])
    
    pages_to_extract = list(range(start_page, end_page+1))
    
    all_pages = []
    for page in pages_to_extract:
        table = camelot.read_pdf(filepath, pages=str(page))
        df = table[0].df.copy()

        df = df.iloc[1:]   # Remove titles
        df = df[~df[0].str.contains("Table")].reset_index(drop=True)  #Remove Table number
        df.columns = start_column_names
        df.insert(0, 'district', np.nan)
        df.insert(0, 'state', np.nan)

#         display(df)
        all_pages.append(df)
        
    all_pages_df = pd.concat(all_pages).reset_index(drop=True)
    state_idx = all_pages_df.index[all_pages_df['center'].str.lower().str.contains('state')].tolist()
    
    for sidx in state_idx:
        state = all_pages_df['center'].iloc[sidx].split(":")[1].strip()
        all_pages_df.loc[sidx+2, 'state'] = state
    all_pages_df = all_pages_df.drop(all_pages_df.index[state_idx], axis='index').reset_index(drop=True)
    
    dist_idx = all_pages_df.index[all_pages_df['center'].str.lower().str.contains('district')].tolist()
    for idx in dist_idx:
        idx = idx+1
        if idx:
            dist = all_pages_df['center'].iloc[idx-1].split(":")[1].strip()
            all_pages_df.loc[idx, 'district'] = dist
    all_pages_df = all_pages_df.drop(all_pages_df.index[dist_idx], axis='index').reset_index(drop=True)
    
    all_pages_df['center'] = all_pages_df['center'].str.replace('center','',case=False)
    all_pages_df['center'] = all_pages_df['center'].str.replace(':','').str.strip()
    all_pages_df = all_pages_df.replace('', np.nan)
    all_pages_df = all_pages_df.replace('\n',' ', regex=True)
    all_pages_df['year'] = year
    
    all_pages_df[['state_name','district_name','center',
                  'labour_category','labour_type']] = all_pages_df[['state_name','district_name','center',
                                                                    'labour_category','labour_type']
                                                                ].fillna(method='ffill')
    all_pages_df = all_pages_df.replace('-', np.nan)
    all_pages_df[['labour_category','labour_type']] = all_pages_df[['labour_category','labour_type']].replace('\s+', ' ', regex=True)
    all_pages_df[['state_name','district_name']] = all_pages_df[['state_name','district_name']].replace('\s+', ' ', regex=True)
    
    data_file = f"{filepath.split('.')[0]}.csv"
    all_pages_df.to_csv(data_file, index=False) 


''' Change the path of each source file as required below and the starting and ending page number those have the tables. Each of the scraping call below would create a seperate csv file for each pdf which is to be parsed. Please note that the pdf filename should include the year range as "2010-11" as the value for year column would be extracted from the filename itself. 
'''

parse_wages_pdf("D:/agriculture_wages/AgriWages2010-11.pdf", 15,169,start_column_names)
parse_wages_pdf("D:/agriculture_wages/AgriWages2011-12.pdf", 16,186,start_column_names)
parse_wages_pdf("D:/agriculture_wages/AgriWages2012-13.pdf", 16,166,start_column_names)
parse_wages_pdf("D:/agriculture_wages/AgriWages2013-14.pdf", 15,169,start_column_names)
parse_wages_pdf("D:/agriculture_wages/AgriWages2014-15.pdf", 17,211,start_column_names)
parse_wages_pdf("D:/agriculture_wages/AgriWages2015-16.pdf", 17,220,start_column_names)
parse_wages_pdf("D:/agriculture_wages/AgriWages2016-17.pdf", 33,250,start_column_names)
parse_wages_pdf("D:/agriculture_wages/AgriWages2017-18.pdf", 33,325,start_column_names)