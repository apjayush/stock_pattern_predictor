# package import statement
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import os
import requests
import time 
import json
import datetime as dt
from retry import retry
import telebot
import candlesticks_pattern


start_time = time.time()


key_path = "/home/ayush/Desktop/angelone_smartapi/angelOne"
os.chdir(key_path)


key_secret = open("keys.txt","r").read().split()

# print(key_secret)

api_key = key_secret[0]
username = key_secret[2]
pwd = key_secret[3]
smartApi = SmartConnect(api_key)
try:
    token = key_secret[5]
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
data = smartApi.generateSession(username, pwd, totp)

if data['status'] == False:
    logger.error(data)
    
else:
        print("Connection sucess")
        authToken = data['data']['jwtToken']
        refreshToken = data['data']['refreshToken']
        # fetch the feedtoken
        feedToken = smartApi.getfeedToken()
        # fetch User Profile
        res = smartApi.getProfile(refreshToken)
        smartApi.generateToken(refreshToken)
        res=res['data']['exchanges']



    # # URL to access
    # url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'

    # # Send a GET request to the URL
    # response = requests.get(url, timeout=5)

        tokens_to_check = []

        with open('Nifty_500.json', 'r') as json_file:
            json_data = json.load(json_file)

# Append JSON data to tokens_to_check array
        for item in json_data:
            token_symbol_dict = {"token": item["token"], "symbol": item["symbol"]}
            tokens_to_check.append(token_symbol_dict)

        # print(tokens_to_check)    


        def get_stock_name_by_token(token):
            for item in tokens_to_check:
                if(item["token"]==token):
                    return item["symbol"]       


        @retry(exceptions=(requests.exceptions.RequestException), tries=5, delay=2, backoff=2)
        def fetch_candle_data(historicParam):
            # Your code to fetch historical data here
            return smartApi.getCandleData(historicParam)["data"]        

        # Fetch historical data for all tokens to avoid redundant API calls
        historic_data = {}


        tokens_left = len(tokens_to_check)

        # ******this below code is used to fetch latest time which is nearest to 5
        current_time = dt.datetime.now()
        # Approximating to the nearest 5-minute interval
        approximated_minute = current_time.minute // 5 * 5
        approximated_time = current_time.replace(minute=approximated_minute)
        # **********************

        for data in tokens_to_check:
            historicParam = {
                "exchange": "NSE",
                "symboltoken": data["token"],
                "interval": "ONE_DAY",
                # "fromdate": (dt.datetime.now() - dt.timedelta(30)).date().strftime("%Y-%m-%d") + " 09:15",     
                # "todate": approximated_time.strftime("%Y-%m-%d %H:%M")
                "fromdate": "2024-01-01 09:15",     #this code reduces 30 days from current date
                "todate": "2024-01-24 12:35"
                
            }
            # candle_data = smartApi.getCandleData(historicParam)["data"]
            candle_data = fetch_candle_data(historicParam)
            historic_data[data["token"]] = candle_data
            # print(historic_data)
            
            # print(candle_data)
            # print("Feeded historic data of token : ", data["token"] )
            # end_time = time.time()
            # execution_time = end_time - start_time
            print("Time left (mins) : ", (tokens_left * 0.4)/60)
            tokens_left = tokens_left - 1
            print("Tokens left : ", tokens_left)
            # print(len(tokens_to_check))

            time.sleep(0.22)

        # Save historic_data to a JSON file after the for loop completion, overwriting the existing file
        with open('historic_data.json', 'w') as outfile:
            json.dump(historic_data, outfile)    
            

        # Loop through each token to check for patterns using fetched historical data
        bullish_engulfing_stocks = []
        bearish_engulfing = []
        hammer_stocks = []
        gapup_stocks = []
        doji_stocks = []
        bullish_piercing_stocks = []
        bullish_harami_stocks = []
        gapdown_stocks = []
        bearish_harami = []

        for data in tokens_to_check:
            if candlesticks_pattern.check_bullish_engulfing(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                bullish_engulfing_stocks.append(stock_name)

            if candlesticks_pattern.standard_hammer_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                hammer_stocks.append(stock_name)

            if candlesticks_pattern.gapup_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                gapup_stocks.append(stock_name)


            if candlesticks_pattern.check_doji_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                doji_stocks.append(stock_name)


            if candlesticks_pattern.bullish_piercing_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                bullish_piercing_stocks.append(stock_name)

            if candlesticks_pattern.bullish_harami_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                bullish_harami_stocks.append(stock_name)


            if candlesticks_pattern.gapdown_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                gapdown_stocks.append(stock_name)

            if candlesticks_pattern.bearish_harami_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                bearish_harami.append(stock_name)


            if candlesticks_pattern.check_bearish_engulfing(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                bearish_engulfing.append(stock_name)


        print("******  Break here *******")


        # Display the stocks forming the patterns
        print("Stocks forming bullish engulfing pattern:  ")
        print(bullish_engulfing_stocks)

        print("******  Break here *******")


        print("Stocks forming bearish engulfing pattern:  ")
        print(bearish_engulfing)

        print("******  Break here *******")


        print("Stocks forming hammer pattern:")
        print(hammer_stocks)

        print("******  Break here *******")



        print("Stocks forming gap-up pattern:")
        print(gapup_stocks)

        print("******  Break here *******")




        print("Stocks forming gap-down pattern:")
        print(gapdown_stocks)

        print("******  Break here *******")


        print("Stocks forming doji pattern:")
        print(doji_stocks)


        print("******  Break here *******")


        print("Stocks forming piercing pattern:")
        print(bullish_piercing_stocks)

        print("******  Break here *******")


        print("Stocks forming bullish harami pattern:")
        print(bullish_harami_stocks)

        print("******  Break here *******")


        print("Stocks forming bearish harami pattern:")
        print(bearish_harami)