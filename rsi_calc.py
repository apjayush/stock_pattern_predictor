# package import statement
import pandas as pd
import numpy as np
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

        with open('test.json', 'r') as json_file:
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

        def EMA(ser, n=9):
            multiplier = 2 / (n + 1)
            sma = ser.rolling(n).mean()
            ema = np.full(len(ser), np.nan)
            
            # Use iloc when accessing elements by position
            ema[len(sma) - len(sma.dropna())] = sma.dropna().iloc[0]
            
            for i in range(len(ser)):
                if not np.isnan(ema[i-1]):  
                    ema[i] = ((ser.iloc[i] - ema[i-1]) * multiplier) + ema[i-1]
            
            ema[len(sma) - len(sma.dropna())] = np.nan
            return ema

        
        def MACD(df_dict,a=12,b=26,c=9):
                for df in df_dict:
                    df["ma_fast"] = EMA(df["Close"],a)
                    df["ma_slow"] = EMA(df["Close"],b)
                    df["macd"] = df["ma_fast"] - df["ma_slow"]
                    df["signal"] = EMA(df["macd"],c)
                    df.drop(["ma_fast", "ma_slow"],axis=1,inplace=True)
            
                
    
        @retry(exceptions=(requests.exceptions.RequestException), tries=5, delay=2, backoff=2)
        def fetch_candle_data(historicParam):
            # Your code to fetch historical data here
            return smartApi.getCandleData(historicParam)["data"]        

        # Fetch historical data for all tokens to avoid redundant API calls
        historic_data = []


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
                "fromdate": "2023-05-01 09:15",     #this code reduces 30 days from current date
                "todate": "2024-01-20 15:30"
                
            }
            # candle_data = smartApi.getCandleData(historicParam)["data"]
            candle_data = fetch_candle_data(historicParam)
            # print(candle_data)
            df_data = pd.DataFrame(candle_data, columns=["Date", "Open", "High", "Low", "Close","Volume"])
            df_data.set_index("Date",inplace=True)
            historic_data.append(df_data)
            # print(df_data)
            MACD(historic_data)
            print(f"DataFrame after MACD calculations for {get_stock_name_by_token(data['token'])}:\n{historic_data[-1]}")



      

      