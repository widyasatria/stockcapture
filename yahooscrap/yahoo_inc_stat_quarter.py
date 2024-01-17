#https://stackoverflow.com/questions/50692358/how-to-work-with-a-specific-version-of-chromedriver-while-chrome-browser-gets-up
#https://stackoverflow.com/questions/63529124/how-to-open-up-microsoft-edge-using-selenium-and-python

# FILE INI SUDAH TIDAK BISA DI RUN LANGSUNG HARUS DIPANGGIL OLEH ../yahoo_data_scheduler.py

import os, time
from selenium import webdriver


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from pathlib import Path
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

from configparser import ConfigParser
import logging

debug = True

def recalculate_ttm(v_cursor, v_ticker, v_finance_key):
    strtxt = v_ticker + "-" + v_finance_key 
    recalculate_result = "=== RECALCULATING TTM for : "+ strtxt
    if debug==True:
        print(recalculate_result)
    
    strquery = "select max(DATE_FORMAT(finance_date,'%%Y')) as max_finance_year from stock_fin_inc_stat_quarter "
    strquery = strquery + "where ticker = %s and finance_key = %s and txt_header <> 'TTM'"
    v_cursor.execute(strquery,(v_ticker,v_finance_key))
    
    rows = v_cursor.fetchone()  
    
    if rows is not None:
        if debug is True:
            print("=== Year of TTM to be calculated: "+ str(rows[0]))
        
        txtyear = rows[0]
        
        strquery= "select count(ticker), sum(finance_value) from stock_fin_inc_stat_quarter " 
        strquery = strquery + "where ticker = %s and finance_key = %s and txt_header <> 'TTM' "
        strquery = strquery + "and DATE_FORMAT(finance_date,'%%Y')= %s "
   
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
    qry="update stocks set stock_fin_inc_stat_quarter = now() where ticker= %s "
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
    
   
    log_path = os.path.join(up_onefolder,"log")
    log_file = os.path.join(log_path,"yahoo_inc_stat_quarter.log")

    
    #DEBUG
    #INFO
    #WARNING
    #ERROR
    #CRITICAL
    FORMAT = '%(asctime)s : %(name)s : %(levelname)s : %(message)s - Line : %(lineno)d'
    logging.basicConfig(filename=log_file, level=logging.INFO, format=FORMAT, datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger('yahoo_inc_stat_quarter')
    logger.info('=================START SCRIPT yahoo_inc_start_quarter================= ')
    
   
    options = Options()
    options.use_chromium=True
    options.add_argument("headless")
    options.add_argument("log-level=2")
    service = Service(verbose = False)
    
    
 
    config_path = os.path.join(up_onefolder,"conf")
    conf_file = os.path.join(config_path,"config.ini")
    
    config = ConfigParser()
    config.read(conf_file)

    conn = MySQLdb.connect(
    host=config.get('db_connection', 'host'),
    user=config.get('db_connection', 'user'),
    password=config.get('db_connection', 'pwd'),
    database=config.get('db_connection', 'db'),
    auth_plugin=config.get('db_connection', 'auth')
    )
    
    cursor = conn.cursor()
    try:
    
        cursor.execute("SELECT ticker FROM stocks order by stock_fin_inc_stat_quarter")
        result = cursor.fetchall()  
        driver = webdriver.Edge(service = service, options = options)
        if result is not None:      
            for x in result:
                txt_ticker = x[0]
                print('=== Populating Quarterly income statement for '+ txt_ticker)
                logger.info('=== Populating Quarterly income statement for '+ txt_ticker)
                
                url='https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK'
               
                stime = datetime.now()
          
                print('=== Start getting data from https://finance.yahoo.com/quote/'+x[0]+'.JK/financials?p='+x[0]+'.JK')

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
                    time.sleep(0.5)
                    driver.implicitly_wait(4)
                    txt_tblheaders = driver.find_elements(By.XPATH,txt_headers_xpath)
                   
                    if debug == True:
                        print('panjang headers ', len(txt_tblheaders))
                        logger.info('panjang headers ', len(txt_tblheaders))
                        
                    
                    col_length = len(txt_tblheaders)
                
                    for txt_header in txt_tblheaders:
                        if debug == True:
                            print('txt_header : ' + txt_header.text)
                            logger.info('txt_header : ' + txt_header.text)
                    
                  
                    
                    #gara2 internet ga bisa
                    # max_fin_dt = txt_tblheaders[2].text.split("/")
                    # print("pjg max_fin_dt " + str(len(max_fin_dt)))
                    # max_fin_date = max_fin_dt[2]+"-"+max_fin_dt[0]+"-"+max_fin_dt[1]
                    # print("max_fin_date " + str(max_fin_date))    
                    
                    
                # if debug == True:
                #     print("max_fin_date : "+ str(max_fin_date))
                # qry=" select count(finance_key)  from stock_fin_inc_stat_quarter where ticker= %s and finance_key='Total Revenue' and finance_date=%s"
                # cursor.execute(qry,(txt_ticker,max_fin_date))
                # rows = cursor.fetchone() 
                # if debug == True:
                #     print("jumlah row : " + str(rows[0]))
                # if cursor.rowcount > 0 and rows is not None:
                    
                #     if rows[0] == 0: #jika tidak ada data nya baru ambil dari web otherwise skip
                #         print("Belum ada data "+ str(url) + " di database ")
                 
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
                                logger.info(" Panjang rw-expanded " + str(len(txt_tbody)))
                            k=1
                            for txt_labels in txt_tbody:
                                time.sleep(1)
                                # row_datas=txt_labels.find_elements(By.TAG_NAME,'span')
                                # search data using DIV  not using span -- NEW Version
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
                                    if debug==True:
                                        print("txt_data.text isi "+ txt_data.text+ " CNT " +str(cnt))
                                        logger.info("txt_data.text isi "+ txt_data.text+ " CNT " +str(cnt))
                                    if cnt == 2:
                                        txt_breakdown = txt_data.text
                                    
                                    # array data disimpan di array no 5 = TTM dst sampai 10  hardcoded
                                    if cnt >=5 and cnt<=(5+(col_length-2)):
                                        print("== txt_tickers : "+ txt_ticker +" - txt_breakdown: - "+ txt_breakdown + " - txt_data "+ txt_data.text + " - header " + txt_tblheaders[col_header].text + " - counter "+ str(cnt) + " - colheader "+ str(col_header) + " - colheader "+ str(col_header+1) ) 
                                        logger.info("== txt_tickers : "+ txt_ticker +" - txt_breakdown: - "+ txt_breakdown + " - txt_data "+ txt_data.text + " - header " + txt_tblheaders[col_header].text + " - counter "+ str(cnt) + " - colheader "+ str(col_header) + " - colheader "+ str(col_header+1) ) 
                                        
                                        
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
                                        
                                        if txt_tblheaders[col_header].text != 'TTM':
                                            arr_header =  txt_tblheaders[col_header].text.split("/")
                                            if len(arr_header)>2 :
                                                lbl_header = arr_header[2]+"-"+arr_header[0]+"-"+arr_header[1]
                                        else:
                                            lbl_header = '1999-12-01'
                                        
                                    
                                        
                                        arg1 = [txt_ticker, txt_breakdown, txt_value ,lbl_header, txt_tblheaders[col_header].text, col_header+1]
                                        cursor.callproc('stock_fin_inc_stat_quarter_upsert',arg1)
                                        
                                        col_header=col_header+1 
                                        time.sleep(0.5)
                                    
                                    # di akhir kolom recalculate TTM
                                    if cnt==(5+(col_length-2)): # break loop jika data yang ada didalamnya sudah habis berdasarkan jumlah column  
                                        r_ticker, r_finance_key, r_ttm_val = recalculate_ttm(cursor, txt_ticker, txt_breakdown)
                                        arg_recalc_ttm = [r_ticker, r_finance_key,r_ttm_val,'1999-12-1','TTM',2]
                                        result_args = cursor.callproc('stock_fin_inc_stat_quarter_upsert',arg_recalc_ttm)
                                        
                                    if cnt==(5+(col_length-2)): # break loop jika data yang ada didalamnya sudah habis berdasarkan jumlah column  
                                        break
                                    
                                    cnt=cnt+1
                            
                                k=k+1
                etime = datetime.now()
                print('Duration for this url {}'.format(etime - stime))        
                upd_stock_last_modify(conn,txt_ticker)       
        end_time = datetime.now()
        print('Duration: {}'.format(end_time - start_time))    
        logger.info('Duration: {}'.format(end_time - start_time))    
        logger.info('=================End script yahoo_inc_start_quarter================= ')
        
    except MySQLdb.Error as ex:
        print('Mysql Generic error caught on: ' + str(ex))
        logger.error('Mysql Generic error caught on: ' + str(ex))
        # try:
        #     print(f"MySQL Error [%d]: %s %s",(ex.args[0], ex.args[1]))
        #     logger.error(f"MySQL Error [%d]: %s %s",(ex.args[0], ex.args[1]))
        #     return None
        # except IndexError:
        #     print (f"MySQL Error: %s",str(ex))
        #     logger.error(f"MySQL Error: %s",str(ex))
        #     return None
    except MySQLdb.DatabaseError as ex:
        logger.error('MYSQL DatabaseError  caught on: ' + str(ex))
    
    except OperationalError as ex:
        print('MYSQL operational error caught on: ' + str(ex))
        logger.error('MYSQL operational error caught on: ' + str(ex))

        return None
    except MySQLdb.OperationalError as ex:
        print('MYSQL operational error caught on: ' + str(ex))
        logger.error('MYSQL operational error caught on: ' + str(ex))
 
        return None
    except TypeError as ex:
        print(ex)
        logger.error(ex)
        return None
    except ValueError as ex:
        print(ex)
        logger.error(ex)
        return None
    except Exception as ex:
        print('Generic Error caught on: ' + str(ex) )
        logger.error('Generic Error caught on: ' + str(ex) )
        return None
    finally:
        conn.close
        driver.quit()
        

if __name__ == "__main__":
    main()

