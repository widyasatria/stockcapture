#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

# FILE INI SUDAH TIDAK BISA DI RUN LANGSUNG HARUS DIPANGGIL OLEH ../yahoo_data_scheduler.py

import os
from selenium import webdriver
#pip install msedge-selenium-tools

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

import MySQLdb
from decimal import Decimal

# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


debug = True

def get_column_value(headers,driver,txt_label,row,col,k):
     
    fin_data=[]
    for i in range (2,col+1):
        
            # get the parent row
        # txt_parent_row_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div['+str(k)+']/div[1]/div[1]/div[1]/span' 
        # txt_parent_res = driver.find_element(By.XPATH,txt_parent_row_xpath).text.strip()
        # print("txt_parent_res "+txt_parent_res +"vs"+ txt_label)
        # if txt_parent_res == txt_label:
        #     txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div[1]/div['+ str(i) +']/span'
        #     fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        #     if debug == True :
        #         print('masuk ke autotxt parent row ' + txt_label + " - " + driver.find_element(By.XPATH,txt_col_xpath).text) 
        
        
        if txt_label == 'Total Revenue':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div['+ str(row) +']/div['+ str(i) +']/span'
            if debug == True :
                print('row '+ str(row) + ' ' + driver.find_element(By.XPATH,txt_col_xpath).text)                    
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
                             
        if txt_label == 'Operating Revenue': # Operating Revenue
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div['+ str(row) +']/div/div[1]/div['+ str(i) +']/span'
            if debug == True :
                print('row '+ str(row) + ' ' + driver.find_element(By.XPATH,txt_col_xpath).text)                    
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        
        if txt_label == 'Cost of Revenue':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        if txt_label == 'Gross Profit':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[3]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        if txt_label == 'Operating Expense':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
                 
        if txt_label == 'Selling General and Administrative':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'  #6 - Selling General and administrative
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        if txt_label == 'General & Administrative Expense': #row == 7:
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        if txt_label == 'Rental & Landing Fees':  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text) 
            
        #if row == 9: 
        if txt_label == 'Other Operating Expenses':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[2]/div[1]/div['+ str(i) +']'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
            
        if txt_label == 'Selling & Marketing Expense':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
                        
        if txt_label == 'Operating Income':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[5]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
            
           

        if txt_label == 'Net Non Operating Interest Income Expense': #Net Non Operating Interest Income Expense
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text) 
        if txt_label == 'Interest Income Non Operating': #Interest Income Non Operating
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'  
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)                  
        if txt_label == 'Interest Expense Non Operating':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Total Other Finance Cost':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[2]/div[3]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Pretax Income':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[7]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Tax Provision':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[8]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Net Income Common Stockholders':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[8]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Net Income':  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Net Income Including Non-Controlling Interests':  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[1]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Net Income Continuous Operations':  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Minority Interests':  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[1]/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Otherunder Preferred Stock Dividend':  
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[9]/div[2]/div[2]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        if txt_label == 'Diluted NI Available to Com Stockholders':
            txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[10]/div[1]/div['+ str(i) +']/span'
            fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        
        
        if row>=24 and row <=46:
             txt_col_xpath= '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div['+ str(k) +']/div[1]/div['+ str(i) +']'
             fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        
        
        
        # if txt_label == 'Basic EPS':
        #     txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[11]/div[1]/div['+ str(i) +']'
        #     fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
   
        # if txt_label == 'Diluted EPS': 
        #     txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[12]/div[1]/div['+ str(i) +']'
                            
        #     fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        # if txt_label == 'Basic Average Shares': 
        #     txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[13]/div[1]/div['+ str(i) +']/span'
        #     fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        # if txt_label == 'Diluted Average Shares': 
        #     txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[14]/div[1]/div['+ str(i) +']/span'
        #     fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)
        
        # if txt_label == 'Total Operating Income as Reported': 
        #     txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[15]/div[1]/div['+ str(i) +']/span'
        #     fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)    
        
        # if txt_label == 'Rent Expense Supplemental': 
        #     txt_col_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[16]/div[1]/div['+ str(i) +']/span'
        #     fin_data.append(driver.find_element(By.XPATH,txt_col_xpath).text)   
        
    
            

        
        
             
    return headers,fin_data
   


