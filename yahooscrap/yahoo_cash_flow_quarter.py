#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

# FILE INI SUDAH TIDAK BISA DI RUN LANGSUNG HARUS DIPANGGIL OLEH ../stockplus_scheduler.py

import os, time
from selenium import webdriver


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from pathlib import Path

import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal

# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from configparser import ConfigParser
import logging


debug = True

def rotate_log_file(log_name,log_file_path,log_file_name):
    curr_date = datetime.now()
    log_file_prev_date = curr_date - timedelta(days = 1)
    
    fname_prev_log_file= log_name+log_file_prev_date.strftime("_%d-%m-%Y")+".log"
    prev_log_file= os.path.join(log_file_path,fname_prev_log_file)
   
    if not os.path.exists(prev_log_file) and os.path.exists(log_file_name) :
        os.rename(log_file_name,prev_log_file)



def recalculate_ttm(v_cursor, v_ticker, v_finance_key):
    strtxt = v_ticker + "-" + v_finance_key 
    recalculate_result = "=== RECALCULATING TTM for : "+ strtxt
    if debug==True:
        print(recalculate_result)
        print("v_finance_key "+str(v_finance_key))
        print(v_ticker)
    
    # Get Max Date
    strquery = "select max(DATE_FORMAT(finance_date,'%Y')) as max_finance_year from stock_fin_bal_sheet_quarter "
    strquery = strquery + "where ticker = %s and finance_key = %s and txt_header <> 'TTM'"
    v_cursor.execute(strquery,(v_ticker,v_finance_key))
    
    rows = v_cursor.fetchone()  
    
    if rows is not None:
        if debug is True:
            print("=== Year of TTM to be calculated: "+ str(rows[0]))
        
        txtyear = rows[0]
        # karena di yahoo finance value nya adalah income per quarter (tidak seperti di IDX dimana angka yang keluar di lap keu terakhir adalah jumlah income dari q1-qterakhir)
        # maka finance_value harus di jumlah
        strquery= "select count(ticker), sum(finance_value) from stock_fin_bal_sheet_quarter " 
        strquery = strquery + "where ticker = %s and finance_key = %s and txt_header <> 'TTM' "
        strquery = strquery + "and DATE_FORMAT(finance_date,'%Y')= %s "
   
        v_cursor.execute(strquery,(v_ticker,v_finance_key,txtyear))
        rowquartervalues = v_cursor.fetchone()  
        
        if rowquartervalues is not None:
            if debug is True:
                print("=== Jumlah lap keuangan yang sudah keluar "+ str(rowquartervalues[0]))
                print("=== Total value "+ v_finance_key +" dari awal Tahun  "+ txtyear + " - " + str(rowquartervalues[1]))
            
            numberofreleases = rowquartervalues[0]
            valueinlastreport = rowquartervalues[1]
            
            #if number of releases =3 then TTM = (valueinlastreport/3)*4
            
            if numberofreleases == 1:
                ttm_val = valueinlastreport*4
            if numberofreleases == 2:
                ttm_val = valueinlastreport*2
            if numberofreleases == 3:
                ttm_val = (valueinlastreport/3)*4
            if numberofreleases == 4:
                ttm_val = valueinlastreport
 
            ttm_val = round(ttm_val,0)
            if debug is True:
                print("=== TTM value yang seharusnya "+ str(ttm_val))
             
            
    return  v_ticker, v_finance_key, ttm_val
    
def upd_stock_last_modify(conn,txt_ticker):
    cursor = conn.cursor()
    qry="update stocks set stock_fin_cash_flow_quarter = now() where ticker= %s "
    cursor.execute(qry,(txt_ticker,))
    conn.commit()
    
    

