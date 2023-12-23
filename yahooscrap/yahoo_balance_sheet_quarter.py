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


def recalculate_ttm(v_cursor, v_ticker, v_finance_key):
    strtxt = v_ticker + "-" + v_finance_key 
    recalculate_result = "=== RECALCULATING TTM for : "+ strtxt
    if debug==True:
        print(recalculate_result)

 
    strquery = "select date_format(finance_date,'%%Y'), finance_date, finance_value, date_format(finance_date,'%%m') from stock_fin_bal_sheet_quarter "
    strquery = strquery +  " where ticker = %s and finance_key = %s and txt_header <> 'TTM' "
    strquery = strquery +  " order by finance_date desc limit 1 "
    v_cursor.execute(strquery,(v_ticker,v_finance_key))
    
    rows = v_cursor.fetchone()  
    
    if rows is not None:
        if debug is True:
            print("=== Year of TTM to be calculated: "+ str(rows[0]))
        
        txt_year = rows[0]
        txt_finance_date = rows[1]
        txt_finance_value = rows[2]
        txt_last_finance_month = int(rows[3])
        
        if txt_last_finance_month == 3:
            numberofreleases = 1
        if txt_last_finance_month == 6:
            numberofreleases = 2
        if txt_last_finance_month == 9:
            numberofreleases = 3
        if txt_last_finance_month == 12:
            numberofreleases = 4
        
        if debug is True:
            print("=== Jumlah lap keuangan yang sudah keluar "+ str(numberofreleases))
            print("=== Total value "+ v_finance_key +" dari awal Tahun  "+ txt_year + " - " + str(txt_finance_value))
        
        if numberofreleases == 1:
            ttm_val = txt_finance_value*4
        if numberofreleases == 2:
            ttm_val = txt_finance_value*2
        if numberofreleases == 3:
            ttm_val = (txt_finance_value/3)*4
        if numberofreleases == 4:
            ttm_val = txt_finance_value

        ttm_val = round(ttm_val,0)
        if debug is True:
            print("=== TTM value yang seharusnya "+ str(ttm_val))
             
            
    return  v_ticker, v_finance_key, ttm_val
    
def upd_stock_last_modify(conn,txt_ticker):
    cursor = conn.cursor()
    qry="update stocks set stock_fin_bal_sheet_quarter = now() where ticker= %s "
    cursor.execute(qry,(txt_ticker,))
    conn.commit()
    
    
def balance_sheet_quarter():
    start_time = datetime.now()
    
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
    
        cursor.execute("SELECT ticker FROM stocks order by stock_fin_bal_sheet_quarter")
        result = cursor.fetchall()  
    
        if result is not None:      
            for x in result:
                if debug == True :
                    print('https://finance.yahoo.com/quote/'+x[0]+'.JK/balance-sheet?p='+x[0]+'.JK')
            
                url='https://finance.yahoo.com/quote/'+x[0]+'.JK/balance-sheet?p='+x[0]+'.JK'
                txt_ticker = x[0]
          
                driver = webdriver.Edge(service = service, options = options)
                driver.get(url)

                time.sleep(1)
                #Default Annual are openned
                #Quarterly clickable, Expandall clickable
              
                driver.implicitly_wait(4)
                #click quarterly
                driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button/div').click()
                
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
                        # row_datas=txt_labels.find_elements(By.TAG_NAME,'span')
                        # search data using DIV  not using span -- NEW Version
                        row_datas=txt_labels.find_elements(By.TAG_NAME,'div')
                        
                        driver.implicitly_wait(4)
                        if debug==True:
                            print("=== ROW ke "+ str(k) + " Panjang div row data "+ str(len(row_datas)) )
                        
                        time.sleep(0.5)
                       
                        cnt=1
                        col_header=1 # col_header 0= breakdown, col_header 1 dst isi tanggal
                        for txt_data in row_datas:
                            #Hanya array 1 yang punya data lengkap
                            #print ("txt_data.text isi "+ txt_data.text+ " CNT " +str(cnt))
                            if cnt == 2:
                                txt_breakdown = txt_data.text
                            
                            # array data disimpan di array no 5-9 hardcoded
                            if cnt >=5 and cnt<=(5+(col_length-2)):
                                
                                print("== txt_tickers : "+ txt_ticker +" - txt_breakdown: - "+ txt_breakdown + " - txt_data "+ txt_data.text + " - header " + txt_tblheaders[col_header].text + " - counter "+ str(cnt) + " - colheader "+ str(col_header) + " - colheader "+ str(col_header+1) ) 
                                   
                                
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
                                
                                
                                arr_header =  txt_tblheaders[col_header].text.split("/")
                                if len(arr_header)>2 :
                                    lbl_header = arr_header[2]+"-"+arr_header[0]+"-"+arr_header[1]
                                
                                
                                arg1 = [txt_ticker, txt_breakdown, txt_value ,lbl_header, txt_tblheaders[col_header].text, col_header+1]
                                cursor.callproc('stock_fin_bal_sheet_quarter_upsert',arg1)
                                
                                col_header=col_header+1 
                                time.sleep(0.5)
                            if cnt==(5+(col_length-2)): # break loop jika data yang ada didalamnya sudah habis berdasarkan jumlah column  
                                r_ticker, r_finance_key, r_ttm_val = recalculate_ttm(cursor, txt_ticker, txt_breakdown)
                                arg_recalc_ttm = [r_ticker, r_finance_key,r_ttm_val,'1999-12-1','TTM',1]
                                result_args = cursor.callproc('stock_fin_bal_sheet_quarter_upsert',arg_recalc_ttm)
                                
                                break
                            
                            cnt=cnt+1
                      
                        k=k+1
                upd_stock_last_modify(conn,txt_ticker)
                
        end_time = datetime.now()
        print('Duration: {}'.format(end_time - start_time))

      
                
       
      
    
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