def inc_stat_quarter():
    
    
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
    
    
    conn = MySQLdb.connect(
    host="localhost",
    user="root",
    password="password",
    database="db_api",
    auth_plugin='mysql_native_password'
    )
    
    cursor = conn.cursor()
    try:
    
        cursor.execute("SELECT ticker FROM stocks")
        result = cursor.fetchall()  
    
        if result is not None:      
            for x in result:
                if debug == True :
                    print('https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK')
            
                url='https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK'
            
                txt_ticker = x[0]
                driver = webdriver.Edge(service = service, options = options)
                driver.get(url)

                
                #Default Annual are openned
                #Quarterly clickable, Expandall clickable
                driver.refresh()
                
                driver.implicitly_wait(4)
                #click quarterly
                driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button/div').click()
                
                #click expandall 
                driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div').click()

                
                driver.implicitly_wait(4)
                
                
                # To get the number of rows
                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                row_element_xpath ='//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div'
                                    
                row_element = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, row_element_xpath))) 
                if row_element is not None:
                    row=driver.find_elements(By.XPATH,row_element_xpath)
                    if debug == True :
                        print("jumlah row ", len(row))
                        
                row_element_css_noparent = '#Col1-1-Financials-Proxy > section > div.Pos\(r\) > div.W\(100\%\).Whs\(nw\).Ovx\(a\).BdT.Bdtc\(\$seperatorColor\) > div > div.D\(tbrg\) > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div.D\(tbr\).fi-row.Bgc\(\$hoverBgColor\)\:h'
                # row_element_xpath_noparent ='/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[3]/div[1]/div/div[2]' 
                                              # //*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div/div[2]/div
                                               
                                               #/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div/div[2]/div/div[1]
                #                             #  //*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div
                #                             # /html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[3]/div[1]/div/div[2]/div[1]/div[1]/div[1]
                #                             # /html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[3]/div[1]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]
                #                             #/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[3]/div[1]/div/div[2]/div[1]/div[2]/div/div[1]
                #                             #/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[3]/div[1]/div/div[2]/div[1]/div[1]
                #                             #/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/section/div[3]/div[1]/div/div[2]/div[2]/div[1]
                # row_element_noparent = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, row_element_xpath_noparent))) 
                # if row_element_noparent is not None:
                #     row_noparent=driver.find_elements(By.XPATH,row_element_xpath_noparent)
                #     if debug == True :
                #         print("jumlah row ", len(row_noparent))
                
                txt_label=[]
                for i in range (1, len(row)+1):
                    row_element_xpath ='//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div['+ str(i) +']/div[1]/div[1]/div[1]/span'
                    row_element = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, row_element_xpath))) 
                    if row_element is not None:
                        print("isi " + str(i) + " "+ driver.find_element(By.XPATH,row_element_xpath).text)
                        txt_label.append(driver.find_element(By.XPATH,row_element_xpath).text)
                        
                        if i == 1: # Total Revenue
                            row_element_xpath='//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]/span'
                                              
                            #print("isi " + str(i) + " Child - "+ driver.find_element(By.XPATH,row_element_xpath).text)
                            txt_label.append(driver.find_element(By.XPATH,row_element_xpath).text)
                            
                        if i == 4: #Operating Expense, it has child so needs to define here
                            
                            
                            row_elements_xpath=[]
                            
                            # seling general and administrative 
                            row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[1]/div[1]/div[1]/span')
                            # General & Administrative Expense
                            row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/span')
                            # Rental & Landing Fees                           
                            row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]/span')
                                                      
                            
                            #Selling & Marketing Expense Kadang tidak ada di beberapa lap keu, jika ada di tambah otherwise di skipp
                            if len(driver.find_elements(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/span')) > 0:
                                row_elements_xpath.append('//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/span')
                            
                            
                            #Other Operating Expenses                                                     
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

                        if i == 9: #Net Income Common Stockholders
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
                
                driver.implicitly_wait(4)
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
                    if debug == True :
                        print("Jumlah Kolom ",len(colnum))
                    col=len(colnum)
            
                #t=0 
                actual_row=1
                k=11  #parent_row_num          
                for txt_lbl in txt_label :
                    if debug == True :
                        print("key :"+ str(actual_row) +' - '+ txt_lbl +' tabel row '+ str(k) )
                    fin_data=[]
                    headers, fin_data = get_column_value(headers,driver,txt_lbl,actual_row,col,k)
                    if actual_row>=24:
                     k=k+1
                    
                    cnt_fin_data = len(fin_data)
                    if cnt_fin_data > 0 :
                        for x in range(cnt_fin_data) :
                            if debug == True :
                                print("" + headers[x] +" - "+fin_data[x] )
                    actual_row=actual_row+1
      
    
    except MySQLdb.Error as ex:
        try:
            print  (f"MySQL Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            return None
        except IndexError:
            print (f"MySQL Error: %s",str(ex))
            return None
    except MySQLdb.OperationalError as ex:
        print(ex)
        return None
    except TypeError as ex:
        print(ex)
        return None
    except ValueError as ex:
        print(ex)
        return None
    finally:
        conn.close
        driver.quit()
# if __name__ == "__main__":
#     main()

