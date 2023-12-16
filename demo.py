# package import statement
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import os
import requests
import time 
import json

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
        # login api call
        # logger.info(f"You Credentials: {data}")
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

        with open('output.json', 'r') as json_file:
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

        def previous_pattern(candle_data):
            if(candle_data[0][4] - candle_data[3][4]) > 0:
                return True            

        # Fetch historical data for all tokens to avoid redundant API calls
        historic_data = {}

        for data in tokens_to_check:
            if(data["token"]=="3405"):
                break
            historicParam = {
                "exchange": "NSE",
                "symboltoken": data["token"],
                "interval": "ONE_DAY",
                "fromdate": "2023-12-01 15:30",
                "todate": "2023-12-11 11:00"
            }
            time.sleep(0.5)
            candle_data = smartApi.getCandleData(historicParam)["data"]
            # print(candle_data)
            historic_data[data["token"]] = candle_data
            # print(historic_data.get(token))
            # print(historic_data)
            # print(historic_data.get(14058))
            print("Feeded historic data of token : ", data["token"] )
            

        # Function to check for the bullish engulfing pattern
        def check_bullish_engulfing(token, historic_data):
            try:
                print("Type is :", type(token))
                # print(historic_data)

                print(historic_data.get("14058")[0])

                candle_data = historic_data.get(token)

                print(candle_data)

                return True

            except Exception as e:
                logger.exception(f"Error in checking bullish engulfing pattern for token {token}: {e}")
                return False
            


        # ... (rest of your code remains the same)

        # Loop through each token to check for patterns using fetched historical data
        bullish_engulfing_stocks = []
   

        for data in tokens_to_check:
            if check_bullish_engulfing(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                print(stock_name)
                # bullish_engulfing_stocks.append(stock_name)

 
        # Display the stocks forming the patterns
        print("Stocks forming bullish engulfing pattern:")
        print(bullish_engulfing_stocks)
    

   

                
end_time = time.time()
execution_time = end_time - start_time

print(execution_time)
