import yfinance as yf
stock_info = yf.Ticker('AMZN').info
market_price = stock_info['regularMarketPrice']
previous_close_price = stock_info['regularMarketPreviousClose']
print('market price ', market_price)
print('previous close price ', previous_close_price)

