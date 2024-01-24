# Function to check for the hammer pattern

def previous_pattern(candle_data):
        if(candle_data[0][4] - candle_data[-1][4]) > 0:
            return True
        else:
            return False    


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
                # logger.exception(f"Error in checking gap-up pattern for token {token}: {e}")
                return False            
                
def gapdown_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                current_open = candle_data[-1][1]
                current_close = candle_data[-1][4]
                nature_of_candle = current_close - current_open
                previous_low = candle_data[-2][3]

                if nature_of_candle < 0 and current_open < previous_low:
                    return True
                else:
                    return False

            except Exception as e:
                # logger.exception(f"Error in checking gap-up pattern for token {token}: {e}")
                return False 
            

        # Function to check for the hammer pattern
def standard_hammer_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                body = abs(candle_data[-1][4] - candle_data[-1][1])
                upper_shadow = candle_data[-1][2] - max(candle_data[-1][1], candle_data[-1][4])
                lower_shadow = abs(candle_data[-1][3] - min(candle_data[-1][1], candle_data[-1][4]))

                condition_1 = previous_pattern(candle_data) and lower_shadow > 4 * body and upper_shadow <= 0.1 * lower_shadow
                condition_2 = previous_pattern(candle_data) and upper_shadow > 4 * body and lower_shadow <= 0.1 * upper_shadow


                if condition_1 or condition_2  :
                    return True
                else:
                    return False

            except Exception as e:
                # logger.exception(f"Error in checking hammer pattern for token {token}: {e}")
                return False
                # pass        

# Function to check for the bullish engulfing pattern
def check_bullish_engulfing(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                # print("Candle data is :" , candle_data)

                last_candle = candle_data[-1][4] - candle_data[-1][1]
                previous_candle = candle_data[-2][4] - candle_data[-2][1]


                if (
                    previous_pattern(candle_data) and
                    last_candle > 0
                    and previous_candle < 0
                    and candle_data[-1][1] <= candle_data[-2][4]
                    and candle_data[-1][4] >= candle_data[-2][1]

                ):
                    return True
                else:
                    return False

            except Exception as e:
                # logger.exception(f"Error in checking bullish engulfing pattern for token {token}: {e}")
                return False
                # pass        
            
def check_bearish_engulfing(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                # print("Candle data is :" , candle_data)

                last_candle = candle_data[-1][4] - candle_data[-1][1]
                previous_candle = candle_data[-2][4] - candle_data[-2][1]


                if (
                    not(previous_pattern(candle_data)) and
                    last_candle < 0
                    and previous_candle > 0
                    and candle_data[-1][1] >= candle_data[-2][4]
                    and candle_data[-1][4] <= candle_data[-2][1]

                ):
                    return True
                else:
                    return False

            except Exception as e:
                # logger.exception(f"Error in checking bullish engulfing pattern for token {token}: {e}")
                return False
                # pass                 

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
                return False
            

def bullish_harami_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                previous_day_body = candle_data[-2][4] - candle_data[-2][1]  #this body should must be red
                current_day_body = candle_data[-1][4] - candle_data[-1][1]
                current_high,current_low = candle_data[-1][2], candle_data[-1][3]
                previous_high,previous_low = candle_data[-2][2], candle_data[-2][3]

                # print(previous_day_body < 0)
                # print(current_day_body > 0)

                # print(previous_pattern(candle_data))



                current_open, current_close = candle_data[-1][1], candle_data[-1][4]
                previous_open, previous_close = candle_data[-2][1], candle_data[-2][4]
                
                condition_1 = current_open > previous_close
                condition_2 = current_close < previous_open
                # condition_1 = current_open >= min(previous_open, previous_close)
                # condition_2 = current_close < max(previous_open, previous_close)
                condition_3 = current_day_body <= abs(0.25 * previous_day_body)
                condition_4 = current_high <= previous_high 
                condition_5 = current_low >= previous_low
                
                
                if previous_pattern(candle_data) and current_day_body > 0 and  previous_day_body < 0 and condition_1 and condition_2 and condition_3 and condition_4 and condition_5: 
                    return True
                else:
                    return False

            except Exception as e:
                return False
                # pass
            

def bearish_harami_pattern(token, historic_data):
            try:
                candle_data = historic_data.get(token)

                previous_day_body = candle_data[-2][4] - candle_data[-2][1]  #this body should must be red
                current_day_body = candle_data[-1][4] - candle_data[-1][1]
                current_high,current_low = candle_data[-1][2], candle_data[-1][3]
                previous_high,previous_low = candle_data[-2][2], candle_data[-2][3]


                current_open, current_close = candle_data[-1][1], candle_data[-1][4]
                previous_open, previous_close = candle_data[-2][1], candle_data[-2][4]
                
                condition_1 = current_open < previous_close
                condition_2 = current_close > previous_open
                # condition_1 = current_open >= min(previous_open, previous_close)
                # condition_2 = current_close < max(previous_open, previous_close)
                condition_3 = current_day_body <= abs(0.25 * previous_day_body)
                condition_4 = current_high <= previous_high 
                condition_5 = current_low >= previous_low
                
                
                if not(previous_pattern(candle_data)) and current_day_body < 0 and  previous_day_body > 0 and condition_1 and condition_2 and condition_3 and condition_4 and condition_5: 
                    return True
                else:
                    return False

            except Exception as e:
                return False
                # pass           
            

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
                # logger.exception(f"Error in checking Doji pattern for token {token}: {e}")
                return False
                # pass  





if __name__ == "__main__":
     gapup_pattern()
     bullish_harami_pattern()
     check_doji_pattern()
     bullish_piercing_pattern()
     check_bullish_engulfing()
     standard_hammer_pattern()
     gapdown_pattern()
     bearish_harami_pattern()
     check_bearish_engulfing()

            