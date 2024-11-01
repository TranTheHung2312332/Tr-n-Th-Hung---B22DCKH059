import pandas as pd
import json
from functools import reduce
import numpy as np
import matplotlib.pylab as plt

df = pd.read_csv('data/results.csv')

df = df.replace('N/A', pd.NA)

numericFields = df.select_dtypes(include=['int64', 'float64']).columns

def findTop3():
    top_3 = {}

    for field in numericFields:
        top_3[field] = [
            {
                "id": df['id'][index],
                "name": df['name'][index],
                "position": df['position'][index],
                "team": df['team'][index],
                "value": value
            }
            for index, value in df[field].dropna().nlargest(3).items()
        ]
        
    #Lưu kết quả
    with open('data/top3.json', mode='w', encoding='utf-8') as file:
        json.dump(top_3, file, ensure_ascii=False, indent=4)
        
    #Xem chỉ số cụ thể
    return lambda stat: top_3[stat]
     
        
def find_median_mean_std():
    def find(team, index):
        filtered_player = df[df['team'].str.contains(team)]
        yield index
        yield team or "all"
        for field in numericFields:
            yield filtered_player[field].dropna().median()
            yield filtered_player[field].dropna().mean()
            yield filtered_player[field].dropna().std(ddof=0)
                
    dataResults2 = pd.DataFrame(
        columns = reduce(lambda acc, field: acc + [f'Median of {field}', f'Mean of {field}', f'Std of {field}'],
            numericFields,
            ['cid', 'team']
        )
    )
    
    index = 0
    teams = [''] + list(df['team'].unique()) # '' = 'all'
    for team in teams:
        dataResults2.loc[index] = list(find(team, index))
        index += 1
                
    #store
    with open('data/results2.csv', mode='w', encoding='utf-8', newline='') as file:    
        dataResults2.to_csv(file, index=False, encoding='utf-8')
    
    cache = {}
    def query(stat):
        if stat in cache:
            return cache[stat]
        result = {}
        medians = dataResults2[f'Median of {stat}'].values
        means = dataResults2[f'Mean of {stat}'].values
        stds = dataResults2[f'Std of {stat}'].values
        index = 0
        for team in teams:
            result[team or 'all'] = [float(medians[index]), float(means[index]), float(stds[index])]
            index += 1
            
        cache[stat] = result
        return result
    
    return query
        
def draw_histogram(field, getter):
    def getBins(data, team):
        n = len(data)
        bins = 1 + np.log2(n)
        if n < 10:
            return int(bins)
        queryRes = getter(field)
        _mean = queryRes[team][1]
        _std = queryRes[team][2]
        m3 = np.sum((data - _mean) ** 3) / n
        m2 = _std ** 2 # m2 = variance
        g1 = m3 / (m2 ** (3 / 2))
        variance_g1 = 6 * (n - 2) / ((n + 1) * (n + 3))
        return int(bins + np.log2(1 + np.fabs(g1) / np.sqrt(variance_g1)))

        
    data = df[field].dropna()
    bins=getBins(data, 'all')
    plt.hist(x=data.values, bins=bins, color='blue', edgecolor='#ccc', alpha=0.7)
    plt.title(f'{field} (all)')
    plt.xlabel(field)
    plt.ylabel('Count')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(f"visualization/hist_{field}_all.png")
        
    teams = df['team'].unique()
    
    for j in range(2):
        fig, axs = plt.subplots(2, 5)
        for i, ax in enumerate(axs.flat):
            data = df[df['team'] == teams[j * 10 + i]][field].dropna()
            bins = bins=getBins(data, teams[j * 10 + i])
            ax.hist(x=data.values, color='blue', bins=bins, edgecolor='#ccc')
            ax.set_title(teams[j * 10 + i])
            ax.set_xlabel(field)
            ax.set_ylabel('Count')
        plt.tight_layout()
        plt.savefig(f"visualization/hist_{field}_{j+1}.png")
    
    plt.show()


if __name__ == '__main__':
    found1 = findTop3()
    print(found1('performance.goals'))
    
    found2 = find_median_mean_std()
    stats = found2('performance.goals')
    for team in stats:
        print(f"{team}: {stats[team]}")
    
    draw_histogram('passing.total.Cmp%', found2)


    
