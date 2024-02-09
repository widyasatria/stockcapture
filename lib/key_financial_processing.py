
#requires  pip install --upgrade holidays, python-mysql
# holidays https://pypi.org/project/holidays/
import mysql.connector
from datetime import datetime, timedelta, date
from decimal import Decimal
import holidays, requests
from pathlib import Path
import os,time
from configparser import ConfigParser
import logging

debug = True

api_limit = 980

def rotate_log_file(log_name,log_file_path,log_file_name):
    curr_date = datetime.now()
    log_file_prev_date = curr_date - timedelta(days = 1)
    
    fname_prev_log_file= log_name+log_file_prev_date.strftime("_%d-%m-%Y")+".log"
    prev_log_file= os.path.join(log_file_path,fname_prev_log_file)
   
    if not os.path.exists(prev_log_file) and os.path.exists(log_file_name) :
        os.rename(log_file_name,prev_log_file)



def get_iso_ticker(cursor,txt_ticker):
     
    qry= " select CONCAT(ticker,'.', exchange) as iso_ticker "
    qry = qry + " from stocks where ticker=%s "    
    cursor.execute(qry,(txt_ticker,))
    rows = cursor.fetchone() 
    if cursor.rowcount > 0:
        return rows[0]
    else:
        return ''

def is_max_finance_date(conn,txt_ticker,val_finance_date):
    qry="select max(finance_date) from key_financials where ticker = %s"
    cursor = conn.cursor()
    cursor.execute(qry,(txt_ticker,))
    rows = cursor.fetchone() 
    bool = False
    if cursor.rowcount > 0 :
        if rows[0] == val_finance_date :
            print("rows[0] " + str(rows[0]) + " val_finance_date : " + str(val_finance_date))
            bool = True
        else:
            bool = False
    
    return bool

def get_ticker_price_by_date(cursor,txt_ticker,the_date):
    qry= " select close,date from stock_daily where ticker = %s "
    qry = qry + " and  date = %s  limit 1"
    
    cursor.execute(qry,(txt_ticker,the_date))
    rows = cursor.fetchone() 

    if cursor.rowcount > 0:
        if debug is True:
            print( str(txt_ticker) + " Price at  : "+ str(rows[1]) + " : " + str(rows[0]) )
        return rows[0]
    else:
        # if debug is True:
        #     print( "No data set price to 0 " + str(txt_ticker) + " val_finance_date "+ str(the_date) + "  Price = 0 ")
        cl_price = 0
        return cl_price 
    
def get_last_price(conn,txt_ticker,val_finance_date):
    cursor = conn.cursor()
    
    bool_max_date = is_max_finance_date(conn,txt_ticker,val_finance_date)
    if debug == True:
        print("============== GET LAST PRICE ==================")
        print(" Is max_finance date " + str(val_finance_date) + " : " + str(bool_max_date) )
   
    if bool_max_date == True:
        txt_ticker = get_iso_ticker(cursor,txt_ticker)
        id_holidays = holidays.country_holidays('ID') 
        dt_today = date.today()
        dt_yesterday = dt_today - timedelta(days=1)
        
        # if debug == True:
        #     print("tanggal kemarin: " + str(dt_yesterday) )
        
        while dt_yesterday.weekday() ==5 or dt_yesterday.weekday() ==6 or val_finance_date in id_holidays or get_ticker_price_by_date(cursor,txt_ticker,dt_yesterday) == 0:
            dt_yesterday =  dt_yesterday - timedelta(days=1)
        
        the_price = get_ticker_price_by_date(cursor,txt_ticker,dt_yesterday)
        if debug is True:    
            print("Date After Busines Working Day : " + str(dt_yesterday) + " the price  : "+ str(the_price))
            print("============== END OF GET LAST PRICE ==================")
            
    else:
        #estimasi rata2 tanggal release laporan keuangan
        val_finance_date = val_finance_date + timedelta(days=35)
        
        txt_ticker = get_iso_ticker(cursor,txt_ticker)
        
        id_holidays = holidays.country_holidays('ID') 
        if debug is True:
            print("Date Before : " + str(val_finance_date) )
       
        while val_finance_date.weekday() ==5 or val_finance_date.weekday() ==6 or val_finance_date in id_holidays or get_ticker_price_by_date(cursor,txt_ticker,val_finance_date) == 0:
            val_finance_date =  val_finance_date + timedelta(days=1)
        
     
        the_price = get_ticker_price_by_date(cursor,txt_ticker,val_finance_date)
        if debug is True:    
            print("Date After Busines Working Day : " + str(val_finance_date) + " the price  : "+ str(the_price))
            print("============== END OF GET LAST PRICE ==================")
            
    return the_price
            
 
