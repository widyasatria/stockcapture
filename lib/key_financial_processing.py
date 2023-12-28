
#requires  pip install --upgrade holidays, python-mysql
# holidays https://pypi.org/project/holidays/
import MySQLdb
from datetime import datetime, timedelta
from decimal import Decimal
import holidays, requests

from configparser import ConfigParser

debug = True
config = ConfigParser()
config.read('./conf/config.ini')
api_limit = 980
def get_iso_ticker(cursor,txt_ticker):
     
    qry= " select CONCAT(ticker,'.', exchange) as iso_ticker "
    qry = qry + " from stocks where ticker=%s "    
    cursor.execute(qry,(txt_ticker,))
    rows = cursor.fetchone() 
    if cursor.rowcount > 0:
        return rows[0]
    else:
        return ''
    
def get_last_price(conn,txt_ticker,val_finance_date):
    cursor = conn.cursor()
    #estimasi rata2 tanggal release laporan keuangan
    val_finance_date = val_finance_date + timedelta(days=35)
    
    txt_ticker = get_iso_ticker(cursor,txt_ticker)
    
    id_holidays = holidays.country_holidays('ID') 
    if debug is True:
        print("Date Before : " + str(val_finance_date))
    while val_finance_date.weekday() ==5 or val_finance_date.weekday() ==6 or val_finance_date in id_holidays:
        val_finance_date =  val_finance_date + timedelta(days=1)
    
    if debug is True:    
        print("Date After Busines Working Day : " + str(val_finance_date))
    
    qry= " select close,date from stock_daily where ticker = %s "
    qry = qry + " and  date = %s  limit 1"
    
    cursor.execute(qry,(txt_ticker,val_finance_date))
    rows = cursor.fetchone() 

    if cursor.rowcount > 0:
        if debug is True:
           print( str(txt_ticker) + " Price at  : "+ str(rows[1]) + " : " + str(rows[0]) )
        return rows[0]
    else:
        print("No data set price to 0")
        print( str(txt_ticker) + " Price = 0 ")
        cl_price = 0
        return cl_price 
    
        # print("No data Contacting Market Data Provider")
        # query="""SELECT id, source_url,secret_key,number_of_call FROM db_api.stock_data_feed where number_of_call <= %s limit 1"""
        # cursor.execute(query,(api_limit,))
        # id, source_url, secret_key, number_of_call = cursor.fetchone()  
        # if cursor.rowcount > 0:
        #     #set parameter
        #     params = {
        #                 'symbols' : txt_ticker,
        #                 'access_key': secret_key,
        #                 'date_from' : val_finance_date,
        #                 'date_to': val_finance_date,
        #                 'limit' : '1000'
        #                 }
                        
                      
        #     api_result = requests.get(source_url, params)
        #     api_response = api_result.json()
        #     if debug == True:
        #             print("Parameter to be send ", params)
        #             print(" API return status code : ", api_result.status_code)  
                    
        #     if api_result.status_code == 200:
        #         cl_price=0
        #         for stock_data in api_response["data"]:     
        #             if stock_data['close'] :
        #                 print(stock_data['close'])
        #                 cl_price = stock_data['close']
           
        #     if api_result.status_code != 200:
        #                 print(" API return content for " + txt_ticker + " " + str(api_result.content))      
            
        #     qry="""update db_api.stock_data_feed set number_of_call=%s where id=%s"""
        #     number_of_call = number_of_call +1
        #     res= cursor.execute(qry,(number_of_call,id,))
        #     conn.commit()
            
            
           
        # else:
        #     return 0
        
    
    
 
