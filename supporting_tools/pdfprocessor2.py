#PDF processor :
# references using pdf plumber: https://www.youtube.com/watch?v=eTz3VZmNPSE&t=186s
# check all required libraries there

import requests
import pdfplumber
import pandas as pd
import re


with pdfplumber.open('sample.pdf') as pdf:
    page = pdf.pages[7]
    text = page.extract_text()
    print(text)

reg_tot_liabilities = re.compile(r'^TOTAL LIABILITAS.*.TOTAL LIABILITIES')

for line in text.split('\n'):
    if reg_tot_liabilities.match(line):
        print(line)
    
    