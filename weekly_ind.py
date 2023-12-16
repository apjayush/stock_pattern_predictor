from datetime import datetime, timedelta


print(datetime.now())
# Calculate 'fromdate' and 'todate' for the previous 10 weeks
end_date = datetime.now() - timedelta(days=datetime.now().weekday())  # To get the current week's end date (Friday)
start_date = end_date - timedelta(weeks=10)  # Get the start date 10 weeks before the current week


print(end_date)

print(start_date)