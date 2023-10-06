#PDF processor :
# Untuk memprocess file laporan keuangan untuk nantinya dikirim ke database
import requests
import pdfplumber
import pandas as pd
import re

def gettextinpages(pdffile,pagestart,pageend,reg):
    textfound=0
    with pdfplumber.open(pdffile) as pdf:
        while (pagestart < pageend):
            page = pdf.pages[pagestart]
            text = page.extract_text()
            for line in text.split('\n'):
                if reg.match(line):
                    #print(line)
                    textfound=1
                    break            
            if textfound==1:
                break
            else:
                pagestart = pagestart + 1

    return pagestart, pageend, line
    

def main():
    pdffile='sample.pdf'
    with pdfplumber.open(pdffile) as pdf:
        pgstart=0
        pgend=len(pdf.pages)
        print("Jumlah Halaman : ",pgend)
      
        reg_tot_liabilities = re.compile(r'^TOTAL LIABILITAS.*.TOTAL LIABILITIES')
        pgstart,pgend,txtresult = gettextinpages(pdffile,pgstart,pgend,reg_tot_liabilities)
        print("Ditemukan pada halaman ", pgstart)
        print("Text yang ditemukan ",txtresult)
        
        reg_revenue = re.compile(r'^LABA PERIODE BERJALAN.*.PROFIT FOR THE PERIOD')
        pgstart,pgend,txtresult = gettextinpages(pdffile,pgstart,pgend,reg_revenue)
        print("Ditemukan pada halaman ", pgstart)
        print("Text yang ditemukan ",txtresult)

        
        reg_revenue_parent_entity = re.compile(r'^Pemilik entitas induk.*.Owners of the parent entity')
        pgstart,pgend,txtresult = gettextinpages(pdffile,pgstart,pgend,reg_revenue_parent_entity)
        print("Ditemukan pada halaman ", pgstart)
        print("Text yang ditemukan ",txtresult)
        
        reg_cashoperation = re.compile(r'^Kas neto yang diperoleh dari.*.Net cash generated from')
         

        
      


if __name__ == '__main__':
    main()