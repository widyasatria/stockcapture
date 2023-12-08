import requests, json

base_url='http://api.marketstack.com/v1/'
access_key='53a78e9e1fc8c591ae6a6b8aa2afd04f'


def getstockfileeod():
    f = open('marketstack_eod.json')
    jsdata = json.load(f)
    f.close()
    return jsdata
    
    
def getstockeod(access_key,symbols):
    url= base_url +'eod?access_key='+ access_key +'&symbols='+ symbols
    #print(url)
    api_result=requests.get(url)
    api_response = api_result.json()
    return api_response
    
def main():
    #stock_datas = getstockfileeod()
    stock_datas = getstockeod(access_key,'BBNI.XIDX')
    #print(stock_datas)
    
    for stock_data in stock_datas['data']:
        print(stock_data['symbol'])
        print(stock_data['open'])
        print(stock_data['high'])
        print(stock_data['low'])
        print(stock_data['close'])
        print(stock_data['volume'])
        print(stock_data['adj_high'])
        print(stock_data['adj_low'])
        print(stock_data['adj_close'])
        print(stock_data['adj_open'])
        print(stock_data['split_factor'])
        print(stock_data['dividend'])
        print(stock_data['exchange'])
        print(stock_data['date'])
        
    

    
if __name__ == '__main__':
    main()
