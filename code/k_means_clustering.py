from sklearn.cluster import KMeans
from sklearn.decomposition import PCA  
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import json
import matplotlib.pyplot as plt

# position GK, DF, MF, FW

df = pd.read_csv('data/results.csv')

GK_FEATURES = [
    'goalKeeping.performance.Save%',
    'goalKeeping.performance.Saves',
    'goalKeeping.performance.CS',
    'goalKeeping.performance.CS%',
    'playingTime.minutes',
    'passing.long.Cmp',
    'passing.long.Cmp%',
    'passing.medium.Cmp',
    'passing.medium.Cmp%',
    'passing.short.Cmp',
    'passing.short.Cmp%',
    'possession.touches.Def 3rd',
    'advancedGoalkeeping.launched.Cmp',
    'advancedGoalkeeping.launched.Att',
    'advancedGoalkeeping.launched.Cmp%',
    'advancedGoalkeeping.crosses.Opp',
    'advancedGoalkeeping.crosses.Stp',
    'advancedGoalkeeping.crosses.Stp%',
    'advancedGoalkeeping.sweeper.#OPA',
    'advancedGoalkeeping.sweeper.#OPA/90',
    'advancedGoalkeeping.sweeper.AvgDist',
    'possession.touches.Def Pen',
]

DF_FEATURES = [
    'defensiveActions.tackles.Tkl',
    'defensiveActions.tackles.TklW',
    'defensiveActions.tackles.Def 3rd',
    'defensiveActions.tackles.Mid 3rd',
    'defensiveActions.tackles.Att 3rd',
    'defensiveActions.challenges.Tkl',
    'defensiveActions.challenges.Tkl%',
    'defensiveActions.challenges.Lost',
    'defensiveActions.blocks.Blocks',
    'defensiveActions.blocks.Int',
    'defensiveActions.blocks.Clr',
    'defensiveActions.blocks.Err',
    'playingTime.minutes',
    'passing.long.Cmp',
    'passing.long.Cmp%',
    'passing.medium.Cmp',
    'passing.medium.Cmp%',
    'passing.short.Cmp',
    'passing.short.Cmp%',
    'possession.touches.Def Pen',
    'possession.touches.Def 3rd',
    'possession.touches.Mid 3rd',
]

MF_FEATURES = [
    'playingTime.minutes',
    'passing.long.Cmp',
    'passing.long.Cmp%',
    'passing.medium.Cmp',
    'passing.medium.Cmp%',
    'passing.short.Cmp',
    'passing.short.Cmp%',
    'passing.expected.xA',
    'passing.expected.KP',
    'passing.expected.1/3',
    'passing.expected.CrsPA',
    'passing.expected.PrgP',
    'performance.goals',
    'performance.assits',
    'expected.xG',
    'expected.xAG',
    'shooting.standards.Sh',
    'shooting.standards.SoT',
    'passTypes.passTypes.Sw',
    'passTypes.passTypes.Crs',
    'passTypes.outcomes.Off',
    'passTypes.outcomes.Blocks',
    'goalShotCreation.SCA.SCA',
    'goalShotCreation.SCAtypes.PassLive',
    'goalShotCreation.SCAtypes.PassDead',
    'goalShotCreation.SCAtypes.TO',
    'goalShotCreation.SCAtypes.Sh',
    'goalShotCreation.SCAtypes.Fld',
    'goalShotCreation.GCA.GCA',
    'goalShotCreation.GCAtypes.PassLive',
    'goalShotCreation.GCAtypes.PassDead',
    'goalShotCreation.GCAtypes.TO',
    'defensiveActions.tackles.Tkl',
    'defensiveActions.tackles.TklW',
    'defensiveActions.challenges.Tkl',
    'defensiveActions.challenges.Lost',
    'possession.touches.Def 3rd',
    'possession.touches.Mid 3rd',
    'possession.touches.Att 3rd',
    'possession.touches.Att Pen',
    'possession.takeOns.Att',
    'possession.takeOns.Succ',
    'possession.takeOns.Succ%',
    'possession.takeOns.Tkld',
    'possession.takeOns.Tkld%',
    'possession.carries.Carries',
    'possession.carries.TotDist',
    'possession.carries.Mis',
    'possession.carries.Dis',
    'possession.receiving.Rec',
]

FW_FEATURES = [
    'playingTime.minutes',
    'passing.long.Cmp',
    'passing.long.Cmp%',
    'passing.medium.Cmp',
    'passing.medium.Cmp%',
    'passing.short.Cmp',
    'passing.short.Cmp%',
    'passing.expected.xA',
    'passing.expected.KP',
    'passing.expected.1/3',
    'passing.expected.PPA',
    'passing.expected.CrsPA',
    'performance.goals',
    'performance.assits',
    'performance.nonPenaltyGoals',
    'expected.xG',
    'expected.npxG',
    'expected.xAG',
    'shooting.standards.Sh',
    'shooting.standards.SoT',
    'shooting.standards.SoT%',
    'shooting.standards.dist',
    'shooting.standards.PK',
    'shooting.standards.PKatt',
    'goalShotCreation.GCA.GCA',
    'possession.touches.Touches',
    'possession.takeOns.Att',
    'possession.takeOns.Succ',
    'possession.takeOns.Succ%',
    'possession.takeOns.Tkld',
    'possession.takeOns.Tkld%',
    'possession.receiving.Rec',
    'miscellaneousStats.performance.Fld'
]


def elbowTest(data, position):
    X = range(1, 11)
    inertia = []
    for i in X:
        model = KMeans(n_clusters=i, random_state=42)
        model.fit(data)
        inertia.append(model.inertia_)
    plt.title(f"elbow {position}")
    plt.plot(X, inertia, marker='o')
    plt.savefig(f"visualization/elbow_{position}.png")
    plt.show()



def visualize(scaled, cluster, position):
    model = PCA(n_components=2)
    
    pca_result = model.fit_transform(scaled)

    plt.scatter(x=pca_result[:, 0], y=pca_result[:, 1], c=cluster)
    plt.title(position)
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.grid()
    plt.savefig(f"visualization/cluster_{position}.png")
    plt.show()


def clustering(position, features: list, k = 3):
    scaler = MinMaxScaler()

    clusData = df[df['position'].str.contains(position)][['id', 'name', 'team'] + features].reset_index()
    clusData = clusData.apply(lambda col: col.fillna(col.min()))
    clusDataScaled = scaler.fit_transform(clusData[features])

    elbowTest(clusDataScaled, position)

    model = KMeans(n_clusters = k, random_state = 42)
    clusData['cluster'] = model.fit_predict(clusDataScaled)
    
    visualize(scaled=clusDataScaled, cluster=clusData['cluster'], position=position)
    
    groups = clusData.groupby('cluster').agg(list).reset_index()
    output = {}
    for index, row in groups.iterrows():
        output[f'cluster-{index}'] = {
            "players": [f'{name} - {id} - {team}' for name, id, team in zip(row["name"], row['id'], row['team'])],
        }
        for feature in features:
            output[f'cluster-{index}'][feature] = np.array(row[feature]).mean()
    
    return output
    

if __name__ == '__main__':
    results = {}
    results['GK'] = clustering('GK', GK_FEATURES, 3)
    results['DF'] = clustering('DF', DF_FEATURES, 4)
    results['MF'] = clustering('MF', MF_FEATURES, 4)
    results['FW'] = clustering('FW', FW_FEATURES, 4)

    with open("data/clusters.json", mode='w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)
