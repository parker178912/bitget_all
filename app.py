import bitget.mix.order_api as order
import bitget.mix.trace_api as trace
import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello"

name_list = ["superball_bitget", "Leo_bitget"]
api_key = ["bg_bdbe978bde7f282269043c1cd5f7329a", "bg_40326f574c24e54da2633e01924e2de2"]
secret_key = ["7b8068afe6edcf082908bd144cf8d82f3d45d0f7d1587538fa9b361b459d3e52", "e56f1046c3843315230942373a21eb458c48fad4dd34373d3cf06bae88bc9836"]
passphrase = ["superball", "bitgetnthpowercryptosohoot"]  # Password
size = ["0.1", "1"]

def open(symbol, side, stoplossprice, takeprofit):
    for i in range(len(name_list)):
        print(f'{name_list[i]} response -> ')
        try:
            orderApi = order.OrderApi(api_key[i], secret_key[i], passphrase[i], use_server_time=False, first=False)
            orderApi.place_order(symbol, marginCoin='USDT', size=size[i], side=side, orderType='market', timeInForceValue='normal', presetStopLossPrice=stoplossprice, presetTakeProfitPrice = takeprofit)
        except Exception as e:
            print("an exception occured - {}".format(e))
    return True

def close(symbol, closeside):
    for j in range(len(name_list)):
        print(f'{name_list[j]} response -> ')
        try:
            traceApi = trace.TraceApi(api_key[j], secret_key[j], passphrase[j], use_server_time=False, first=False)
            findorder = traceApi.current_track(symbol = symbol,productType='umcbl',pageSize=20,pageNo=1)
            datalen = len(findorder['data'])
            if datalen!=0:
                for i in range(datalen):
                    if findorder['data'][i]['holdSide'] == closeside:
                        trackno = findorder['data'][i]['trackingNo']
                        traceApi.close_track_order(symbol, trackno)
                        break
        except Exception as e:
            print("an exception occured - {}".format(e))
    return True

@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)
    symbol = "ETHUSDT_UMCBL"
    market_position = data['strategy']['market_position']
    pre_market_position = data['strategy']['prev_market_position']
    action = data['strategy']['order_action']
    try:
        stoplossprice = str(int(data['strategy']['stopLossPrice']*100)/100)
        takeprofit = str(int(data['strategy']['takeprofit']*100)/100)
    except:
        stoplossprice = None
        takeprofit = None
    if(market_position == "flat" and action == "buy"): #close short
        close(symbol, "short")
    elif(market_position == "flat" and action == "sell"): #close long
        close(symbol, "long")
    elif(market_position == "long" and action == "buy" and pre_market_position == "flat"): #long entry
        open(symbol, "open_long", stoplossprice, takeprofit)
    elif(market_position == "short" and action == "sell" and pre_market_position == "flat"): #short entry
        open(symbol, "open_short", stoplossprice, takeprofit)
    elif(market_position == "long" and action == "buy" and pre_market_position == "short"): #close short and open long
        close(symbol, "short")
        open(symbol, "open_long", stoplossprice, takeprofit)
    elif(market_position == "short" and action == "sell" and pre_market_position == "long"): #close long and open short
        close(symbol, "long")
        open(symbol, "open_short", stoplossprice, takeprofit)     
    return{
        "code":"success",
        "message":"0117 dsv "
    }    