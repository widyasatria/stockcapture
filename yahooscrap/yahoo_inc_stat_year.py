#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

# FILE INI SUDAH TIDAK BISA DI RUN LANGSUNG HARUS DIPANGGIL OLEH ../stockplus_scheduler.py

import os, time
from selenium import webdriver
#pip install msedge-selenium-tools

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal
# for wait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from pathlib import Path

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from configparser import ConfigParser
config = ConfigParser()
import logging
from logging.handlers import TimedRotatingFileHandler

debug = True

def rotate_log_file(log_name,log_file_path,log_file_name):
    curr_date = datetime.now()
    log_file_prev_date = curr_date - timedelta(days = 1)
    
    fname_prev_log_file= log_name+log_file_prev_date.strftime("_%d-%m-%Y")+".log"
    prev_log_file= os.path.join(log_file_path,fname_prev_log_file)
   
    if not os.path.exists(prev_log_file) and os.path.exists(log_file_name) :
        os.rename(log_file_name,prev_log_file)

def upd_stock_last_modify(conn,txt_ticker):
    cursor = conn.cursor()
    qry="update stocks set stock_fin_inc_stat_year = now() where ticker= %s "
    cursor.execute(qry,(txt_ticker,))
    conn.commit()
    

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
    options.add_argument("log-level=2")
    # log-level: 
    # Sets the minimum log level.
    # Valid values are from 0 to 3: 
    #     INFO = 0, 
    #     WARNING = 1, 
    #     LOG_ERROR = 2, 
    #     LOG_FATAL = 3.
    # default is 0.
    
    service = Service(verbose = False)
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    config_path = os.path.join(up_onefolder,"conf")
    conf_file = os.path.join(config_path,"config.ini")
    
    config = ConfigParser()
    config.read(conf_file)

    log_path = os.path.join(up_onefolder,"log")
    log_file = os.path.join(log_path,"yahoo_inc_stat_year.log")

    rotate_log_file("yahoo_inc_stat_year",log_path,log_file)
    
    #Log Level DEBUG INFO  WARNING ERROR CRITICAL
    # jika kita set info, maka warning error critical keluar, jika kita set warning : hanya warning error critical yang keluar
    my_log_format= '%(asctime)s : %(name)s : %(levelname)s : %(message)s - Line : %(lineno)d'
    logging.basicConfig(filename=log_file,level=logging.INFO, format=my_log_format, datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger('yahoo_inc_stat_year')
    
    logger.info('=================START SCRIPT yahoo_inc_stat_year ================= ')
    
    
    conn = mysql.connector.connect(
    host=config.get('db_connection', 'host'),
    user=config.get('db_connection', 'user'),
    password=config.get('db_connection', 'pwd'),
    database=config.get('db_connection', 'db'),
    auth_plugin=config.get('db_connection', 'auth')
    )
    
    cursor = conn.cursor()
    try:
    
        cursor.execute("SELECT ticker FROM stocks order by stock_fin_inc_stat_year")
        result = cursor.fetchall()  
        driver = webdriver.Edge(service = service, options = options)
        if result is not None:      
            for x in result:
                txt_ticker = x[0]
                print('=== Populating Yearly income statement for '+ txt_ticker)
                print('=== Start getting data from https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK')
                
                logger.info('=== Populating Yearly income statement for '+ str(txt_ticker))
                logger.info('=== Start getting data from https://finance.yahoo.com/quote/'+ str(x[0]) +'.JK/financials?p='+ str(x[0]) +'.JK')
                
                stime = datetime.now()
                url='https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK'
                
                
                
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
                   
                    driver.implicitly_wait(4)
                    txt_tblheaders = driver.find_elements(By.XPATH,txt_headers_xpath)
                   
                    if debug == True:
                        print('panjang headers ', len(txt_tblheaders))
                        logger.info(('panjang headers ', len(txt_tblheaders)))
                    
                    col_length = len(txt_tblheaders)
                    
                    for txt_header in txt_tblheaders:
                        if debug == True:
                            print('txt_header : ' + txt_header.text)
                            logger.info('txt_header : ' + txt_header.text)
                        if txt_header.text != 'Breakdown' and txt_header.text != 'TTM':
                            max_fin_dt = txt_header.text.split("/")
                            max_fin_date = max_fin_dt[2]+"-"+max_fin_dt[0]+"-"+max_fin_dt[1]
                            break
                ##################################
                # iterasi ke table header jika sudah ada total revenue dengan tanggal yang ada di t diberi if, jika sudah ada langsung pass ke next ticker biar tidak ambil data lagi
                if debug == True:
                    print("max_fin_date : "+ str(max_fin_date))
                    logger.info("max_fin_date : "+ str(max_fin_date))
                qry=" select count(finance_key)  from stock_fin_inc_stat_year where ticker= %s and finance_key='Total Revenue' and finance_date=%s"
                cursor.execute(qry,(txt_ticker,max_fin_date))
                rows = cursor.fetchone() 
                if debug == True:
                    print("jumlah row : " + str(rows[0]))
                    logger.info("jumlah row : " + str(rows[0]))
                    
                if cursor.rowcount > 0 and rows is not None:
                    
                    if rows[0] == 0: #jika tidak ada data nya baru ambil dari web otherwise skip
                        print("Belum ada data "+ str(url) + " di database ")
                        logger.info("Belum ada data "+ str(url) + " di database ")
                        
                        driver.implicitly_wait(4)    
                        if col_length > 2:
                            txt_all_data_css = 'rw-expnded'
                            all_datas = WebDriverWait(driver,5,1,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, txt_all_data_css))) 
                            
                            if all_datas is not None:
                                driver.implicitly_wait(4)
                                txt_tbody = driver.find_elements(By.CLASS_NAME,txt_all_data_css)
                                driver.implicitly_wait(4)
                                        
                                if debug==True:
                                    print(" Panjang rw-expanded ", len(txt_tbody))
                                    logger.info(" Panjang rw-expanded "+ str(len(txt_tbody)) )
                                k=1
                                for txt_labels in txt_tbody:
                                    time.sleep(1)
                                    #row_datas=txt_labels.find_elements(By.TAG_NAME,'span')
                                    # search data using DIV  not using span -- new version
                                    row_datas=txt_labels.find_elements(By.TAG_NAME,'div')
                                    
                                    driver.implicitly_wait(4)
                                    if debug==True:
                                        print("=== ROW ke "+ str(k) + " Panjang div row data "+ str(len(row_datas)) )
                                        logger.info("=== ROW ke "+ str(k) + " Panjang div row data "+ str(len(row_datas)) )
                                    
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
                                            print("== txt_tickers : "+ txt_ticker +" - txt_breakdown: - "+ txt_breakdown + " - txt_data "+ txt_data.text + " - header " + txt_tblheaders[col_header].text + " - counter "+ str(cnt) + " - colheader "+ str(col_header) + " - colheader+1 "+ str(col_header+1) ) 
                                            logger.info("== txt_tickers : "+ txt_ticker +" - txt_breakdown: - "+ txt_breakdown + " - txt_data "+ txt_data.text + " - header " + txt_tblheaders[col_header].text + " - counter "+ str(cnt) + " - colheader "+ str(col_header) + " - colheader+1 "+ str(col_header+1) ) 
                                         
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
                    if rows[0] > 0:
                        print("Sudah ada data di database : " + str(rows[0]))
                        logger.info("Sudah ada data di database : " + str(rows[0]))
                etime = datetime.now()
                print('Duration for this url {}'.format(etime - stime))        
                logger.info('Duration for this url {}'.format(etime - stime))        
                upd_stock_last_modify(conn,txt_ticker)
    except mysql.connector.Error as ex:
        try:
            print  (f"MySQL Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            logger.error(f"MySQL Error [%d]: %s %s",(ex.args[0], ex.args[1]))
            return None
        except IndexError:
            logger.error(f"MySQL Error: %s",str(ex))
            return None
    except Exception as ex:
        print('Generic Exception Error caught on: '+ txt_ticker +' : ' + str(ex) )
        logger.error('Generic Exception Error caught on: '+ txt_ticker +' : ' + str(ex) )
        return None
    finally:
        conn.close
        driver.quit()
        
if __name__ == "__main__":
    main()

