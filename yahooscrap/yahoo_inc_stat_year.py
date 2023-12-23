#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

# FILE INI SUDAH TIDAK BISA DI RUN LANGSUNG HARUS DIPANGGIL OLEH ../yahoo_data_scheduler.py

import os, time
from selenium import webdriver
#pip install msedge-selenium-tools

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

import MySQLdb
from datetime import datetime
from decimal import Decimal
# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


debug = True

def upd_stock_last_modify(conn,txt_ticker):
    cursor = conn.cursor()
    qry="update stocks set stock_fin_inc_stat_year = now() where ticker= %s "
    cursor.execute(qry,(txt_ticker,))
    conn.commit()
    

def inc_stat_annual():
    
    
    #requirement selenium versi 4.13.0
    #ms edge webdriver : https://msedgedriver.azureedge.net/119.0.2151.72/edgedriver_win64.zip
    
    # parameter executable_path ini sudah tidak di bisa di pakai di selenium versi 4, caranya ketik di command prompt echo %Path% untuk mengetahui existing environment variable
    # kemudian copy msedge webdriver ke salah satu path yang terdaftar.
    
    # driver = webdriver.Edge(executable_path=r'C:\Users\wardians\stockcapture\msedgedriver.exe')
    # references : https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/ie-mode?tabs=python
    
    options = Options()
    options.use_chromium=True
    options.add_argument("headless")
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
    
        cursor.execute("SELECT ticker FROM stocks order by stock_fin_inc_stat_year")
        result = cursor.fetchall()  
    
        if result is not None:      
            for x in result:
                if debug == True :
                    print('https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK')
            
                url='https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK'
                txt_ticker = x[0]
                
                
                driver = webdriver.Edge(service = service, options = options)
                driver.get(url)

                time.sleep(3)
                #Default Annual are openned
                #Quarterly clickable, Expandall clickable
              
                driver.implicitly_wait(4)
                
                # do not click quarterly so disable this line below
                #driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button/div').click()
                
                driver.implicitly_wait(4)
                #click expandall 
                driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div').click()

                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
              
                driver.implicitly_wait(4)
                # to get the headers
                           
                txt_headers_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[1]/div/div'
                col_headers = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, txt_headers_xpath))) 
                
                if col_headers is not None:
                    time.sleep(1)
                    driver.implicitly_wait(4)
                    txt_tblheaders = driver.find_elements(By.XPATH,txt_headers_xpath)
                   
                    if debug == True:
                        print('panjang headers ', len(txt_tblheaders))
                    
                    col_length = len(txt_tblheaders)
                    
                    for txt_header in txt_tblheaders:
                        print(txt_header.text)
                
                driver.implicitly_wait(4)
                
          
               
                txt_all_data_css = 'rw-expnded'
                all_datas = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, txt_all_data_css))) 
                
                print("getting financial data from ... "+ url)
                
                if all_datas is not None:
                    driver.implicitly_wait(4)
                    txt_tbody = driver.find_elements(By.CLASS_NAME,txt_all_data_css)
                    driver.implicitly_wait(4)
                             
                    if debug==True:
                        print(" Panjang rw-expanded ", len(txt_tbody))
                    k=1
                    for txt_labels in txt_tbody:
                        time.sleep(1)
                        #row_datas=txt_labels.find_elements(By.TAG_NAME,'span')
                        # search data using DIV  not using span -- new version
                        row_datas=txt_labels.find_elements(By.TAG_NAME,'div')
                        
                        driver.implicitly_wait(4)
                        if debug==True:
                            print("=== ROW ke "+ str(k) + " Panjang div row data "+ str(len(row_datas)) )
                        
                        time.sleep(0.5)
                       
                        cnt=1
                        col_header=1 # col_header 0= breakdown, col_header 1 dst isi tanggal
                        for txt_data in row_datas:
                            #Hanya array 1 yang punya data lengkap
                            # if cnt == 1:
                            #     if debug == True:
                            #         print ("txt_data.text isi "+ txt_data.text+ " CNT " +str(cnt))
                           
                            if cnt == 2:
                                txt_breakdown = txt_data.text
                            
                            # array data disimpan di array no 5-8 hardcoded
                            # data disimpan mulai di array no 5, kemudian iterate terus sampai 5+ (panjang kolom-1) karena panjang kolom array (mulai dari 0-)
                            # untuk inc_stat_year
                            if cnt >=5 and cnt<=(5+(col_length-2)):
                                if debug == True:
                                    print("== txt_tickers : "+ txt_ticker +" - txt_breakdown: - "+ txt_breakdown + " - txt_data "+ txt_data.text + " - header " + txt_tblheaders[col_header].text + " - counter "+ str(cnt) + " - colheader "+ str(col_header) + " - colheader+1 "+ str(col_header+1) ) 
                                    print("Ada karakter k? : ", txt_data.text.find("k"))
                                #cleansing data
                                
                                if txt_data.text.find("k")>0:
                                    txt_value = txt_data.text
                                    txt_value = txt_value.replace("k","")
                                    txt_value = Decimal(txt_value) * 1000 
                                else:
                                    txt_value = txt_data.text.replace(",","")
                                    txt_value = txt_value.replace(".","")
                                    if txt_value == '-' :
                                        txt_value = 0
                                    
                       
                                    
                                # if debug == True:
                                #     print("=== print text header before: "+ txt_tblheaders[col_header].text)
                                
                                # Hanya diinsert jika bukan TTM
                                if txt_tblheaders[col_header].text != 'TTM':
                                    arr_header =  txt_tblheaders[col_header].text.split("/")
                                    if len(arr_header)>2 :
                                        lbl_header = arr_header[2]+"-"+arr_header[0]+"-"+arr_header[1]
                                    arg1 = [txt_ticker, txt_breakdown, txt_value ,lbl_header, txt_tblheaders[col_header].text, col_header+1]
                                    cursor.callproc('stock_fin_inc_stat_year_upsert',arg1)
                                
                                
                                # if debug == True:
                                #     print("=== print text header after : "+ lbl_header)
                                
                                col_header=col_header+1 
                                time.sleep(0.5)
                            if cnt==(5+(col_length-2)): # break loop jika data yang ada didalamnya sudah habis berdasarkan jumlah column  
                                break
                            
                            cnt=cnt+1
                      
                        k=k+1
                upd_stock_last_modify(conn,txt_ticker)
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