def get_finance_value(cursor, table_name, txt_ticker, txt_finance_date, finance_key):
    print("=== START GET FINANCE VALUE FOR : " + str(finance_key) + "================")
    if table_name == 'stock_fin_inc_stat_quarter':  
       
        qry = "select max(DATE_FORMAT(finance_date,'%Y')) from stock_fin_inc_stat_quarter "
        qry = qry + "where ticker = %s and txt_header <> 'TTM' "
        qry = qry + "and finance_key = %s "  #'Net Income Common Stockholders'
        
        cursor.execute(qry,(txt_ticker,finance_key))
        
        rows = cursor.fetchone() 
        max_year = rows[0]
    
        val_finance_date = str(txt_finance_date).split('-')
 
        if int(val_finance_date[0]) == int(max_year):
            qry = "select sum(finance_value) from stock_fin_inc_stat_quarter "
            qry = qry + " where ticker = %s and txt_header <> 'TTM' "
            qry = qry + " and DATE_FORMAT(finance_date,'%Y-%m') <= DATE_FORMAT(%s,'%Y-%m') "  
            qry = qry + " and DATE_FORMAT(finance_date,'%Y') = %s " #max_year
            qry = qry + " and finance_key = %s " #'Net Income Common Stockholders'
            cursor.execute(qry,(txt_ticker,txt_finance_date,max_year,finance_key))
            rows = cursor.fetchone() 
            if cursor.rowcount > 0:
                txt_finance_value = rows[0]
                
            else:
                txt_finance_value = 0
        
      
        if int(val_finance_date[0]) == int(max_year)-1: 
            #print(" Tablename " + table_name+" val_finance_date[1] : "+ val_finance_date[1])
           
            if int(val_finance_date[1]) == 12:
                
                #print(" INI YANG 12 isi int(val_finance_date[1]) : " + str(val_finance_date[1]))
                
                qry = "select finance_value from stock_fin_inc_stat_year"
                qry = qry + " where ticker = %s and txt_header <> 'TTM' "
                qry = qry + " and finance_key = %s "
                qry = qry + " and finance_date=%s "
                
                if debug == True:
                    print(" Cek di table stock_fin_inc_stat_year untuk isi year end net income: " + " ticker : "+ txt_ticker + " finance key : "  + str(finance_key) + " txt_finance_date " + str(txt_finance_date))
                
                cursor.execute(qry,(txt_ticker,finance_key, txt_finance_date))
                rows = cursor.fetchone() 
                if cursor.rowcount > 0:
                    txt_finance_value = rows[0]
                    #print(" ADA RECORD NYA BLOSS: " + " ticker : "+ txt_ticker + " finance key : "  + str(finance_key) + " txt_finance_date " + str(txt_finance_date))
                else:
                    txt_finance_value = 0
                
            if int(val_finance_date[1]) == 9 or int(val_finance_date[1]) == 3:
                
                #print(" INI YANG 9 or 3 Masuk sini isi int(val_finance_date[1]) : " + str(val_finance_date[1]))
                
                qry = "select sum(finance_value) from stock_fin_inc_stat_quarter "
                qry = qry + " where ticker = %s and txt_header <> 'TTM' "
                qry = qry + " and DATE_FORMAT(finance_date,'%Y-%m') <= DATE_FORMAT(%s,'%Y-%m') "  
                qry = qry + " and DATE_FORMAT(finance_date,'%Y') = %s " #max_year-1
                qry = qry + " and finance_key = %s " #'Net Income Common Stockholders'
                cursor.execute(qry,(txt_ticker,txt_finance_date,int(max_year)-1,finance_key))
                rows = cursor.fetchone() 
                if cursor.rowcount > 0:
                    txt_finance_value = rows[0]
                else:
                    txt_finance_value = 0
                    
    else:
        
        qry = "select finance_value from "+ table_name +" where finance_key = %s and finance_date = %s and ticker = %s limit 1"
        # if debug == True:
        #     print(finance_key + " finance_date : "+ str(txt_finance_date) + "txt ticker : " + txt_ticker + " query " + qry )
        cursor.execute(qry,(finance_key,txt_finance_date, txt_ticker))
        rows = cursor.fetchone() 
        if cursor.rowcount > 0:
            txt_finance_value = rows[0]
        else:
            txt_finance_value = 0
    
    print("=== END GET FINANCE VALUE FOR : " + str(finance_key) + "================")
    return txt_finance_value

