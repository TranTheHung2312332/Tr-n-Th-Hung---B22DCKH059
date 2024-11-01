import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_json("data/clubs.json")

for stat in df.select_dtypes(include=['int64', 'float64']).keys():
    highest = df[df[stat] == df[stat].max()]
    print(f'Highest {stat}:')
    for index, club in highest.iterrows():
        print(f'  - {club["name"]} = {club[stat]}')
    print()

#Real Result Performance
# index = rank
df['RP'] = 43 * np.log10(((20 - df.index) * 0.5 + 0.5)) / np.log10(10.5) + df['points'] / 2

#Offensive-Defensive Performance
df['ODP'] =  df['goals'] - 0.75 * df['goalsAgainst']
df['ODP'] = (df['ODP'] - np.min(df['ODP'])) / (np.max(df['ODP']) - np.min(df['ODP'])) * 100

#Expected Performance
df['EP'] = df['xG'] - 0.75 * df['xGA']
df['EP'] = (df['EP'] - np.min(df['EP'])) / (np.max(df['EP']) - np.min(df['EP'])) * 100

#Performance value
df['PV'] = 0.5 * df['RP'] + 0.3 * df['ODP'] + 0.2 * df['EP']

df = df.sort_values(by='PV', ascending=False)
print(df['PV'])


plt.barh(df['name'], df['PV'], color='skyblue')
plt.title("Performance of EPL clubs 2023 - 2024")
plt.gca().invert_yaxis()
plt.savefig("visualization/hist_club_performances.png")
plt.show()
