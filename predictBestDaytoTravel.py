import matplotlib.pyplot as plt
import pandas as pd
# Add a column for the day of the week
def main(df=None):
    if df is None:
        df = pd.read_csv(r'data\new_classified_messages_2.csv')
        df['Date'] = pd.to_datetime(df['Date'])
    else:
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'])
    # Add a column for the day of the week
    df['Day_of_Week'] = pd.to_datetime(df['Date']).dt.day_name()
    # Calculate the percentage of each crowd level per day
    day_crowd_counts = df.groupby(['Day_of_Week', 'Crowd Level']).size().unstack(fill_value=0)
    day_crowd_percent = day_crowd_counts.div(day_crowd_counts.sum(axis=1), axis=0) * 100
    # Ensure the days are in order
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_crowd_percent = day_crowd_percent.reindex(days_order)
    return day_crowd_percent

if __name__ == "__main__":
    main()