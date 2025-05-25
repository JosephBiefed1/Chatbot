import matplotlib.pyplot as plt
import pandas as pd


def main(df=None, day_of_week=None):
    # day_of_week must be in full name format, e.g. 'Tuesday'
    if df is None:
        df = pd.read_csv(r'data\new_classified_messages_2.csv')
        df['Date'] = pd.to_datetime(df['Date'])
    else:
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'])
    df['Day_of_Week'] = pd.to_datetime(df['Date']).dt.day_name()
    if day_of_week is not None:
        df = df[df['Day_of_Week'] == day_of_week].copy()
    df['Hour'] = pd.to_datetime(df['Date']).dt.hour
    hour_crowd_counts = df.groupby(['Hour', 'Crowd Level']).size().unstack(fill_value=0)
    hour_crowd_percent = hour_crowd_counts.div(hour_crowd_counts.sum(axis=1), axis=0).fillna(0) * 100
    hours_order = list(range(24))
    hour_crowd_percent = hour_crowd_percent.reindex(hours_order, fill_value=0)

    return hour_crowd_percent
