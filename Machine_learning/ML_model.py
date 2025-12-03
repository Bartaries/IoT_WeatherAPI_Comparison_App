import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Dict, Any
import os

FILENAME = 'iot_data_full.json'
OUTPUT_FILE = 'predictions.json'

SERVER_IMG_DIR = '/static/img'
CHART_FILENAME = 'wykres_analiza.png'
CHART_OUTPUT_FILE = os.path.join(SERVER_IMG_DIR, CHART_FILENAME)

PREDICT_STEPS = 144
TIME_STEP_SECONDS = 600

CHART_META = {
    'temperature': {'label': 'Temperatura', 'unit': '°C', 'color': '#d62728', 'icon': '🌡️'},
    'humidity': {'label': 'Wilgotność Powietrza', 'unit': '%', 'color': '#1f77b4', 'icon': '💧'},
    'soil': {'label': 'Wilgotność Gleby', 'unit': '%', 'color': '#2ca02c', 'icon': '🌱'}
}

def get_cyclic_features(dt_series: pd.Series) -> pd.DataFrame:
    seconds = dt_series.dt.hour * 3600 + dt_series.dt.minute * 60 + dt_series.dt.second
    day_radians = seconds * (2 * np.pi / 86400)
    return pd.DataFrame({
        'sin_time': np.sin(day_radians),
        'cos_time': np.cos(day_radians)
    })

def predict_and_plot() -> None:
    try:
        df = pd.read_json(FILENAME)
    except (FileNotFoundError, ValueError) as e:
        print(f"CRITICAL ERROR: {e}")
        return

    df['timestamp_dt'] = pd.to_datetime(df['timestamp'], format='%d-%m-%y %H:%M:%S')

    X = get_cyclic_features(df['timestamp_dt'])
    models: Dict[str, RandomForestRegressor] = {}
    targets = ['temperature', 'humidity', 'soil']
    
    for target in targets:
        if target not in df.columns:
            continue
        
        y = df[target].values
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X, y)
        models[target] = model

    last_timestamp = df['timestamp_dt'].max()
    future_dates = [last_timestamp + timedelta(seconds=i * TIME_STEP_SECONDS) for i in range(1, PREDICT_STEPS + 1)]
    
    future_df = pd.DataFrame({'timestamp_dt': future_dates})
    future_X = get_cyclic_features(future_df['timestamp_dt'])
    
    results = future_df.copy()

    for target, model in models.items():
        raw_pred = model.predict(future_X)
        noise = np.random.normal(0, 0.1, size=len(raw_pred))
        final_pred = raw_pred + noise
        
        if target != 'temperature':
            final_pred = np.clip(np.round(final_pred), 0, 100).astype(int)
        else:
            final_pred = np.round(final_pred, 1)
            
        results[target] = final_pred

    results['timestamp'] = results['timestamp_dt'].dt.strftime('%d-%m-%y %H:%M:%S')
    
    cols_to_save = ['timestamp'] + [t for t in targets if t in results.columns]
    results[cols_to_save].to_json(OUTPUT_FILE, orient='records', indent=2)
    print(f"Saved data to: {OUTPUT_FILE}")

    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except OSError:
        plt.style.use('ggplot')

    fig, axs = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    
    plt.subplots_adjust(hspace=0.15)
    fig.suptitle('Analiza i Predykcja Warunków Środowiskowych', fontsize=20, fontweight='bold', y=0.95)

    hist_tail = df.tail(144) 

    for i, target in enumerate(targets):
        if target not in models: continue
        
        ax = axs[i]
        meta = CHART_META[target]
        
        ax.plot(hist_tail['timestamp_dt'], hist_tail[target], 
                label='Dane Historyczne', color='gray', alpha=0.6, linewidth=1.5)
        
        ax.plot(results['timestamp_dt'], results[target], 
                label='Prognoza AI', color=meta['color'], linestyle='-', linewidth=2.5)
        
        ax.plot([hist_tail['timestamp_dt'].iloc[-1], results['timestamp_dt'].iloc[0]],
                [hist_tail[target].iloc[-1], results[target].iloc[0]],
                color=meta['color'], linestyle=':', alpha=0.8)

        ax.axvline(x=last_timestamp, color='black', linestyle='--', linewidth=1, label='TERAZ')
        
        ax.set_ylabel(f"{meta['label']} [{meta['unit']}]", fontsize=12, fontweight='bold')
        ax.set_title(f"{meta['icon']} {meta['label']}", loc='left', fontsize=10, pad=10)
        ax.grid(True, which='major', linestyle='-', alpha=0.6)
        
        if i == 0:
            ax.legend(loc='upper left', frameon=True, framealpha=0.9)

    axs[-1].set_xlabel('Czas', fontsize=12, labelpad=10)
    axs[-1].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
    axs[-1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
    plt.xticks(rotation=0, ha='center')

    try:
        os.makedirs(SERVER_IMG_DIR, exist_ok=True)
        fig.savefig(CHART_OUTPUT_FILE, format='png', dpi=300, bbox_inches='tight', transparent=True)
        print(f"Chart saved to {CHART_OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving chart: {e}")

if __name__ == "__main__":
    predict_and_plot()
