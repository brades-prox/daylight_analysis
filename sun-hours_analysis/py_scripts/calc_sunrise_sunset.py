

from skyfield import api
from skyfield.api import Topos, load, load_file
from datetime import datetime, timedelta
import pytz
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

ts = api.load.timescale()
eph = api.load('de421.bsp')
# Then, load the “almanac” module.
from skyfield import almanac



# define lat and long for Johannesburg and Den Haag (The Hague) 
Hague = api.wgs84.latlon(+52.0705, 4.3007)
joburg = api.wgs84.latlon(-26.1223, 28.0115)

t0 = ts.utc(2023, 1, 1, 4)
t1 = ts.utc(2023, 12, 31, 4)

times_hag, hag_events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, Hague))
times_jhb, jhb_events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, joburg))

 times_hag.utc_iso()[0::2] #1st element is the the sunrise
 times_hag.utc_iso()[1::2] #2nd the sunset

# Create a DataFrame
sunrise_sunset_df = pd.DataFrame({'Sunrise': times_hag.utc_iso()[0::2],
                                'Sunset': times_hag.utc_iso()[1::2]})

# Define a function to convert times and calculate time difference
def convert_and_calculate(df):
    df['Date'] = pd.to_datetime(df['Sunrise']).dt.date
    df['Sunrise'] = pd.to_datetime(df['Sunrise'])
    df['Sunset'] = pd.to_datetime(df['Sunset'])
    df['Daylight Hours'] = (df['Sunset'] - df['Sunrise']).dt.total_seconds() / 3600
    
    df['diff_share'] = df['Daylight Hours'] / df['Daylight Hours'].shift(1)
    df['diff_abs'] = df['Daylight Hours'] - df['Daylight Hours'].shift(1)
    df['diff_minutes'] = round(df['diff_abs'] * 60,4)
    return df


# Apply the function to the DataFrame
sunrise_sunset_clean = convert_and_calculate(sunrise_sunset_df)

# plot as line chart

# Plot the data
# Set the Seaborn style to "whitegrid" for a minimalist look
sns.set_style("whitegrid")

# Create the first plot
plot1 = sns.lineplot(data=sunrise_sunset_df, x='Date', y='Daylight Hours')
plt.title('Daylight Hours Over Time')
plt.xlabel('Date')
plt.ylabel('Daylight Hours')
plt.xticks(rotation=45)

# Create the second plot
plot2 = sns.lineplot(data=sunrise_sunset_df, x='Date', y='diff_minutes')
plt.title('Difference in Minutes Over Time')
plt.xlabel('Date')
plt.ylabel('Difference in Minutes')
plt.xticks(rotation=45)



sns.lineplot(data=sunrise_sunset_df, x='Date', y='Daylight Hours')
sns.lineplot(data=sunrise_sunset_df, x='Date', y='diff_minutes')

plt.title('Daylight Hours Over Time')
plt.xlabel('Date')
plt.ylabel('Daylight Hours')

plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

plt.tight_layout()
plt.show()





times_df = times_hag.utc_iso()
dir(times_hag)

pd.DataFrame({'Date (Local)': times_df})

# Assuming you have times_hag and times_jhb as Skyfield Time objects
# Convert times to datetime objects and then to UTC
times_hag_utc = [times_hag.utc_datetime() for t in times_hag]
times_jhb_utc = [t.utc_datetime() for t in times_jhb]

df_hag = pd.DataFrame({'Date (UTC)': times_hag_utc})

# Create a timezone object for two cities
tz_hague = pytz.timezone('Europe/Amsterdam')
tz_joburg = pytz.timezone('Africa/Johannesburg')


# Convert UTC times to local time (The Hague)
times_hague_local = [t.astimezone(tz_hague) for t in times]
times_joburg_local = [t.astimezone(tz_joburg) for t in times]

# Create a pandas DataFrame
df_hague = pd.DataFrame({'Date (UTC)': times_hag, 'Date (Local)': times_hague_local, 'Event': hag_events})

# Split the 'Event' column into 'Sunrise' and 'Sunset' columns
df_hague['Sunrise'] = df_hague['Event'].apply(lambda x: x == 'sunrise')
df_hague['Sunset'] = df_hague['Event'].apply(lambda x: x == 'sunset')

# Drop the original 'Event' column
df = df.drop('Event', axis=1)

# Print the DataFrame
print(df)
This code splits the 'Event' column into 'Sunrise' and 'Sunset' columns, where 'Sunrise' and 'Sunset' will have boolean values (True or False) indicating whether it's a sunrise or sunset event for each day. The original 'Event' column is then dropped from the DataFrame.




# Figure out local midnight.
import datetime as dt
from pytz import timezone
from skyfield import almanac
from skyfield.api import N, W, wgs84, load

zone = timezone('US/Eastern')
now = zone.localize(dt.datetime.now())
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
next_midnight = midnight + dt.timedelta(days=1)



ts = load.timescale()
t0 = ts.from_datetime(midnight)
t1 = ts.from_datetime(next_midnight)
eph = load('de421.bsp')
bluffton = wgs84.latlon(40.8939 * N, 83.8917 * W)
f = almanac.dark_twilight_day(eph, bluffton)
times, events = almanac.find_discrete(t0, t1, f)

previous_e = f(t0).item()
for t, e in zip(times, events):
    tstr = str(t.astimezone(zone))[:16]
    if previous_e < e:
        print(tstr, ' ', almanac.TWILIGHTS[e], 'starts')
    else:
        print(tstr, ' ', almanac.TWILIGHTS[previous_e], 'ends')
    previous_e = e



#------------------------------------

def calc_sunrise_sunset(lat_long, date_begin, date_end):
    # Load the ephemeris
    eph = load('de421.bsp')

    # Retrieve sunrise and sunset times
    times, events = almanac.find_discrete(date_begin, date_end, almanac.sunrise_sunset(eph, lat_long))

    # Create a DataFrame
    sunrise_sunset_df = pd.DataFrame({'Sunrise': times.utc_iso()[0::2],
                                        'Sunset': times.utc_iso()[1::2]})

    # Convert times and calculate time difference
    sunrise_sunset_df['Date'] = pd.to_datetime(sunrise_sunset_df['Sunrise']).dt.date # add date
    sunrise_sunset_df['Sunrise'] = pd.to_datetime(sunrise_sunset_df['Sunrise']) #specify sunrise time
    sunrise_sunset_df['Sunset'] = pd.to_datetime(sunrise_sunset_df['Sunset']) #specify sunset time
    sunrise_sunset_df['Daylight Hours'] = (sunrise_sunset_df['Sunset'] - sunrise_sunset_df['Sunrise']).dt.total_seconds() / 3600 # calc daylight hours 
    sunrise_sunset_df['daily_delta_share'] = sunrise_sunset_df['Daylight Hours'] / sunrise_sunset_df['Daylight Hours'].shift(1)
    sunrise_sunset_df['daily_delta_hours'] = sunrise_sunset_df['Daylight Hours'] - sunrise_sunset_df['Daylight Hours'].shift(1)
    sunrise_sunset_df['daily_delta_minutes'] = round(sunrise_sunset_df['daily_delta_hours'] * 60, 4)

    return sunrise_sunset_df

calc_sunrise_sunset(Hague, t0, t1)