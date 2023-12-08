import requests, json

urleod='http://api.marketstack.com/v1/'
params = {
    'access_key': '53a78e9e1fc8c591ae6a6b8aa2afd04f'
    }


def getstockfileeod():
    f = open('marketstack_eod.json')
    jsdata = json.load(f)
    f.close()
    for stock_data in jsdata['data']:
       print(u'Ticker %s has a day high of  %s on %s' % (
           stock_data['symbol'],
           stock_data['high'],
           stock_data['date'],
       ))
       
    return jsdata
    
    
def getstockeod():
    api_result = requests.get('http://api.marketstack.com/v1/tickers/DJI.INDX/eod', params)
    api_response = api_result.json()
    return api_response
    
def main():
    #stock_datas = getstockfileeod()
    stock_datas = getstockeod()
    print(stock_datas)
    
    

    
if __name__ == '__main__':
    main()
