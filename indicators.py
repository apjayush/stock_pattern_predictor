# package import statement
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import os
import requests
import time 

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

    # URL to access
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'

    # Send a GET request to the URL
    response = requests.get(url, timeout=5)
   

    # Check if the request was successful (status code 200 indicates success)
    if response.status_code == 200:
        # Print the content of the response (HTML content for a website, for example)
        # print(response.json())if

        data = response.json()
        tokens_to_check = []


        for index,item in enumerate(data):
            if index >= 5000:  # Limit the iteration to the first 3000 items
                break
            else:
                if item.get('symbol', '').endswith('-EQ') and item.get('exch_seg') == 'NSE':
                    # print(item["token"]+ " : " + item["name"])
                    tokens_to_check.append(item["token"])


        def get_stock_name_by_token(token):
            for item in data:
                if(item["token"]==token):
                    return item["name"]       

        def previous_pattern(candle_data):
            if(candle_data[0][4] - candle_data[3][4]) > 0:
                return True            

        # Fetch historical data for all tokens to avoid redundant API calls
        historic_data = {}

        for token in tokens_to_check:
            historicParam = {
                "exchange": "NSE",
                "symboltoken": token,
                "interval": "ONE_DAY",
                "fromdate": "2023-12-01 15:30",
                "todate": "2023-12-11 11:00"
            }
            time.sleep(0.5)
            candle_data = smartApi.getCandleData(historicParam)["data"]
            historic_data[token] = candle_data


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

                if lower_shadow > 2 * body and body > 0 and upper_shadow < 2 * lower_shadow:
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

                last_green_candle = candle_data[-1][4] - candle_data[-2][1]
                previous_red_candle = candle_data[-2][4] - candle_data[-2][1]

                if (
                    last_green_candle > 0
                    and previous_red_candle < 0
                    and candle_data[-1][1] <= candle_data[-2][4]
                    and candle_data[-1][4] > candle_data[-2][1]
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
                if price_difference <= 0.001 * candle_data[-1][4]:  # Adjustable threshold, here 0.1% of close price
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

        for token in tokens_to_check:
            if check_bullish_engulfing(token, historic_data):
                stock_name = get_stock_name_by_token(token)
                bullish_engulfing_stocks.append(stock_name)

            if check_hammer_pattern(token, historic_data):
                stock_name = get_stock_name_by_token(token)
                hammer_stocks.append(stock_name)

            if gapup_pattern(token, historic_data):
                stock_name = get_stock_name_by_token(token)
                gapup_stocks.append(stock_name)


            if check_doji_pattern(token, historic_data):
                stock_name = get_stock_name_by_token(token)
                doji_stocks.append(stock_name)



        # Display the stocks forming the patterns
        print("Stocks forming bullish engulfing pattern:")
        print(bullish_engulfing_stocks)
        print("Stocks forming hammer pattern:")
        print(hammer_stocks)
        print("Stocks forming gap-up pattern:")
        print(gapup_stocks)
        print("Stocks forming doji pattern:")
        print(doji_stocks)


    else:
        # If the request was not successful, print the status code
                print(f"Failed to fetch the URL. Status code: {response.status_code}")
  
                
end_time = time.time()
execution_time = end_time - start_time

print(execution_time)
# ... (rest of your code remains the same)
