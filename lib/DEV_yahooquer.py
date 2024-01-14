from yahooquery import Ticker
import yfinance as yf


aapl = Ticker('aapl')
aapl.key_stats
# df = yf.Ticker('GOOG').history(period='4mo')[['Open', 'High', 'Low', 'Close', 'Volume']]