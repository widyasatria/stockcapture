#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

import os
from selenium import webdriver
#pip install msedge-selenium-tools

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

def main():
    
    #requirement selenium versi 4.13.0
    #ms edge webdriver : https://msedgedriver.azureedge.net/119.0.2151.72/edgedriver_win64.zip
    
    # parameter executable_path ini sudah tidak di bisa di pakai di selenium versi 4, caranya ketik di command prompt echo %Path% untuk mengetahui existing environment variable
    # kemudian copy msedge webdriver ke salah satu path yang terdaftar.
    
    # driver = webdriver.Edge(executable_path=r'C:\Users\wardians\stockcapture\msedgedriver.exe')
    # references : https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/ie-mode?tabs=python
    
    options = Options()
    options.use_chromium=True
    options.add_argument("headless")
    options
    service = Service(verbose = False)
    debug = True

    
    
    url='https://finance.yahoo.com/quote/SIDO.JK/financials?p=SIDO.JK'
    driver = webdriver.Edge(service = service, options = options)
    driver.get(url)
    

    link_stock_header = driver.find_element(By.XPATH,'//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1')
    if link_stock_header is not None:
        if debug == True :
            print("Stock Name :", link_stock_header.text)
        
    txt_income_statement = driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/h3/span')
    if debug == True :
        print("txt_income : ", txt_income_statement.text)
    
    txt_price=driver.find_element(By.XPATH,'//*[@id="quote-header-info"]/div[3]/div[1]/div')
    
    txt_prices= txt_price.text.split("\n")
    if debug == True :    
        print("pandjang text ", len(txt_prices))
    txtpricenchange = txt_prices[0].split(" ")
    
    txt_price = txtpricenchange[0]
    if debug == True :
        print("txt price  : ", txtpricenchange[0])
    
    txt_price_change=txtpricenchange[1].replace("(","").replace(")","")
    if debug == True :
        print("txt price Change : ", txt_price_change)
        print("txt price line 2 : ", txt_prices[1])

if __name__ == "__main__":
    main()