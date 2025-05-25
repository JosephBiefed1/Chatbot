from datetime import datetime, timedelta
import holidays
# Example: Predict crowd level for a new sample
import pandas as pd
import joblib

#model loading
model = joblib.load('model/xgb_model.pkl')
le_crowd = joblib.load('model/label_encoder.pkl')
le_dir = joblib.load('model/direction_encoder.pkl')



def predict_crowd_level(direction):
    # Example input (replace with your actual data)
    # Get the current time
    #current_time = datetime.now()
    #current_time = datetime(2025, 5, 16, 13, 22, 0)  # Local time (naive)
    #current_time = datetime(2025, 5, 16, 13, 22, 0) + timedelta(hours=8)  # Local time (aware)
    
    # Singapore and Malaysia holidays
    #verify if direction is valid
    if direction not in ["Singapore to Malaysia", "Malaysia to Singapore"]:
        return "Invalid direction. Please use 'Singapore to Malaysia' or 'Malaysia to Singapore'."
    
    sg_holidays = holidays.country_holidays('SG', observed=True)
    my_holidays = holidays.country_holidays('MY', observed=True)
    current_time = datetime.now()

    time_of_day = current_time.time().hour
    day_of_week = current_time.date().weekday()
    month=current_time.month
    ispublic_holiday_sg = current_time.date() in sg_holidays
    iscurrent_holiday_my = current_time.date() in my_holidays
    direction = direction
    direction_encoded = le_dir.transform([direction])[0]


    # Example input (replace with your actual data)
    sample = {
        'time_of_day': time_of_day,
        'day_of_week': day_of_week,
        'month': month,
        'is_public_holiday_sg': ispublic_holiday_sg,
        'is_public_holiday_my': iscurrent_holiday_my,
        'Direction Encoded': direction_encoded,
    }
    X_new = pd.DataFrame([sample])

    # Predict
    y_pred = model.predict(X_new)
    predicted_label = le_crowd.inverse_transform(y_pred)
    return ("No recent info (within 30 min) for that direction. Predicted crowd level:", predicted_label[0])

