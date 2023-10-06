# references using pdfminer https://www.youtube.com/watch?v=w2r2Bg42UPY

import re
from pdfminer.high_level import extract_pages, extract_text

#for page_layout in extract_pages("sample.pdf"):
#    for element in page_layout:
#        print(element)
        

text = extract_text("sample.pdf")
print(text)