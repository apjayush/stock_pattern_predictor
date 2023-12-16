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


        def get_stock_name_by_token(token):
            for item in tokens_to_check:
                if(item["token"]==token):
                    return item["symbol"]       

        def previous_pattern(candle_data):
            if(candle_data[0][4] - candle_data[-1][4]) > 0:
                return True
            else:
                return False            

        # Fetch historical data for all tokens to avoid redundant API calls
        historic_data = {}

        tokens_left = len(tokens_to_check)

        for data in tokens_to_check:
            historicParam = {
                "exchange": "NSE",
                "symboltoken": data["token"],
                "interval": "ONE_DAY",
                "fromdate": "2023-08-15 09:30",
                "todate": "2023-12-15 15:30"
            }
            candle_data = smartApi.getCandleData(historicParam)["data"]
            historic_data[data["token"]] = candle_data
            # print(historic_data)
            
            # print(candle_data)
            print("Feeded historic data of token : ", data["token"] )
            # end_time = time.time()
            # execution_time = end_time - start_time
            print("Time left (mins) : ", (tokens_left * 0.4)/60)
            tokens_left = tokens_left - 1
            print("Tokens left : ", tokens_left)
            # print(len(tokens_to_check))

            time.sleep(0.2)

        # Save historic_data to a JSON file after the for loop completion, overwriting the existing file
        with open('historic_data.json', 'w') as outfile:
            json.dump(historic_data, outfile)    
            

        # Function to check for the hammer pattern
        def gapup_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                current_open = candle_data[-1][1]
                current_close = candle_data[-1][4]
                nature_of_candle = current_close - current_open
                previous_highest = candle_data[-2][2]

                if nature_of_candle > 0 and current_open > previous_highest:
                    return True
                else:
                    return False

            except Exception as e:
                logger.exception(f"Error in checking gap-up pattern for token {token}: {e}")
                return False

        # Function to check for the hammer pattern
        def check_hammer_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                body = (candle_data[-1][4] - candle_data[-1][1])
                upper_shadow = candle_data[-1][2] - max(candle_data[-1][1], candle_data[-1][4])
                lower_shadow = abs(candle_data[-1][3] - min(candle_data[-1][1], candle_data[-1][4]))

                if  previous_pattern(candle_data) and lower_shadow > 2 * body and body > 0 and upper_shadow < 2 * lower_shadow :
                    return True
                else:
                    return False

            except Exception as e:
                logger.exception(f"Error in checking hammer pattern for token {token}: {e}")
                return False

        # Function to check for the bullish engulfing pattern
        def check_bullish_engulfing(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                # print("Candle data is :" , candle_data)

                last_green_candle = candle_data[-1][4] - candle_data[-1][1]
                previous_red_candle = candle_data[-2][4] - candle_data[-2][1]


                if (
                    previous_pattern(candle_data) and
                    last_green_candle > 0
                    and previous_red_candle < 0
                    and candle_data[-1][1] <= candle_data[-2][4]
                    and candle_data[-1][4] >= candle_data[-2][1]

                ):
                    return True
                else:
                    return False

            except Exception as e:
                logger.exception(f"Error in checking bullish engulfing pattern for token {token}: {e}")
                return False
            

        def check_doji_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                # Calculate the difference between open and close prices
                price_difference = abs(candle_data[-1][1] - candle_data[-1][4])

                # Check if the difference is negligible (considering it as a Doji)
                if price_difference <= 0.001 * candle_data[-1][4] and previous_pattern(candle_data) :  # Adjustable threshold, here 0.1% of close price
                    return True
                else:
                    return False

            except Exception as e:
                logger.exception(f"Error in checking Doji pattern for token {token}: {e}")
                return False
            

        def bullish_harami_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                previous_day_body = candle_data[-2][4] - candle_data[-2][1]  #this body should must be red
                current_day_body = candle_data[-1][4] - candle_data[-1][1]

                # print(previous_day_body < 0)
                # print(current_day_body > 0)

                # print(previous_pattern(candle_data))



                current_open, current_close = candle_data[-1][1], candle_data[-1][4]
                previous_open, previous_close = candle_data[-2][1], candle_data[-2][4]
                
                condition_1 = current_open > min(previous_open, previous_close)
                condition_2 = current_close < max(previous_open, previous_close)




                if previous_pattern(candle_data) and current_day_body > 0 and  previous_day_body < 0 and condition_1 and condition_2: 
                    return True
                else:
                    return False

            except Exception as e:
                logger.exception(f"Error in checking Doji pattern for token {token}: {e}")
                return False
            

        def bullish_piercing_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                open_price, close_price = candle_data[-2][1], candle_data[-2][4]   #this is for candle before current
                current_open_price, current_close_price = candle_data[-1][1], candle_data[-1][4]   #this is for current candle

                body = close_price - open_price  #this is body for candle before current 

                # Check if the difference is negligible (considering it as a Doji)
                if previous_pattern(candle_data) and body < 0 and current_open_price <= min(open_price,close_price) and (min(open_price, close_price) + 0.5*abs(body) <=current_close_price < max(open_price, close_price)) : 
                    return True
                else:
                    return False

            except Exception as e:
                logger.exception(f"Error in checking Doji pattern for token {token}: {e}")
                return False
    

        # ... (rest of your code remains the same)

        # Loop through each token to check for patterns using fetched historical data
        bullish_engulfing_stocks = []
        hammer_stocks = []
        gapup_stocks = []
        doji_stocks = []
        bullish_piercing_stocks = []
        bullish_harami_stocks = []

        for data in tokens_to_check:
            if check_bullish_engulfing(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                bullish_engulfing_stocks.append(stock_name)

            if check_hammer_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                hammer_stocks.append(stock_name)

            if gapup_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                gapup_stocks.append(stock_name)


            if check_doji_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                doji_stocks.append(stock_name)


            if bullish_piercing_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                bullish_piercing_stocks.append(stock_name)

            if bullish_harami_pattern(data["token"], historic_data):
                stock_name = get_stock_name_by_token(data["token"])
                bullish_harami_stocks.append(stock_name)


        print("******  Break here *******")

        print("******  Break here *******")

        # Display the stocks forming the patterns
        print("Stocks forming bullish engulfing pattern:  ")
        print(bullish_engulfing_stocks)

        print("******  Break here *******")

        print("******  Break here *******")

        print("Stocks forming hammer pattern:")
        print(hammer_stocks)

        print("******  Break here *******")

        print("******  Break here *******")


        print("Stocks forming gap-up pattern:")
        print(gapup_stocks)

        print("******  Break here *******")

        print("******  Break here *******")

        print("Stocks forming doji pattern:")
        print(doji_stocks)


        print("******  Break here *******")

        print("******  Break here *******")

        print("Stocks forming piercing pattern:")
        print(bullish_piercing_stocks)

        print("******  Break here *******")

        print("******  Break here *******")

        print("Stocks forming bullish harami pattern:")
        print(bullish_harami_stocks)

   

