import json
import math
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

FILENAME = 'iot_data_full.json'
OUTPUT_FILE = 'predictions.json'
PREDICT_STEPS = 144
TIME_STEP_SECONDS = 600

CHART_META = {
    'temperature': {
        'label': 'Temperatura',
        'unit': '°C',
        'color': '#d62728',
        'icon': '🌡️'
    },
    'humidity': {
        'label': 'Wilgotność Powietrza',
        'unit': '%',
        'color': '#1f77b4',
        'icon': '💧'
    },
    'soil': {
        'label': 'Wilgotność Gleby',
        'unit': '%',
        'color': '#2ca02c',
        'icon': '🌱'
    }
}

def get_cyclic_features(dt_series):
    seconds = dt_series.dt.hour * 3600 + dt_series.dt.minute * 60 + dt_series.dt.second
    day_radians = seconds * (2 * np.pi / 86400)
    return pd.DataFrame({
        'sin_time': np.sin(day_radians),
        'cos_time': np.cos(day_radians)
    })

def predict_and_plot():
    try:
        df = pd.read_json(FILENAME)
    except FileNotFoundError:
        print(f"BŁĄD: Nie ma pliku '{FILENAME}'.")
        return

    df['timestamp_dt'] = pd.to_datetime(df['timestamp'], format='%d-%m-%y %H:%M:%S')

    X = get_cyclic_features(df['timestamp_dt'])
    models = {}
    targets = ['temperature', 'humidity', 'soil']
    
    for target in targets:
        if target not in df.columns: continue
        y = df[target].values
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        models[target] = model

    last_timestamp = df['timestamp_dt'].max()
    future_dates = []
    
    for i in range(1, PREDICT_STEPS + 1):
        future_dates.append(last_timestamp + timedelta(seconds=i * TIME_STEP_SECONDS))
    
    future_dates_df = pd.DataFrame({'timestamp_dt': future_dates})
    future_X = get_cyclic_features(future_dates_df['timestamp_dt'])
    
    predictions = []
    for i, date_val in enumerate(future_dates):
        features = future_X.iloc[[i]]
        pred_record = {'timestamp_dt': date_val}
        
        for target, model in models.items():
            val = model.predict(features)[0]
            val += np.random.normal(0, 0.1)

            if target == 'temperature':
                pred_record[target] = round(val, 1)
            else:
                pred_record[target] = int(round(np.clip(val, 0, 100)))
        
        predictions.append(pred_record)

    predicted_df = pd.DataFrame(predictions)

    predicted_df['timestamp'] = predicted_df['timestamp_dt'].dt.strftime('%d-%m-%y %H:%M:%S')
    cols_to_save = ['timestamp', 'temperature', 'humidity', 'soil']
    predicted_df[cols_to_save].to_json(OUTPUT_FILE, orient='records', indent=2)
    print(f"Zapisano do {OUTPUT_FILE}")

    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except:
        pass

    fig, axs = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    plt.subplots_adjust(hspace=0.15)
    
    fig.suptitle('Analysis and Prediction of Environmental Conditions', fontsize=20, fontweight='bold', y=0.95)
    
    for i, target in enumerate(targets):
        ax = axs[i]
        meta = CHART_META[target]
        
        hist_tail = df.tail(144) 
        
        ax.plot(hist_tail['timestamp_dt'], hist_tail[target], 
                label='Historical Data', color='gray', alpha=0.6, linewidth=1.5)
        
        ax.plot(predicted_df['timestamp_dt'], predicted_df[target], 
                label='ML forecast', color=meta['color'], linestyle='-', linewidth=2.5)
        
        ax.plot([hist_tail['timestamp_dt'].iloc[-1], predicted_df['timestamp_dt'].iloc[0]],
                [hist_tail[target].iloc[-1], predicted_df[target].iloc[0]],
                color=meta['color'], linestyle=':', alpha=0.8)
        
        ax.axvline(x=last_timestamp, color='black', linestyle='--', linewidth=1, label='Moment predykcji')

        ax.set_ylabel(f"{meta['label']} [{meta['unit']}]", fontsize=12, fontweight='bold')
        ax.set_title(f"{meta['icon']} {meta['label']}", loc='left', fontsize=10, pad=10)
        
        if i == 0:
            ax.legend(loc='upper left', frameon=True, framealpha=0.9)
        
        ax.grid(True, which='major', linestyle='-', alpha=0.6)

    axs[-1].set_xlabel('Time', fontsize=12, labelpad=10)
    
    date_format = mdates.DateFormatter('%d-%m %H:%M')
    axs[-1].xaxis.set_major_formatter(date_format)
    axs[-1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
    
    plt.xticks(rotation=0, ha='center')
    plt.show()

if __name__ == "__main__":
    predict_and_plot()