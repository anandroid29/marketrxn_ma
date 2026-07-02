import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import timedelta
from transformers import pipeline

def get_returns(ticker, start, end):
    data = yf.download(ticker, start=start, end=end, progress=False)['Close']
    return data.pct_change().dropna()

def event_study(stock_ticker, market_ticker, event_date_str,
                 est_window=(-250, -30), event_window=(-5, 5)):
    event_date = pd.to_datetime(event_date_str)
    start = event_date + timedelta(days=est_window[0] - 10)
    end   = event_date + timedelta(days=event_window[1] + 10)

    stock_ret = get_returns(stock_ticker, start, end)
    mkt_ret   = get_returns(market_ticker, start, end)

    df = pd.concat([stock_ret, mkt_ret], axis=1).dropna()
    df.columns = ['stock', 'market']
    trading_days = df.index
    event_idx = trading_days.searchsorted(event_date)
    df['day_offset'] = np.arange(len(df)) - event_idx    

    #Estimation window: fit the market model (Rt = alpha + beta*Rm + e)
    est = df[(df['day_offset'] >= est_window[0]) & (df['day_offset'] <= est_window[1])]
    X = sm.add_constant(est['market'])
    model = sm.OLS(est['stock'], X).fit()
    alpha, beta = model.params['const'], model.params['market']

    #Event window: compute Abnormal Returns
    evt = df[(df['day_offset'] >= event_window[0]) & (df['day_offset'] <= event_window[1])].copy()
    evt['expected'] = alpha + beta * evt['market']
    evt['AR'] = evt['stock'] - evt['expected']
    evt['CAR'] = evt['AR'].cumsum()
    return evt, model

events = pd.read_csv('events.csv', parse_dates=['event_date'])
results = {}

for _, row in events.iterrows():
    evt_df, model = event_study(row['acquirer_ticker'], row['market_ticker'], row['event_date'])
    results[row['deal_name']] = evt_df

for name, evt in results.items():
    print(f"\n{name}: CAR at event day = {evt.loc[evt['day_offset']==0, 'CAR'].values}")
    print(evt[['day_offset', 'AR', 'CAR']])

from scipy import stats

def aggregate_car(results_dict, event_window=(-5, 5)):
    offsets = list(range(event_window[0], event_window[1] + 1))
    car_matrix = pd.DataFrame({
        name: evt.set_index('day_offset')['CAR'].reindex(offsets)
        for name, evt in results_dict.items()
    })
    caar = car_matrix.mean(axis=1)
    se = car_matrix.std(axis=1) / np.sqrt(car_matrix.shape[1])
    t_stats = caar / se
    p_values = 2 * (1 - stats.norm.cdf(abs(t_stats)))
    return pd.DataFrame({'CAAR': caar, 't_stat': t_stats, 'p_value': p_values}, index=offsets)

summary = aggregate_car(results)
print(summary)

import matplotlib.pyplot as plt

plt.figure(figsize=(8,5))
plt.plot(summary.index, summary['CAAR'], marker='o', color='#1f4e79')
plt.axvline(0, color='red', linestyle='--', label='Announcement day')
plt.axhline(0, color='gray', linewidth=0.8)
plt.xlabel('Days relative to announcement')
plt.ylabel('Cumulative Average Abnormal Return (CAAR)')
plt.title('Market Reaction to M&A Announcements')
plt.legend()
plt.tight_layout()
plt.savefig('caar_plot.png', dpi=150)
plt.show()

finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")

headline = "Capital One to acquire Discover in $35.3 billion all-stock deal"
result = finbert(headline)
print(result)