def get_finance_value(cursor, table_name, txt_ticker, txt_finance_date, finance_key):
    
    if table_name == 'stock_fin_inc_stat_quarter':  
       
        qry = "select max(DATE_FORMAT(finance_date,'%%Y')) from stock_fin_inc_stat_quarter "
        qry = qry + "where ticker = %s and txt_header <> 'TTM' "
        qry = qry + "and finance_key = %s "  #'Net Income Common Stockholders'
        
        cursor.execute(qry,(txt_ticker,finance_key))
        
        rows = cursor.fetchone() 
        max_year = rows[0]
    
        val_finance_date = str(txt_finance_date).split('-')
        #print("boskuuu" + val_finance_date[0] + " max_year " + max_year)
        if int(val_finance_date[0]) == int(max_year):
            qry = "select sum(finance_value) from stock_fin_inc_stat_quarter "
            qry = qry + " where ticker = %s and txt_header <> 'TTM' "
            qry = qry + " and DATE_FORMAT(finance_date,'%%Y-%%m') <= DATE_FORMAT(%s,'%%Y-%%m') "  
            qry = qry + " and DATE_FORMAT(finance_date,'%%Y') = %s " #max_year
            qry = qry + " and finance_key = %s " #'Net Income Common Stockholders'
            cursor.execute(qry,(txt_ticker,txt_finance_date,max_year,finance_key))
            rows = cursor.fetchone() 
            if cursor.rowcount > 0:
                txt_finance_value = rows[0]
                
            else:
                txt_finance_value = 0
        
      
        if int(val_finance_date[0]) == int(max_year)-1: 
            print(" Tablename " + table_name+" val_finance_date[1] : "+ val_finance_date[1])
           
            if int(val_finance_date[1]) == 12:
                
                #print(" INI YANG 12 isi int(val_finance_date[1]) : " + str(val_finance_date[1]))
                
                qry = "select finance_value from stock_fin_inc_stat_year"
                qry = qry + " where ticker = %s and txt_header <> 'TTM' "
                qry = qry + " and finance_key = %s "
                qry = qry + " and finance_date=%s "
                
                cursor.execute(qry,(txt_ticker,finance_key, txt_finance_date))
                rows = cursor.fetchone() 
                if cursor.rowcount > 0:
                    txt_finance_value = rows[0]
                else:
                    txt_finance_value = 0
                
            if int(val_finance_date[1]) == 9 or int(val_finance_date[1]) == 3:
                
                #print(" INI YANG 9 or 3 Masuk sini isi int(val_finance_date[1]) : " + str(val_finance_date[1]))
                
                qry = "select sum(finance_value) from stock_fin_inc_stat_quarter "
                qry = qry + " where ticker = %s and txt_header <> 'TTM' "
                qry = qry + " and DATE_FORMAT(finance_date,'%%Y-%%m') <= DATE_FORMAT(%s,'%%Y-%%m') "  
                qry = qry + " and DATE_FORMAT(finance_date,'%%Y') = %s " #max_year-1
                qry = qry + " and finance_key = %s " #'Net Income Common Stockholders'
                cursor.execute(qry,(txt_ticker,txt_finance_date,int(max_year)-1,finance_key))
                rows = cursor.fetchone() 
                if cursor.rowcount > 0:
                    txt_finance_value = rows[0]
                else:
                    txt_finance_value = 0
                    
    else:
        
        qry = "select finance_value from "+ table_name +" where finance_key = %s and finance_date = %s and ticker = %s limit 1"
        print(finance_key + " finance_date : "+ str(txt_finance_date) + "txt ticker : " + txt_ticker + " query " + qry )
        cursor.execute(qry,(finance_key,txt_finance_date, txt_ticker))
        rows = cursor.fetchone() 
        if cursor.rowcount > 0:
            txt_finance_value = rows[0]
        else:
            txt_finance_value = 0
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
            print("=============")
            print (" txt_stockholders_equity*txt_unit_of_number : " + str(txt_stockholders_equity*txt_unit_of_number))
            print("txt_share_issued*txt_unit_of_number : " + str(txt_share_issued*txt_unit_of_number))
            print("round(( (txt_stockholders_equity*txt_unit_of_number)/(txt_share_issued*txt_unit_of_number) ) )*txt_rate,2 : " + str(txt_book_value) )
            print("=============")
        
        
    else:
        txt_book_value = 0
    return txt_book_value
def update_key_financial_records(conn,val_ticker,val_finance_date):
    
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
  
   
    #print('price to book : ' + str(txt_last_price) + " : " + str(txt_book_value) )
    txt_price_to_book_value = round((txt_last_price/txt_book_value),2)
    
    #print("txt_last_price " + str(txt_last_price) + " txt_book_value "  + str(txt_book_value) + " round((txt_last_price/txt_book_value),2) : " + str(round((txt_last_price/txt_book_value),2)) )
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
    qry = qry + " price_to_book_value=%s "
    
    qry = qry + " where ticker=%s "
    qry = qry + " and finance_date =%s "
    
    cursor.execute(qry,(txt_share_issued,txt_last_price,txt_stockholders_equity,txt_total_liabilities,txt_current_liabilities,txt_non_current_liabilities,txt_non_current_assets,
                        txt_current_assets,txt_total_assets,txt_net_income_stakeholders,txt_net_income_ttm,txt_book_value, txt_price_to_book_value , val_ticker,val_finance_date))
    conn.commit() 

def key_financial_processing():
    conn = MySQLdb.connect(
        # host=config.get('db_connection', 'host'),
        # user=config.get('db_connection', 'user'),
        # password=config.get('db_connection', 'pwd'),
        # database=config.get('db_connection', 'db'),
        # auth_plugin=config.get('db_connection', 'auth')
        host="localhost",
        user="root",
        password="password",
        database="db_api",
        auth_plugin='mysql_native_password'
        )
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ticker,exchange FROM stocks")
        stocklists = cursor.fetchall() 
        
        if stocklists is not None:   
            for x in stocklists:
                txt_ticker = x[0]
                # txt_ticker = 'ABMM'
               
                
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
                    
                        qry = " select count(*) rowexist from db_api.key_financials where ticker= %s and finance_date = %s and total_assets is not null" 
                        cursor.execute(qry,(bs_ticker,bs_finance_date))
                        numrow = cursor.fetchone()  
                        print("numrow ", numrow[0])
                        #if norecord
                        if numrow[0]== 0:
                            if debug == True:
                                print("Jumlah Row : " + str(numrow[0])  + " INSERT " + bs_ticker + " " + str(bs_finance_date)+ " " + str(bs_finance_key))
                            
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

                            update_key_financial_records(conn,bs_ticker,bs_finance_date)
                           
                        
                        if numrow[0] == 1:
                            if debug == True:
                                print("Jumlah Row : " + str(numrow[0])  + " UPDATE " + bs_ticker + " " + str(bs_finance_date)+ " " + str(bs_finance_key)+ " " + str(bs_finance_value) )
                            # jika total_assets sudah ada di update
                            update_key_financial_records(conn,bs_ticker,bs_finance_date) 
                # if bs_ticker=='ITMG':
                #     break
                        
                    
                        
 
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
    except Exception as ex:
        print('Generic Error caught on: '+ txt_ticker +' : ' + str(ex) )
        return None
    finally:
        conn.close

def main():
    key_financial_processing()
    
if __name__ == '__main__':
    main()