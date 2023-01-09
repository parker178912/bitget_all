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


@app.route('/webhook', methods=['POST'])
def webhook():
    api_key = "bg_c93b9964acf78d8aefafc8a9fba3ae47"
    secret_key = "5999639f45fe079af6931bc7568b0da3b04397da4eed3be2f06fe9de36fb7d5b"
    passphrase = "superball"  # Password

    orderApi = order.OrderApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
    closeApi = trace.TraceApi(api_key, secret_key, passphrase, use_server_time=False, first=False)
    # get Tradingview message
    data = json.loads(request.data)
    data['strategy']['position_size'] = abs(data['strategy']['position_size'])
    if data['ticker'] == 'BTCUSDT.P':
        data['ticker'] = 'BTCUSDT'
    if data['ticker'] == 'ETHUSDT.P':
        data['ticker'] = 'ETHUSDT'   
    if data['ticker'] == 'ETCUSDT.P':
        data['ticker'] = 'ETCUSDT' 
    if data['ticker'] == 'SOLUSDT.P':
        data['ticker'] = 'SOLUSDT' 

    if data['strategy']['order_id'] == 'Short Entry':
        if data['strategy']['order_contracts']*data['strategy']['order_price']>1400:
            tracking = closeApi.current_track(symbol=data['ticker']+'_UMCBL', productType='umcbl', pageSize=20, pageNo=1)
            datalen = len(tracking['data'])
            for i in range(datalen):
                if tracking['data'][i]['holdSide'] == 'long':
                    trackingNo = tracking['data'][i]['trackingNo']
                    closeApi.close_track_order(symbol=data['ticker']+'_UMCBL',trackingNo=trackingNo)
                    orderApi.place_order(symbol=data['ticker']+'_UMCBL', marginCoin='USDT', size=data['strategy']['position_size'],side='open_short', orderType='market', timeInForceValue='normal', presetStopLossPrice=data['strategy']['order_price']*1.01)
                    break
        else:
            orderApi.place_order(symbol=data['ticker']+'_UMCBL', marginCoin='USDT', size=data['strategy']['position_size'],side='open_short', orderType='market', timeInForceValue='normal')
    if data['strategy']['order_id'] == 'Long Entry':
        if data['strategy']['order_contracts']*data['strategy']['order_price']>1400:
            tracking = closeApi.current_track(symbol=data['ticker']+'_UMCBL', productType='umcbl', pageSize=20, pageNo=1)
            datalen = len(tracking['data'])
            for i in range(datalen):
                if tracking['data'][i]['holdSide'] == 'short':
                    trackingNo = tracking['data'][i]['trackingNo']
                    closeApi.close_track_order(symbol=data['ticker']+'_UMCBL',trackingNo=trackingNo)
                    orderApi.place_order(symbol=data['ticker']+'_UMCBL', marginCoin='USDT', size=data['strategy']['position_size'],side='open_long', orderType='market', timeInForceValue='normal', presetStopLossPrice=data['strategy']['order_price']*0.99)
                    break
        else:
            orderApi.place_order(symbol=data['ticker']+'_UMCBL', marginCoin='USDT', size=data['strategy']['position_size'],side='open_long', orderType='market', timeInForceValue='normal')
    if data['strategy']['order_id'] == 'Long Exit':
        data['strategy']['order_id'] = 'close_long'
    if data['strategy']['order_id'] == 'Short Exit':
        data['strategy']['order_id'] = 'close_short'    
    if data['strategy']['order_id'] == 'Close entry(s) order Long Entry':
        data['strategy']['order_id'] = 'close_long'
    if data['strategy']['order_id'] == 'Close entry(s) order Short Entry':
        data['strategy']['order_id'] = 'close_short' 

    if data['strategy']['order_id'] == 'Close entry(s) order open_long':
        data['strategy']['order_id'] = 'close_long'
    if data['strategy']['order_id'] == 'Close entry(s) order open_short':
        data['strategy']['order_id'] = 'close_short' 

    if (data['strategy']['order_id'] == 'open_long' or data['strategy']['order_id'] == 'open_short'):
        orderApi.place_order(symbol=data['ticker']+'_UMCBL', marginCoin='USDT', size=data['strategy']['position_size'],side=data['strategy']['order_id'], orderType='market', timeInForceValue='normal')    

    if (data['strategy']['order_id'] == 'close_long'):
        tracking = closeApi.current_track(symbol=data['ticker']+'_UMCBL', productType='umcbl', pageSize=20, pageNo=1)
        datalen = len(tracking['data'])
        for i in range(datalen):
            if tracking['data'][i]['holdSide'] == 'long':
                trackingNo = tracking['data'][i]['trackingNo']
                closeApi.close_track_order(symbol=data['ticker']+'_UMCBL',trackingNo=trackingNo)
                break

    if (data['strategy']['order_id'] == 'close_short'):
        tracking = closeApi.current_track(symbol=data['ticker']+'_UMCBL', productType='umcbl', pageSize=20, pageNo=1)
        datalen = len(tracking['data'])
        for i in range(datalen):
            if tracking['data'][i]['holdSide'] == 'short':
                trackingNo = tracking['data'][i]['trackingNo']
                closeApi.close_track_order(symbol=data['ticker']+'_UMCBL',trackingNo=trackingNo)
                break

    return{
        'message':'success'
    }

    