def calculate_ttm(txt_ticker,txt_finance_date, txt_net_income_stakeholder):
    val_finance_date = str(txt_finance_date).split('-')
    month = int(val_finance_date[1])
    if month == 12:
        ttm_value = txt_net_income_stakeholder
    if month == 9:
        ttm_value = (txt_net_income_stakeholder/3)*4
    if month == 6:
        ttm_value = (txt_net_income_stakeholder/2)*4
    if month == 3:
        ttm_value = (txt_net_income_stakeholder)*4
    
    return ttm_value

def calculate_book_value(cursor, val_ticker,val_finance_date,txt_stockholders_equity,txt_share_issued):  
    
    qry = " select cx.rate, s.unit_of_number,s.currency, s.ticker from stocks s, currency_fx cx "
    qry = qry + " where s.currency = cx.currency "  
    qry = qry + " and ticker = %s "
    cursor.execute(qry,(val_ticker,))

    rows = cursor.fetchone()
    if cursor.rowcount > 0:
        
        txt_rate = rows[0]
        txt_unit_of_number = rows[1]
        txt_book_value = round(( (txt_stockholders_equity*txt_unit_of_number)/(txt_share_issued*txt_unit_of_number) )*txt_rate,2)
        if debug==True:
            print("============= CALCULATE BOOK VALUE ======")
            print (" txt_stockholders_equity * txt_unit_of_number : " + str(txt_stockholders_equity*txt_unit_of_number))
            print(" txt_share_issued * txt_unit_of_number : " + str(txt_share_issued*txt_unit_of_number))
            print(" round(( (txt_stockholders_equity*txt_unit_of_number)/(txt_share_issued*txt_unit_of_number) ) )* txt_rate,2 : " + str(txt_book_value) )
            print("============= END OF CALCULATE BOOK VALUE =====")
        
        
    else:
        txt_book_value = 0
    return txt_book_value

def average_values(cursor,val_ticker,val_finance_date):
    
    qry = " select IFNULL(avg(price_to_book_value),0) pbv_avg, "
    qry = qry + "IFNULL(avg(price_earning_ratio),0) per_avg, "
    qry = qry + "IFNULL(avg(return_on_equity),0) roe_avg  from key_financials "
    qry = qry + " where ticker = %s and price_to_book_value <> 0 and price_earning_ratio <> 0 and return_on_equity <> 0 and finance_date <= %s"  
   
    cursor.execute(qry,(val_ticker,val_finance_date))
    rows = cursor.fetchone()
    
    if cursor.rowcount > 0 and rows is not None:
        txt_book_value_avg = rows[0]
        txt_per_avg = rows[1]
        txt_roe_avg = rows[2]
        if debug==True:
            print(" txt_book_value_avg :"+ str(txt_book_value_avg) + " txt_per_avg : "+ str(txt_per_avg) + " txt_roe_avg : " + str(txt_roe_avg) + " ticker "+ val_ticker + str(val_finance_date))
       
    else:
        txt_book_value_avg = 0
        txt_per_avg = 0
        txt_roe_avg = 0

    return txt_book_value_avg, txt_per_avg, txt_roe_avg

