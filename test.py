import datetime as dt
import time
print(dt.datetime.now().strftime("%Y-%m-%d"))


previous = (dt.datetime.now() - dt.timedelta(30)).date().strftime("%Y-%m-%d") + " 09:30"

print(previous)
                          
 # Define the start and end dates for the loop
start_date = dt.datetime(2024, 1, 1)
end_date = dt.datetime(2024, 1, 12)  # Adjust the end date as needed

current_date = start_date                          

start_date = dt.datetime(2024, 1, 1)
end_date = dt.datetime(2024, 1, 12)  # Adjust the end date as needed
formatted_date = current_date.strftime("%Y-%m-%d")
print(formatted_date)

current_time = dt.datetime.now()
        # Approximating to the nearest 5-minute interval
approximated_minute = current_time.minute // 5 * 5
approximated_time = current_time.replace(minute=approximated_minute)

print((dt.datetime.now() - dt.timedelta(1)).date().strftime("%Y-%m-%d") + " 09:15")

print(approximated_time.strftime("%Y-%m-%d %H:%M"))
        # **********************    
                        
