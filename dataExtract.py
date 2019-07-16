# -*- coding: utf-8 -*-
"""
Created on Fri May 31 19:14:53 2019

@author: Umit
"""

# Import packages
import numpy  as np
import pandas as pd
import xlrd
import os
from shutil import copyfile

# Define input/output files 
setupPath  = 'c:\\his-data-extract'
setupFile  = 'concept.xlsx'
outputFile = 'concept2.xlsx'
os.chdir(setupPath)

#Import his functions
import hisFunctions
read_his    = hisFunctions.read_his
read_hishia = hisFunctions.read_hishia
write_his   = hisFunctions.write_his

#Import appendToExcel function
import appendToExcel
append_df_to_excel = appendToExcel.append_df_to_excel

#Open the setupFile
wb = xlrd.open_workbook(setupFile)
sheet = wb.sheet_by_name("SETUP")  
ribasimPath = sheet.cell(1,1)
projectName = sheet.cell(2,1)
caseNum     = sheet.cell(3,1)

#Define a data table of his files, parameters, location, and tab names 
sheet2 = wb.sheet_by_name("RIBASIM_OUT")  
hisNamesList = []
parNamesList = []
locNamesList = []
tabNamesList = []

for i in range(sheet2.nrows): 
    if i !=0:
        hisNamesList.append(sheet2.cell_value(i, 1)) 
        parNamesList.append(sheet2.cell_value(i, 2)) 
        locNamesList.append(sheet2.cell_value(i, 4)) 
        tabNamesList.append(sheet2.cell_value(i, 5)) 

ribasimDat = pd.DataFrame({'hisName': hisNamesList, 'parName': parNamesList,
     'locName': locNamesList, 'tabName': tabNamesList})

#Get unique his names from ribasimDat  
hisNamesUnique = ribasimDat.hisName.unique()

#Dublicate the setup file
copyfile(setupFile, outputFile)

# Data extraction: loop through his files
for i in range(len(hisNamesUnique)): 
 
    #Read the current his file  
    hisCurrent = hisNamesUnique[i]
    hisPath = ribasimPath.value + "\\" + projectName.value + "\\" + str(round(caseNum.value)) + "\\" + hisCurrent
    hisObject = read_his(hisPath)

    #Find the list of parameters in the current his file    
    subset1 = ribasimDat[ribasimDat['hisName'] == hisCurrent]
    parAll  = subset1['parName'].unique()
    
    #Loop through each parameter in the current his file
    for k in range(len(parAll)): 
        
        #Current parameter and short name(20 chars)
        parCurrent = parAll[k]
        parCurrent2 = parCurrent[:20]
        parIndex = hisObject[0].index(parCurrent2) 
        
        #Desired locations & tabnames for the current parameter
        subset2 = ribasimDat[ribasimDat['parName'] == parCurrent]
        locNamesCurrent = subset2['locName'].values.tolist()
        tabCurrent = subset2['tabName'].iloc[0]

        #Define dataframe from hisObject
        xyz = []
        for s in range(len(locNamesCurrent)):
            xyz.append(hisObject[1].index(locNamesCurrent[s]))
        data = pd.DataFrame(hisObject[3][parIndex,:,:])
        data = data.loc[:, xyz]
        data.columns = locNamesCurrent # Location names
        data.index = hisObject[2]   # date
        
        #Append the extracted data to the output excel workbook
        append_df_to_excel(outputFile, data, sheet_name=tabCurrent, index=True)


