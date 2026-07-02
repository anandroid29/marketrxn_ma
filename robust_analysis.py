import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

offsets = list(range(-5, 6))

ar_data = {
    "HDFC-HDFC Bank Merger": [-0.001900, 0.008262, 0.008752, -0.002373, 0.014065,
                                0.081081, -0.024157, -0.027834, -0.013145, -0.008365, -0.006319],
    "Axis Bank-Citi India Consumer Business": [-0.001973, -0.004536, 0.003016, 0.016712, -0.003285,
                                0.007397, 0.016506, 0.006046, -0.009205, 0.004404, -0.003278],
    "IDFC Limited-IDFC First Bank Merger": [0.007312, -0.002535, -0.002172, 0.008269, -0.017654,
                                0.023281, -0.045132, 0.020081, -0.004864, -0.001336, -0.008034],
    "Capital One-Discover Financial": [0.017370, -0.014162, 0.000290, 0.001929, 0.010988,
                                0.007124, -0.019528, -0.027838, 0.005958, -0.004134, 0.014623],
    "UBS-Credit Suisse": [-0.032655, 0.019305, -0.038570, -0.000936, -0.043084,
                                0.026984, 0.097917, -0.031503, -0.053908, -0.000214, -0.000622],
    "First Citizens BancShares-Silicon Valley Bank": [0.096695, 0.037282, 0.013875, -0.004916, -0.016304,
                                0.535452, 0.023625, 0.015077, -0.013251, 0.029545, -0.026571],
    "JPMorgan Chase-First Republic Bank": [-0.000331, -0.008496, -0.015201, -0.004993, 0.000368,
                                0.020838, -0.006685, -0.015812, -0.008130, 0.002061, 0.001088],
    "Nasdaq-Adenza": [-0.002635, 0.018415, 0.003240, 0.005713, 0.002556,
                                -0.126328, -0.004707, 0.002062, 0.015088, -0.015586, 0.013353],
    "BlackRock-Global Infrastructure Partners": [-0.006508, -0.000634, -0.001468, -0.010394, 0.001118,
                                0.007718, -0.005384, 0.002427, -0.001931, -0.003767, -0.017210],
    "Morgan Stanley-E*TRADE": [-0.001711, -0.002392, -0.004247, -0.001930, 0.007722,
                                -0.040451, -0.010673, -0.007115, 0.007572, -0.011487, 0.020813],
    "Broadcom-VMware": [-0.036064, -0.007329, -0.058739, 0.005751, -0.000745,
                                0.006168, 0.022760, 0.001851, -0.002266, -0.022141, -0.001815],
}

crisis_deals = ["UBS-Credit Suisse", "First Citizens BancShares-Silicon Valley Bank",
                "JPMorgan Chase-First Republic Bank"]
strategic_deals = [d for d in ar_data if d not in crisis_deals]

car_df = pd.DataFrame({name: np.cumsum(ar) for name, ar in ar_data.items()}, index=offsets)

def summarize(df, label):
    caar = df.mean(axis=1)
    med  = df.median(axis=1)
    se   = df.std(axis=1) / np.sqrt(df.shape[1])
    tstat = caar / se
    pval  = 2 * (1 - stats.norm.cdf(abs(tstat)))
    out = pd.DataFrame({'CAAR': caar, 'Median_CAR': med, 't_stat': tstat, 'p_value': pval})
    out.index.name = 'day_offset'
    print(f"\n=== {label} (n={df.shape[1]}) ===")
    print(out.round(6))
    return out

full = summarize(car_df, "FULL SAMPLE (n=11)")
ex_outlier = summarize(car_df.drop(columns=["First Citizens BancShares-Silicon Valley Bank"]), "EX-FIRST CITIZENS (n=10)")
strategic = summarize(car_df[strategic_deals], "STRATEGIC / VOLUNTARY DEALS ONLY (n=8)")
crisis = summarize(car_df[crisis_deals], "CRISIS-DRIVEN DEALS ONLY (n=3)")

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(offsets, full['CAAR'], marker='o', color='#1f4e79', label='Mean CAAR (n=11, full sample)')
ax.plot(offsets, full['Median_CAR'], marker='s', color='#548235', linestyle='--', label='Median CAR (n=11, full sample)')
ax.plot(offsets, ex_outlier['CAAR'], marker='^', color='#c00000', linestyle=':', label='Mean CAAR (n=10, ex-First Citizens)')
ax.axvline(0, color='gray', linestyle='--', alpha=0.6)
ax.axhline(0, color='gray', linewidth=0.8)
ax.set_xlabel('Days relative to announcement')
ax.set_ylabel('Cumulative Abnormal Return')
ax.set_title('Market Reaction to M&A Announcements: Mean vs Median vs Outlier-Adjusted')
ax.legend()
plt.savefig('fig1')
plt.tight_layout()

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(offsets, strategic['CAAR'], marker='o', color='#1f4e79', label='Strategic/voluntary deals (n=8)')
ax.plot(offsets, crisis['CAAR'], marker='o', color='#c00000', label='Crisis-driven / FDIC-assisted deals (n=3)')
ax.axvline(0, color='gray', linestyle='--', alpha=0.6)
ax.axhline(0, color='gray', linewidth=0.8)
ax.set_xlabel('Days relative to announcement')
ax.set_ylabel('Cumulative Average Abnormal Return (CAAR)')
ax.set_title('Strategic vs. Crisis-Driven Deals: Divergent Market Reaction')
ax.legend()
plt.savefig('fig2')
plt.tight_layout()

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(offsets, full['CAAR'], marker='o', color='#1f4e79', linewidth=2)
ax.axvline(0, color='red', linestyle='--', label='Announcement day')
ax.axhline(0, color='gray', linewidth=0.8)
ax.set_xlabel('Days relative to announcement')
ax.set_ylabel('Cumulative Average Abnormal Return (CAAR)')
ax.set_title('Market Reaction to M&A Announcements')
ax.legend()
plt.savefig('fig3')
plt.tight_layout()