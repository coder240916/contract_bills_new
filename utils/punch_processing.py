import pandas as pd
import os

from datetime import datetime,timedelta


# Define shift timings
shift_timings = {
    "shift-1": {"start": "07:00", "break_start": "12:00", "break_end": "12:45", "end": "15:15"},
    "shift-2": {"start": "15:15", "break_start": "20:15", "break_end": "20:45", "end": "23:15"},
    "shift-B": {"start": "12:15", "break_start": "17:15", "break_end": "17:45", "end": "20:15"}
}


def generate_dates_df(month,year):

    end_of_month = pd.offsets.MonthEnd().rollforward(pd.Timestamp(f'{year}-{month}-01'))

    # Generate a pandas DataFrame with all dates for the specified month and year
    dates = pd.date_range(start=f'{year}-{month}-01', end=end_of_month, freq='D')

    # Convert the dates to a DataFrame
    dates_df = pd.DataFrame(dates, columns=['Date'])

    dates_df["sunday"] = (dates_df.Date.dt.day_of_week == 6).apply(lambda x:"sunday" if x else "weekday")
    return dates_df


def extract_punches(punch_string):

    unique_punches =[]
    punches = [p.strip() for p in punch_string.split(',')]

    for punch in punches:
      if punch not in unique_punches and punch != "":
        unique_punches.append(punch)

    # print(unique_punches)
    unique_punches = sorted([datetime.strptime(p, '%H:%M') for p in punches if p!=""])
    punch_processed = [unique_punches[0]]

    for punch in unique_punches[1:]:
        if (punch - punch_processed[-1]).total_seconds() >= 120:
            punch_processed.append(punch)
    #print([str(p.time()) for p in punch_processed])
    return [p.time() for p in punch_processed]
    #return ",".join([str(p.time()) for p in punch_processed])




# Function to determine shift based on start time within a window
def determine_shift(start_time, last_punch):
    #start_time = start_time.time()
    #last_punch_time = last_punch.time()
    for shift, timings in shift_timings.items():
        start = datetime.strptime(timings["start"], '%H:%M').time()
        end = datetime.strptime(timings["end"], '%H:%M').time()

        # Add a 30-minute buffer before and after shift start
        start_buffer = datetime.strptime(timings["start"], '%H:%M') - timedelta(minutes=15)
        end_buffer = datetime.strptime(timings["start"], '%H:%M') + timedelta(minutes=15)

        # Add a 30-minute buffer before and after shift start
        start_buffer_end = datetime.strptime(timings["end"], '%H:%M') - timedelta(minutes=15)
        end_buffer_end = datetime.strptime(timings["end"], '%H:%M') + timedelta(minutes=15)

        if ( start_time >= start_buffer.time() and start_time <= end_buffer.time() ) or (last_punch >= start_buffer_end.time() and last_punch <= end_buffer_end.time() ) :
            return shift
        elif shift == "shift-B" and last_punch > datetime.strptime("20:15", "%H:%M").time():
            return shift
    return "Unknown"


def categorize_punch(row):
    try:
      punches = row["PUNCHING_DETAILS"]
      shift = row["shift"]

      shift_timing = shift_timings[shift]
      start_time = datetime.strptime(shift_timing["start"], '%H:%M')
      break_start_time = datetime.strptime(shift_timing["break_start"], '%H:%M')
      break_end_time = datetime.strptime(shift_timing["break_end"], '%H:%M')
      end_time = datetime.strptime(shift_timing["end"], '%H:%M')

      # Define window period around each shift timing
      window_start = timedelta(minutes=-30)
      window_end = timedelta(minutes=30)

      punch_category = []

      for punch in punches:
        # Check if punch falls within the window period for each shift timing
        if (start_time + window_start).time() <= punch <= (start_time + window_end).time():
            punch_category.append( "start")
        elif (break_start_time + timedelta(minutes=-5)).time() <= punch <= (break_start_time + window_end).time():
            punch_category.append(  "break_start")
        elif (break_end_time + window_start).time() <= punch <= (break_end_time + window_end).time():
            punch_category.append(  "break_end")
        elif punch >= (end_time + timedelta(minutes=-15)).time():
            punch_category.append(  "end")
        else:
            punch_category.append(  "NP")

      return punch_category
    except Exception as e:
      return punches