def calculate_per(txt_last_price, txt_net_income_ttm,txt_share_issued,txt_currency, txt_unit_of_number, txt_rate):
    if txt_currency == 'IDR' :
        if debug == True:
            print('txt_last_price '+ str(txt_last_price) +' txt_net_income_ttm : '+ str(txt_net_income_ttm) + " txt_unit_of_number : " + str(txt_unit_of_number) + "txt_share_issued : " +str(txt_share_issued) )
       
        val_per = round(txt_last_price/( (txt_net_income_ttm* txt_unit_of_number) / (txt_share_issued*txt_unit_of_number)),2)
    if txt_currency == 'USD' :
        if debug == True:
            print('txt_last_price '+ str(txt_last_price) +' txt_net_income_ttm : '+ str(txt_net_income_ttm) + " txt_unit_of_number : " + str(txt_unit_of_number) + "txt_share_issued : " +str(txt_share_issued) )
        
        val_per = round(txt_last_price/(((txt_net_income_ttm* txt_unit_of_number)*txt_rate) / (txt_share_issued*txt_unit_of_number)),2)
    return val_per

def calculate_eps(txt_net_income_ttm,txt_share_issued,txt_currency, txt_unit_of_number, txt_rate):
    if txt_currency == 'IDR' :
        if debug == True:
            print('txt_net_income_ttm : '+ str(txt_net_income_ttm) + " txt_unit_of_number : " + str(txt_unit_of_number) + "txt_share_issued : " +str(txt_share_issued) )
        val_per = round(((txt_net_income_ttm* txt_unit_of_number) / (txt_share_issued*txt_unit_of_number)),2)
    if txt_currency == 'USD' :
        if debug == True:
            print('txt_net_income_ttm : '+ str(txt_net_income_ttm) + " txt_unit_of_number : " + str(txt_unit_of_number) + "txt_share_issued : " +str(txt_share_issued) )
        val_per = round(( (txt_net_income_ttm* txt_unit_of_number *txt_rate) / (txt_share_issued*txt_unit_of_number) ),2)
    return val_per

