import bitget.mix.market_api as market
import bitget.mix.account_api as accounts
import bitget.mix.position_api as position
import bitget.mix.order_api as order
import bitget.mix.plan_api as plan
import bitget.mix.trace_api as trace
import json, time, hmac, base64, requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello"

api_key = "bg_c93b9964acf78d8aefafc8a9fba3ae47"
secret_key = "5999639f45fe079af6931bc7568b0da3b04397da4eed3be2f06fe9de36fb7d5b"
passphrase = "superball"  # Password

marketApi = market.MarketApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
orderApi = order.OrderApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
accountApi = accounts.AccountApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
traceApi = trace.TraceApi(api_key, secret_key, passphrase, use_server_time=False, first=False)

def open(symbol, size, side):
    try:
        print(f"sending order - {side} {size} {symbol}")
        result = orderApi.place_order(symbol, marginCoin='USDT', size=size, side=side, orderType='market', timeInForceValue='normal')
        print(result)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return open

def close(symbol, closeside):
    try:
        findorder = traceApi.current_track(symbol = symbol,productType='umcbl',pageSize=20,pageNo=1)
        datalen = len(findorder['data'])
        if datalen!=0:
            for i in range(datalen):
                if findorder['data'][i]['holdSide'] == closeside:
                    trackno = findorder['data'][i]['trackingNo']
                    print(trackno)
                    traceApi.close_track_order(symbol, trackno)
                    break
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False
    return close

@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)
    if data['ticker'] == 'BTCUSDT.P' or data['ticker'] == 'BTCUSDT':
        symbol = "BTCUSDT_UMCBL"
    elif data['ticker'] == 'ETHUSDT.P' or data['ticker'] == 'ETHUSDT':
        symbol = "ETHUSDT_UMCBL"
    size = data['strategy']['order_contracts']
    market_position = data['strategy']['market_position']
    pre_market_position = data['strategy']['prev_market_position']
    action = data['strategy']['order_action']
    orderid = data['strategy']['order_id']
    if(market_position == "flat" and action == "buy"): #close short
        close(symbol, "short")
        if orderid != "close_short2":
            close(symbol, "short")
    elif(market_position == "flat" and action == "sell"): #close long
        close(symbol, "long")
        if orderid != "close_long2":        
            close(symbol, "long")
    elif(market_position == "long" and action == "buy" and pre_market_position == "flat"): #long entry
        open(symbol, size, "open_long")
        time.sleep(1.5)
        open(symbol, size, "open_long")
    elif(market_position == "short" and action == "sell" and pre_market_position == "flat"): #short entry
        open(symbol, size, "open_short")
        time.sleep(1.5)
        open(symbol, size, "open_short")
    elif(market_position == "long" and action == "sell" and pre_market_position == "long"): #close long1
        close(symbol, "long")
    elif(market_position == "short" and action == "buy" and pre_market_position == "short"): #close short1
        close(symbol, "short")
    elif(market_position == "long" and action == "buy" and pre_market_position == "short"): #close short and open long
        close(symbol, "short")
        close(symbol, "short")
        open(symbol, size, "open_long")
        time.sleep(1.5)
        open(symbol, size, "open_long")
    elif(market_position == "short" and action == "sell" and pre_market_position == "long"): #close long and open short
        close(symbol, "long")
        close(symbol, "long")
        open(symbol, size, "open_short")   
        time.sleep(1.5)
        open(symbol, size, "open_short")     
    return{
        "code":"success",
        "message":"0117 dsv "
    }    