# Function to calculate total working hours
def calculate_working_hours(punches):
    if len(punches) < 2:
        return timedelta(0)
    total_hours = (punches[-1] - punches[0]).total_seconds() / 3600
    return timedelta(hours=total_hours)


def fill_punches(row):
    # Define punches placeholder list
    punch_times = row["PUNCHING_DETAILS"]
    punch_cat = row["punch_cat"]

    punches_four = ["start","break_start","break_end","end"]
    punches = []

    for punch in punches_four:
      if punch in punch_cat:
        punches.append(punch_times[punch_cat.index(punch)])
      else:
        punches.append("NP")
    extra_punches = [punch for punch in punch_times if punch not in punches]
    punches_return = punches + extra_punches
    return punches_return


def get_attendance(row):
  if (row.punch_1 != "NP" and row.punch_4 != "NP" ) and (row.punch_2 == "NP" and row.punch_3 == "NP"):
    return "PP"
  elif (row.punch_1 != "NP" and row.punch_2 != "NP" ) and (row.punch_3 == "NP" or  row.punch_4 == "NP"):
    return "PA"
  elif (row.punch_1 == "NP" or row.punch_2 == "NP" ) and (row.punch_3 != "NP" and  row.punch_4 != "NP"):
    return "AP"
  else:
    return "AA"


def map_values(value):
    if value == 'PP':
        return 1
    elif value == 'AA':
        return 0
    else :  # Assuming PA or AP
        return 0.5

       
def process_punch_df(file_path,month,year):
    df = pd.read_excel(file_path)
    dates_df =  generate_dates_df(month,year)
    df = df[(df.PDATE >= dates_df.Date.values[0]) & (df.PDATE <= dates_df.Date.values[-1])]

    df.PUNCHING_DETAILS = df.PUNCHING_DETAILS.apply(lambda x:str(x)[:-3]+"," if "," not in str(x) else x).apply(extract_punches)

    df["shift"] = df['PUNCHING_DETAILS'].apply(lambda x: determine_shift(x[0],x[-1]))
    df["punch_cat"] = df.apply(categorize_punch,axis=1)
    df["punches_sorted"] = df.apply(fill_punches,axis=1)

    max_punch_count = df.punches_sorted.apply(lambda x:len(x)).max()
    # Separate punches into individual columns
    for i in range(max_punch_count):
        df[f'punch_{i+1}'] = df['punches_sorted'].apply(lambda x: x[i] if len(x) > i else None)

    df["attendance"] = df.apply(get_attendance,axis=1)

    df["date_short"] = df.PDATE.dt.strftime("%d/%m")

    df_merged = dates_df.merge(df,how="left",left_on="Date",right_on="PDATE")

    attendance_df = df_merged.pivot(
                                        index="ENAME",
                                        values =["attendance","PUNCHING_DETAILS"],
                                        columns="date_short"
                                     )

    attendance_df["attendance"] = attendance_df["attendance"].fillna("AA")

    attendance_df["PUNCHING_DETAILS"] = attendance_df["PUNCHING_DETAILS"].fillna("No Punch")


    numeric_df = attendance_df["attendance"].map(map_values)
    attendance_df.loc[:,("attendance","DP")] = numeric_df.sum(axis=1)

    punch_df = attendance_df.xs('attendance', level=0, axis=1)
    hover_df = attendance_df.xs('PUNCHING_DETAILS', level=0, axis=1)


    return punch_df,hover_df

def get_saved_punch_data(filename):
    print(filename)
    if os.path.exists(filename):
    #   print("Running the function")
      punch_df = pd.read_csv(filename)
      return punch_df
    else:
      return None
   

if __name__ == "__main__":
   attendance_df,punch_data_df =  process_punch_df("utils/punch_data.xlsx",3,2024)
   attendance_df.reset_index(inplace=True)
   html_table = attendance_df.to_html(classes='table table-bordered table-hover', index=True, escape=False,
                                header="true", table_id="editable")
   print(attendance_df.columns)