def update_key_financial_records(conn,val_ticker,val_finance_date,txt_currency, txt_unit_of_number,txt_rate,logger):
    
    cursor = conn.cursor()
    txt_share_issued = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Share Issued')
    #txt last price ini kalau bisa ambil pada saat tanggal yang ditentukan
    txt_last_price = get_last_price(conn,val_ticker, val_finance_date)
    txt_stockholders_equity = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Stockholders\' Equity')
    
    txt_total_liabilities = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Total Liabilities Net Minority Interest')
    txt_current_liabilities = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Current Liabilities')
    txt_non_current_liabilities = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Total Non Current Liabilities Net minority interest')
    
    txt_non_current_assets = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Total non-current assets')
    
    txt_current_assets = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Current Assets')
    txt_total_assets = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Total Assets')
    txt_net_income_stakeholders = get_finance_value(cursor,'stock_fin_inc_stat_quarter',val_ticker,val_finance_date,'Net Income Common Stockholders')
    
   
    txt_net_income_ttm = calculate_ttm(val_ticker,val_finance_date,txt_net_income_stakeholders)
    
    txt_book_value = calculate_book_value(cursor, val_ticker,val_finance_date,txt_stockholders_equity,txt_share_issued)
  
    txt_price_to_book_value = round((txt_last_price/txt_book_value),2)
    
  
    
    txt_per = calculate_per(txt_last_price, txt_net_income_ttm,txt_share_issued,txt_currency, txt_unit_of_number, txt_rate)
    
    txt_roe = round((txt_net_income_ttm/txt_stockholders_equity)*100,2)
    txt_der = round(txt_total_liabilities/txt_stockholders_equity,2)
    txt_cash_equiv = get_finance_value(cursor,'stock_fin_bal_sheet_quarter',val_ticker,val_finance_date,'Cash And Cash Equivalents')
    
    txt_eps = calculate_eps(txt_net_income_ttm,txt_share_issued,txt_currency, txt_unit_of_number, txt_rate)
    
    txt_avg_book_value, txt_per_avg, txt_roe_avg  = average_values(cursor,val_ticker,val_finance_date)
    
    if debug == 'True':
        print(' txt_eps '+ str(txt_eps) +' txt_per : '+ str(txt_per)+ 'txt_book_value : ' + str(txt_book_value) + 'txt_avg_book_value : ' + str(txt_avg_book_value) + " : " + str(txt_price_to_book_value) )
        logger.info(' txt_eps '+ str(txt_eps) +' txt_per : '+ str(txt_per)+ 'txt_book_value : ' + str(txt_book_value) + 'txt_avg_book_value : ' + str(txt_avg_book_value) + " : " + str(txt_price_to_book_value) )
    
    # if debug == 'True':        
        # print("txt_last_price " + str(txt_last_price) + " txt_book_value "  + str(txt_book_value) + " round((txt_last_price/txt_book_value),2) : " + str(round((txt_last_price/txt_book_value),2)) )
        # print(" txt_share_issued: " + str(txt_share_issued) + " txt_last_price  :" + str(txt_last_price) + " txt_stockholders equyity  :" + str(txt_stockholders_equity) + " txt_total_liabilities   :" + str(txt_total_liabilities))
        
    
    qry = " update key_financials "
    qry = qry + " set share_issued=%s, "
    qry = qry + " price=%s, "
    qry = qry + " stockholders_equity=%s, "
    
    qry = qry + " total_liabilities=%s, "
    qry = qry + " current_liabilities=%s, "
    qry = qry + " non_current_liabilities=%s, "
    
    qry = qry + " non_current_assets=%s, "
    qry = qry + " current_assets=%s, "
    qry = qry + " total_assets=%s, "
    qry = qry + " net_income_stakeholders=%s, "
    qry = qry + " net_income_ttm=%s, "
    qry = qry + " book_value=%s, "
    qry = qry + " price_to_book_value=%s, "
    qry = qry + " price_to_book_value_avg=%s, "
    #masih salah kalkulasinya
    qry = qry + " price_earning_ratio=%s, "
    qry = qry + " earning_per_share=%s, "
    qry = qry + " return_on_equity=%s, "
    qry = qry + " der=%s, "
    qry = qry + " cash_and_equivalents=%s, "
    qry = qry + " price_earning_ratio_avg=%s, "
    qry = qry + " return_on_equity_avg=%s "
    
    qry = qry + " where ticker=%s "
    qry = qry + " and finance_date =%s "
    
    cursor.execute(qry,(txt_share_issued,txt_last_price,txt_stockholders_equity,txt_total_liabilities,txt_current_liabilities,txt_non_current_liabilities,txt_non_current_assets,
                        txt_current_assets,txt_total_assets,txt_net_income_stakeholders,txt_net_income_ttm,txt_book_value, txt_price_to_book_value,txt_avg_book_value,txt_per, txt_eps,
                        txt_roe,txt_der,txt_cash_equiv, txt_per_avg, txt_roe_avg,
                        val_ticker,val_finance_date))
    conn.commit() 