def main():
    #requirement selenium versi 4.13.0
    #ms edge webdriver : https://msedgedriver.azureedge.net/119.0.2151.72/edgedriver_win64.zip
    
    # parameter executable_path ini sudah tidak di bisa di pakai di selenium versi 4, caranya ketik di command prompt echo %Path% untuk mengetahui existing environment variable
    # kemudian copy msedge webdriver ke salah satu path yang terdaftar.
    
    # driver = webdriver.Edge(executable_path=r'C:\Users\wardians\stockcapture\msedgedriver.exe')
    # references : https://learn.microsoft.com/en-us/microsoft-edge/webdriver-chromium/ie-mode?tabs=python
    start_time = datetime.now()
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    config_path = os.path.join(up_onefolder,"conf")
    conf_file = os.path.join(config_path,"config.ini")
  
    log_path = os.path.join(up_onefolder,"log")
    log_file = os.path.join(log_path,"yahoo_cash_flow_quarter.log")
    
    rotate_log_file("yahoo_cash_flow_quarter",log_path,log_file)
    
    #Log Level DEBUG INFO  WARNING ERROR CRITICAL
    # jika kita set info, maka warning error critical keluar, jika kita set warning : hanya warning error critical yang keluar
    my_log_format= '%(asctime)s : %(name)s : %(levelname)s : %(message)s - Line : %(lineno)d'
    logging.basicConfig(filename=log_file,level=logging.INFO, format=my_log_format, datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger('yahoo_cash_flow_quarter')

        
  

    logger.info('=================START SCRIPT yahoo_cash_flow_quarter================= ')
    options = Options()
    options.use_chromium=True
    #options.add_argument("headless")
    options.add_argument("log-level=2")
    options.add_argument("--start-maximized")
    service = Service(verbose = False)
    #service = Service(verbose = True)
    
    
    config = ConfigParser()
    config.read(conf_file)

    conn = mysql.connector.connect(
    host=config.get('db_connection', 'host'),
    user=config.get('db_connection', 'user'),
    password=config.get('db_connection', 'pwd'),
    database=config.get('db_connection', 'db'),
    auth_plugin=config.get('db_connection', 'auth')
    )
    
    cursor = conn.cursor()
    try:
    
        cursor.execute("SELECT ticker FROM stocks order by stock_fin_cash_flow_quarter")
        result = cursor.fetchall()  
        driver = webdriver.Edge(service = service, options = options)
        if result is not None:      
            for x in result:
                txt_ticker = x[0]

                
                print('=== Populating Cash Flow quarter statement for '+ txt_ticker)
                logger.info('=== Populating Cash Flow Quarter statement for '+ txt_ticker)
                
               
                url='https://finance.yahoo.com/quote/'+x[0]+'.JK/cash-flow?p='+x[0]+'.JK'
                #url='https://finance.yahoo.com/quote/'+x[0]+'.JK/financials/'
                
                # For Testing
                # txt_ticker='INDF'
                # url='https://finance.yahoo.com/quote/INDF.JK/financials?p=INDF.JK'
                
                stime = datetime.now()
          
                print('=== Start getting data from ' + url)
                logger.info('=== Start getting data from ' + url)
                driver.get(url)

                time.sleep(2)
                #Default Annual are openned
                #Quarterly clickable, Expandall clickable
                
                # driver.implicitly_wait(4)
                # #click balancesheet
               
                # element = driver.find_element(By.XPATH,'/html/body/div[2]/main/section/section/section/article/article/div/div[1]/nav/ul/li[2]/a')
                # driver.execute_script("var ele = arguments[0];ele.addEventListener('click', function() {ele.setAttribute('automationTrack','true');});",element)
                # element.click()
                # # now check the onclick attribute
                # print("Balance Sheet Clicked?  : " + element.get_attribute("automationTrack"))
                
                driver.implicitly_wait(4)
                
                #click quarterly
                #driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[1]/div[2]/button/div').click()
                #driver.find_element(By.XPATH,'//*[@id="tab-quarterly"]').click()
                driver.find_element(By.XPATH,'/html/body/div[2]/main/section/section/section/article/article/div/div[2]/div[1]/button[2]').click() # copy full xpath
                
                driver.implicitly_wait(4)
                #click expandall 
                #driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div').click()
                driver.find_element(By.XPATH,'/html/body/div[2]/main/section/section/section/article/article/div/div[2]/div[3]/button/span').click()
                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                
                driver.implicitly_wait(4)
            
                # to get the headers
                txt_headers_xpath = '//*[@id="nimbus-app"]/section/section/section/article/article/section/div/div/div[1]/div'
                txt_headers_xpath = '//*[@id="nimbus-app"]/section/section/section/article/article/section/div/div/div[1]'
                
                col_headers = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, txt_headers_xpath))) 
                
                if col_headers is not None:
                    time.sleep(0.5)
                    driver.implicitly_wait(4)
                    txt_tblheaders = driver.find_elements(By.XPATH,txt_headers_xpath)
                   
                    if debug == True:
                        print('panjang headers ', len(txt_tblheaders))
                        logger.info('panjang headers ' + str(len(txt_tblheaders)))

                    for txt_header in txt_tblheaders:
                        if debug == True:
                            print(' ISI txt_header : ' + txt_header.text)
                            print (' Jumlah Kolom : ' + str(len(txt_header.text.split())) )
                            col_length = len(txt_header.text.split())
                            logger.info('txt_header : ' + txt_header.text)
                            logger.info('Jumlah Kolom : ' + str(len(txt_header.text.split())) )
                            header_value = txt_header.text.split()
                            
                    # Jika jumlah kolom < 2 then pasti ga komplit
                    if col_length >2 :
                            # cari jumlah row
                            driver.implicitly_wait(4)

                            tbl_body_xpath = '//*[@id="nimbus-app"]/section/section/section/article/article/section/div/div/div[2]'
                            tbl_body_css = 'rowTitle'
                            tbl_body_element = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, tbl_body_css))) 
                            if tbl_body_element is not None:
                                time.sleep(0.5)
                                driver.implicitly_wait(4)
                                tbl_body_rows = driver.find_elements(By.CLASS_NAME,tbl_body_css)
                                    
                            if debug == True:
                                print('Num Rows ', len(tbl_body_rows))
                                logger.info('NumRows ' + str(len(tbl_body_rows)))

                            for tbl_body_row in tbl_body_rows:
                                if debug == True:
                                    print("")
                                    print("")
                                    print("Row Title", tbl_body_row.text)
                                    logger.info('Row Title ' + str(tbl_body_row.text))

                                row_parent = tbl_body_row.find_element(By.XPATH,'../..') # naik ke parent element dari class rowTitle
                                # print("tag name :", row_parent.tag_name)
                                # print("tag name :", row_parent.text) # akan nge print semua nya
                                col_values = row_parent.find_elements(By.CLASS_NAME,'column') 
                                
                                ctr=0
                                for col_value in col_values:
                                    if debug == True:
                                        print ("Header :", header_value[ctr])
                                        logger.info("Header " + str(header_value[ctr]))
                                        print ("Before Cleansing Column Value: ", col_value.text)
                                        logger.info("Before Cleansing Value: " + str(col_value.text))
                                    
                                    if ctr>0:    
                                        
                                        #cleansing data
                                    
                                        if col_value.text.find("k")>-1 and col_value.text.find(".")>-1:
                                            txt_value = str(col_value.text)
                                            txt_value = txt_value.replace("k","")
                                            print (" txt_value SEBLUM DIKALI: " + txt_value )
                                            txt_value = Decimal(txt_value) * 1000 
                                            print (" txt_value SEETELAH DIKALI: " + str(txt_value)) 
                                            #untuk nyetop sementara troubleshooting
                                            #time.sleep(2)
                                        elif col_value.text.isdigit() : #to check if unsigned integer is in a text
                                            print("#integer masuk sini")
                                            txt_value = Decimal(col_value.text)

                                        if (col_value.text.find(",")>-1 or col_value.text.find(".")>-1) and col_value.text.find("k")==-1 :
                                            txt_value = str(col_value.text.replace(",","").strip())
                                            txt_value = Decimal(txt_value)
                                      

                                        if col_value.text == '-' or col_value.text == '--' or col_value.text=="" or col_value.text == '0':
                                            txt_value = 0
                                        
                                        
                          
                                        #                                         
                                        if header_value[ctr] != 'TTM' and header_value[ctr] != 'Breakdown':
                                            arr_header = header_value[ctr].split("/")
                                            if len(arr_header)>2 :
                                                lbl_header = arr_header[2]+"-"+arr_header[0]+"-"+arr_header[1]
                                        else:
                                            lbl_header = '1999-12-01'

                                        
                                        if debug == True:     
                                            print ("After Cleansing Column Value: ", str(txt_value))
                                            logger.info("After Cleansing Value: "+ str(txt_value))    
                                            print("=== ROW ke "+ str(ctr) + " jumlah kolom "+ str(col_length-1))
                                            print(" Entry db Ticker : "+ txt_ticker + " -- txt_breakdown :" + txt_breakdown +" -- txt_value : "+ str(txt_value) + " -- lbl_header :" + lbl_header + " -- txt_header : "+ header_value[ctr] + " -- header index : " + str(ctr))
                                            
                                            # if txt_breakdown == 'Basic EPS':
                                            #     time.sleep(2)
                                            print("")
                                            print("")
                                        
                                        print("Insert ke database")
                                        arg1 = [txt_ticker, txt_breakdown, txt_value ,lbl_header, header_value[ctr] , str(ctr)]
                                        cursor.callproc('stock_fin_bal_sheet_quarter_upsert',arg1)
                                            
                                    
                                    elif ctr==0: # kolom pertama selalu key value nya
                                        txt_value = str(col_value.text)
                                        txt_breakdown= str(col_value.text)
                                        lbl_header=""



                                    if debug == True:
                                        print("counter ", str(ctr))
                                    ctr+=1
                               
                                # Recalculate TTM hanya dilakukan pada Net income * dan minoity interests selain dua record tsb itu tidak perlu dilakukan untuk perhitungan PER

                                if txt_breakdown.find("Net Income") >-1 or txt_breakdown.find("Minority Interests") > -1: 
                                    print("calculate TTM : " + txt_ticker + " breakdown txt : "+ txt_breakdown)
                                    r_ticker, r_finance_key, r_ttm_val = recalculate_ttm(cursor, txt_ticker, txt_breakdown)
                                    print("Hasil TTM : " + str(r_ttm_val) + " Ticker txt : "+ str(r_ticker) + "finance key : "+ str(r_finance_key))

                                    arg_recalc_ttm = [r_ticker, r_finance_key,r_ttm_val,'1999-12-01','TTM',1]
                                    cursor.callproc('stock_fin_cash_flow_quarter_upsert',arg_recalc_ttm)
                                    
                                    #untuk nyetop sementara troubleshooting
                                    #time.sleep(25)

                            etime = datetime.now()
                            print('Duration for this url {}'.format(etime - stime))     
                            logger.info('Duration for this url {}'.format(etime - stime))   
                            upd_stock_last_modify(conn,txt_ticker)       
                            
                            #untuk nyetop sementara troubleshooting
                            #time.sleep(25)

        end_time = datetime.now()
        print('Duration: {}'.format(end_time - start_time))    
        logger.info('Duration: {}'.format(end_time - start_time))    
        logger.info('=================End script yahoo_inc_start_quarter================= ')
        
    except mysql.connector.Error as ex:
        print('Mysql Generic Error caught on: ' + str(ex))
        logger.error('Mysql Generic error caught on: ' + str(ex))
        try:
            print(f"MySQL Generic Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            logger.error(f"MySQL Generic Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            return None
        except IndexError:
            print (f"MySQL Index Error: %s",str(ex))
            logger.error(f"MySQL Index Error: %s",str(ex))
            return None
    except Exception as ex:
        print('Exception Error caught on: ' + str(ex) )
        logger.error('Exception Error caught on: ' + str(ex) )
        return None
    finally:
        conn.close
        driver.quit()
        

if __name__ == "__main__":
    main()

