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

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def get_column_value(headers,driver,txt_label,row,col,k):
     
    fin_data=[]
    for i in range (2,col+1):
        if row == 1: # Total Revenue
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div['+ str(row) +']/div['+ str(i) +']/span'
            #print('row '+ str(row) + ' ' + driver.find_element(By.XPATH,txt_col_xpath).text)                    
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
                             
        if row == 2: # Operating Revenue
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div['+ str(row) +']/div/div[1]/div['+ str(i) +']/span'
                            
            #print('row '+ str(row) + ' ' + driver.find_element(By.XPATH,txt_col_xpath).text)                    
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row >= 3 and row <= 5 :# Cost Of Revenue 10 Operating Income
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
                          
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row == 6:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'  #6 - Selling General and administrative
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        if row == 7:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        if row==8:    
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text) 
            
        if row == 9:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row == 10: #Other Operating Expenses
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[2]/div[1]/div['+ str(i) +']'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)   
        if row == 11: #Operating Income
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[5]/div[1]/div['+ str(i) +']/span' 
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text) 
        if row == 12: #Net Non Operating Interest Income Expense
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text) 
        if row == 13: #Interest Income Non Operating
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'  
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)                  
        if row == 14:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row == 15:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[3]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row == 16:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[7]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row==17:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[8]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row==18:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[8]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row==19:  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row==20:  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row==21:  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row==22:  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row==23:  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if row==24:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[10]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)

        if row>=25 and row <=46:
             txt_col_xpath= '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div['+ str(row-14) +']/div[1]/div['+ str(i) +']'
             fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
             
    return headers,fin_data
   


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
    

    
    
    url='https://finance.yahoo.com/quote/SIDO.JK/financials?p=SIDO.JK'
    driver = webdriver.Edge(service = service, options = options)
    driver.get(url)
    

    link_stock_header = driver.find_element(By.XPATH,'//*[@id="quote-header-info"]/div[2]/div[1]/div[1]/h1')
    if link_stock_header is not None:
        print("Stock Name :", link_stock_header.text)
        
    txt_income_statement = driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/h3/span')
    print("asdada : ", txt_income_statement.text)
    
    txt_price=driver.find_element(By.XPATH,'//*[@id="quote-header-info"]/div[3]/div[1]/div')
    
    txt_prices= txt_price.text.split("\n")
    print("pandjang text ", len(txt_prices))
    txtpricenchange = txt_prices[0].split(" ")
    
    txt_price = txtpricenchange[0]
    print("txt price  : ", txtpricenchange[0])
    
    txt_price_change=txtpricenchange[1].replace("(","").replace(")","")
    print("txt price Change : ", txt_price_change)
    
    print("txt price line 2 : ", txt_prices[1])
    
    # //*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[1]/span
    # //*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[2]/span
    
    #Default Annual are openned
    #Quarterly clickable, Expandall clickable
    driver.refresh()
    
    driver.implicitly_wait(4)
    #click quarterly
    driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button/div').click()
    
    #click expandall 
    driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div').click()

    
    driver.implicitly_wait(2)
    
    # To get the number of rows
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    row_element_xpath ='//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div'
    row_element = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, row_element_xpath))) 
    if row_element is not None:
        row=driver.find_elements(By.XPATH,row_element_xpath)
    
    txt_label=[]
    for i in range (1, len(row)+1):
        row_element_xpath ='//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div['+ str(i) +']/div[1]/div[1]/div[1]/span'
        row_element = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, row_element_xpath))) 
        if row_element is not None:
            #print("isi " + str(i) + " "+ driver.find_element(By.XPATH,row_element_xpath).text)
            txt_label.append(driver.find_element(By.XPATH,row_element_xpath).text)
            
            if i == 1: # Total Revenue
                row_element_xpath='//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]/span'
                #print("isi " + str(i) + " Child - "+ driver.find_element(By.XPATH,row_element_xpath).text)
                txt_label.append(driver.find_element(By.XPATH,row_element_xpath).text)
                 
            if i == 4: #Operating Expense, it has child so needs to define here
                row_elements_xpath=[]
                
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[2]/div[1]/div[1]/div[1]/span')
                
                for txt_xpath in row_elements_xpath :
                     #print("isi " + str(i) + " Child - "+ driver.find_element(By.XPATH,txt_xpath).text)
                     txt_label.append(driver.find_element(By.XPATH,txt_xpath).text)
                
                row_elements_xpath.clear
            
            if i == 6: #Net Non Operating Interest Income Expense
                row_elements_xpath=[]
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[1]/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[2]/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[3]/div[1]/div[1]/div[1]/span')
                 
                for txt_xpath in row_elements_xpath :
                     #print("isi " + str(i) + " Child - "+ driver.find_element(By.XPATH,txt_xpath).text)
                     txt_label.append(driver.find_element(By.XPATH,txt_xpath).text)
                
                row_elements_xpath.clear

            if i == 9: #Net Income
                row_elements_xpath=[]
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/span')
                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[2]/div[1]/div[1]/div[1]/span') 
                for txt_xpath in row_elements_xpath :
                    #print("isi " + str(i) + " Child - "+ driver.find_element(By.XPATH,txt_xpath).text)
                    txt_label.append(driver.find_element(By.XPATH,txt_xpath).text)
                     
                row_elements_xpath.clear
    
    
    # fill column nya
    
    driver.implicitly_wait(2)
    #get the table headers
    headers=[]
    headers.append(driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[2]/span').text)
    headers.append(driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[3]/span').text)
    headers.append(driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[4]/span').text)
    headers.append(driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[5]/span').text)
    headers.append(driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[6]/span').text)
    headers.append(driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[7]/span').text)
    
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    col_elements_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div[1]/div'
    col_elements = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, col_elements_xpath))) 
    if col_elements is not None:
        colnum=driver.find_elements(By.XPATH,col_elements_xpath)
        print("Jumlah Kolom ",len(colnum))
        col=len(colnum)
   
    t=0 
    actual_row=1
    k=11            
    for txt_lbl in txt_label :
        print("key :"+ str(actual_row) +' - '+ txt_lbl +' '+ str(k) )
        fin_data=[]
        headers, fin_data = get_column_value(headers,driver,txt_lbl,actual_row,col,k)
        
        if actual_row>25:
            k=k+1
        
        cnt_fin_data = len(fin_data)
        if cnt_fin_data > 0 :
            for x in range(cnt_fin_data) :
                print("" + headers[x] +" - "+fin_data[x] )
                t=t+1
        actual_row=actual_row+1
                
    
    
    # row_after_head=driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/section/div[3]/div[1]/div/div[2]/div[1]/div[1]')
    # print("row after_head",len(row_after_head))
    
    # txt_breakdown = driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[1]/span')
    # txt_ttm = driver.find_element(By.XPATH, '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div[2]/span')
    
    driver.quit()

if __name__ == "__main__":
    main()