def key_financial_processing():
    
    path = Path(__file__)
    up_onefolder = path.parent.absolute().parent
    config_path = os.path.join(up_onefolder,"conf")
    conf_file = os.path.join(config_path,"config.ini")
    log_path = os.path.join(up_onefolder,"log")
    log_file = os.path.join(log_path,"key_financial_processing.log")
    
    rotate_log_file("key_financial_processing",log_path,log_file)
    
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
    
    
    my_log_format= '%(asctime)s : %(name)s : %(levelname)s : %(message)s - Line : %(lineno)d'
    logging.basicConfig(filename=log_file,level=logging.INFO, format=my_log_format, datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger('key_financial_processing')

    logger.info('=================START SCRIPT key_financial_processing ================= ')


    try:
        #cursor.execute("SELECT ticker,exchange, currency, unit_of_number FROM stocks")
        cursor.execute("select  s.ticker, s.exchange, s.currency,  s.unit_of_number, cx.rate from stocks s, currency_fx cx where s.currency = cx.currency")
        stocklists = cursor.fetchall() 
        
        if stocklists is not None:   
            for x in stocklists:
                txt_ticker = x[0]
                txt_exchange = x[1]
                txt_currency = x[2]
                txt_unit_of_number = x[3]
                txt_rate = x[4]
          
               
                
                qry = " select bs.ticker, bs.finance_key,finance_value, finance_date,txt_header from stock_fin_bal_sheet_quarter bs "
                qry = qry + " where bs.ticker= %s "
                qry = qry + " and bs.txt_header <> 'TTM' "
                qry = qry + " and bs.finance_key = 'Total Assets' "
                qry = qry + " order by bs.id "
                
                cursor.execute(qry,(txt_ticker,))
                fin_bal_sheet = cursor.fetchall() 
               
                if fin_bal_sheet is not None:
                    for y in fin_bal_sheet:
                        bs_ticker = y[0]
                        bs_finance_key = y[1]
                        bs_finance_value = y[2]
                        bs_finance_date = y[3]
                        bs_txt_header = y[4]
                    
                        qry = " select count(*) rowexist from key_financials where ticker= %s and finance_date = %s and total_assets is not null" 
                        cursor.execute(qry,(bs_ticker,bs_finance_date))
                        numrow = cursor.fetchone()  
                  
                        #if norecord
                        if numrow[0]== 0:
                            if debug == True:
                                print("Belum ada di DB - Jumlah Row : " + str(numrow[0])  + " INSERT " + bs_ticker + " " + str(bs_finance_date)+ " " + str(bs_finance_key))
                                logger.info("Belum ada di DB - Jumlah Row : " + str(numrow[0])  + " INSERT " + bs_ticker + " " + str(bs_finance_date)+ " " + str(bs_finance_key))
                            qry = "INSERT INTO key_financials(ticker, "
                            qry = qry + " total_assets, "
                            qry = qry + " finance_date, "
                            qry = qry + " txt_header, "
                            qry = qry + " share_issued, "
                            qry = qry + " price, "
                            qry = qry + " stockholders_equity, "
                            qry = qry + " net_income_stakeholders, "
                            qry = qry + " net_income_ttm, "
                            qry = qry + " book_value, "
                            qry = qry + " price_to_book_value, "
                            qry = qry + " price_to_book_value_avg, "
                            qry = qry + " price_earning_ratio,"
                            qry = qry + " price_earning_ratio_avg, "
                            qry = qry + " earning_per_share, "
                            qry = qry + " return_on_equity, "
                            qry = qry + " return_on_equity_avg, "
                            qry = qry + " total_liabilities, "
                            qry = qry + " current_liabilities, "
                            qry = qry + " non_current_liabilities, "
                            qry = qry + " der, "
                            qry = qry + " current_assets, "
                            qry = qry + " cash_and_equivalents,"
                            qry = qry + " non_current_assets, "
                            qry = qry + " url_to_chart,"
                            qry = qry + " remarks, "
                            qry = qry + " flag, "
                            qry = qry + " created_at,"
                            qry = qry + " updated_at)"
                            qry = qry + " VALUES (%s,%s,%s,%s,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'','','',now(),now()) "
                            cursor.execute(qry,(bs_ticker,bs_finance_value,bs_finance_date,bs_txt_header))
                            conn.commit()    

                            update_key_financial_records(conn,bs_ticker,bs_finance_date,txt_currency, txt_unit_of_number,txt_rate,logger)
                           
                        
                        if numrow[0] == 1:
                            if debug == True:
                                print(" Sudah ada di DB - Jumlah Row : " + str(numrow[0])  + " UPDATE " + bs_ticker + " " + str(bs_finance_date)+ " " + str(bs_finance_key)+ " " + str(bs_finance_value) )
                                logger.info(" Sudah ada di DB - Jumlah Row : " + str(numrow[0])  + " UPDATE " + bs_ticker + " " + str(bs_finance_date)+ " " + str(bs_finance_key)+ " " + str(bs_finance_value) )
                            # jika total_assets sudah ada di update
                            update_key_financial_records(conn,bs_ticker,bs_finance_date,txt_currency, txt_unit_of_number,txt_rate,logger) 
                       
        logger.info('=================END SCRIPT key_financial_processing ================= ')              
                        
 
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
        

def main():
    key_financial_processing()
    
if __name__ == '__main__':
    main()