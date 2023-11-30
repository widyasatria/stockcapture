
import requests
import pdfplumber
from pdfminer.high_level import extract_text
import pandas as pd
import re
import sys, os, shutil, logging
from shutil import Error


def getreldate(text,matchesQ2,matchesQ3):
    txtreldate=""
    quarter="" 
    year=""
    
    if matchesQ2 >=0 :
        k=matchesQ2
        quarter='Q2'
        #print("text yang ditangkap : "+ text)
        
        for x in text:
            txtreldate=txtreldate+text[k]
            if (k-matchesQ2) == 11 : 
                break
            else:
                k=k+1
        year = txtreldate[-4:]
        
    if matchesQ3 >=0 :
        k=matchesQ3
        quarter='Q3'
        #print("text yang ditangkap : "+ text)
        for x in text:
            txtreldate=txtreldate+text[k]
            if (k-matchesQ3) == 16 : 
                break
            else:
                k=k+1
        
        year = txtreldate[-4:]
        
                
    return txtreldate, quarter, year
                                        
def gettextinpages(pdffile,pagestart,pageend,reg):
    textfound=0
    strfound=''
    with pdfplumber.open(pdffile) as pdf:
        while (pagestart < pageend):
            page = pdf.pages[pagestart]
            text = page.extract_text()
            for line in text.split('\n'):
                if reg.match(line):
                    #print(line)
                    textfound=1
                    strfound=line
                    break
            if textfound==1:
                break
            else:
                pagestart = pagestart + 1
                strfound=''
            
    return pagestart, pageend, strfound
    
def main():
    
    #pdffile='finance_pdf/sample.pdf'
    
    successfolder = os.path.join("finance_pdf", "success")
    successfolder = "./finance_pdf/success/" # hilangkan./ jika dimasukkan ke job
    #for root, dirs, files in os.walk('finance_pdf'):
    finance_dir="./finance_pdf"
    dirlist = os.listdir(finance_dir)
    #print(dirlist)
    for file in dirlist:
        #for file in files:
            #print(file)
            if file.endswith('.pdf') and os.path.isfile(os.path.join(finance_dir, file)):
                pdffile = finance_dir+"/"+file
               
                print("Lokasi file ", pdffile)
                #pdffile = os.path.join(root, file)
             
                try:
                    with pdfplumber.open(pdffile) as pdf:
                        pgstart=0
                        pgend=len(pdf.pages)
                        print("Jumlah Halaman : ",pgend)
                        
                        reg_company = re.compile(r'^PT.*.Tbk$')
                        pgstart,pgend,txtcompany = gettextinpages(pdffile,pgstart,pgend,reg_company)
                        print("Ditemukan pada halaman ", pgstart)
                        print("Text yang ditemukan ",txtcompany)
                        txtcompany=txtcompany.replace(" ", "_")
                        print("Text yang ditemukan after processing ",txtcompany)
                        
                        
                    
                        # reg_Q2_release_datev1 = re.compile(r'^30 JUNI.*\d+$')
                        # pgstart,pgend,txtreleasedate = gettextinpages(pdffile,pgstart,pgend,reg_Q2_release_datev1)
                        # print("compileresult ",reg_Q2_release_datev1)
                        
                        # if (reg_Q3_release_datev1):
                        #     pgstart,pgend,txtreleasedate = gettextinpages(pdffile,pgstart,pgend,reg_Q3_release_datev1)
                        # reg_Q3_release_datev2 = re.compile(r'^30 September\d+$')
                        # if (reg_Q3_release_datev2):
                        #     pgstart,pgend,txtreleasedate = gettextinpages(pdffile,pgstart,pgend,reg_Q3_release_datev2)
                            
                        # reg_Q2_release_datev1 = re.compile(r'^30 JUNI\d+$')
                        # if (reg_Q2_release_datev1):
                        #     pgstart,pgend,txtreleasedate = gettextinpages(pdffile,pgstart,pgend,reg_Q3_release_datev1)
                        # reg_Q2_release_datev2 = re.compile(r'^30 Juni\d+$')
                        # if (reg_Q2_release_datev2):
                        #     pgstart,pgend,txtreleasedate = gettextinpages(pdffile,pgstart,pgend,reg_Q2_release_datev2)
                        
                        # print("Ditemukan Release Date pada halaman ", pgstart)
                        # print("Text yang ditemukan ",reg_Q2_release_datev1) 
                        
                        # txtreleasedate=txtreleasedate.replace(" ", "_")
                        # txtreleasedate="_"+txtreleasedate
                       
                        # print("Text yang ditemukan after processing ",txtreleasedate)
                        
                       
                    
                        reg_tot_liabilities = re.compile(r'^.*.TOTAL LIABILITIES')
                        pgstart,pgend,txtresult = gettextinpages(pdffile,pgstart,pgend,reg_tot_liabilities)
                        
                        print("Ditemukan pada halaman ", pgstart)
                        print("Text yang ditemukan ",txtresult)
                        
                        pg_revenue_st = pgstart
                        pg_revenue_end = pgend
                        
                        reg_revenue = re.compile(r'^.*.PROFIT FOR THE PERIOD')
                        pgstart,pgend,txtresult = gettextinpages(pdffile,pgstart,pgend,reg_revenue)
                        if txtresult == '' :
                            reg_revenue = re.compile(r'^.*.PROFIT FOR.*?')
                            pgstart,pgend,txtresult = gettextinpages(pdffile,pg_revenue_st,pg_revenue_end,reg_revenue)
                        
                        print("Ditemukan pada halaman ", pgstart)
                        print("Text yang ditemukan ",txtresult)

                            
                        reg_revenue_parent_entity = re.compile(r'^.*.Owners of the parent entity')
                        pgstart,pgend,txtresult = gettextinpages(pdffile,pgstart,pgend,reg_revenue_parent_entity)
                        print("Ditemukan pada halaman ", pgstart)
                        print("Text yang ditemukan ",txtresult)
                        
                        reg_cashoperation = re.compile(r'^.*.Net cash generated from')
                    
                        
                        page1 = pdf.pages[0]
                        page1_text = page1.extract_text().split('\n')
                        print(page1_text)
                        matchesQ2=-1
                        matchesQ3=-1
                        for text in page1_text:
                            print(text)
                            matchesQ2 = text.find("30 Juni")
                            matchesQ3 = text.find("30 September")
                            if matchesQ2 >=0 or matchesQ3 >= 0 :
                                print ("hasil matches ", matchesQ2)
                                txtreldate, quarter, year = getreldate(text,matchesQ2,matchesQ3)
                                break
                            
                        print("Tanggal release dokumen :", txtreldate)
                        print("Tanggal Quarter dokumen :", quarter)
                        print("Tanggal year dokumen :", year)
                            
                            #print(matchesQ2)
                        #pgstart,pgend,txtreldate = gettextinpages(pdffile,pgstart,pgend,reg_reldate)
                        # pgstart,pgend,txtreldate = gettextinpages(pdffile,pgstart,pgend,reg_reldate)
                        # print("Financial Release Date ditemukan pada halaman ", pgstart)
                        # print("Text yang ditemukan "+txtreldate)
                        
                    
                    
                    
                    
                    # try: 
                     
                    #     shutil.move(pdffile, successfolder+'samplu.pdf',copy_function="copy2") 
                    # except Error as err:
                    #     #print("setelah move : ", err.args[0])
                    #     pass
                  
                except shutil.Error:
                    pass
                

if __name__ == '__main__':
    main()