import argparse
import pandas as pd
from enum import Enum
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np

class Comparator(Enum):
    GK_CMP = (
            'playingTime.minutes', 
            'goalKeeping.performance.Save%', 
            'goalKeeping.performance.CS%', 
            'advancedGoalkeeping.crosses.Stp%', 
            'possession.touches.Def 3rd'
        )
    
    DF_CMP = (
            'playingTime.minutes', 
            'defensiveActions.tackles.TklW',
            'passing.total.Cmp',
            'defensiveActions.blocks.Int',
            'defensiveActions.blocks.Clr'
          )
    
    MF_CMP = (
            'playingTime.minutes',
            'passing.total.Cmp',
            'expected.xG',
            'expected.xAG',
            'defensiveActions.tackles.TklW',
            'possession.takeOns.Succ'
        )

    FW_CMP = (
            'playingTime.minutes',
            'performance.goals',
            'performance.assits',
            'expected.xG',
            'possession.takeOns.Succ',
            'shooting.standards.SoT'
        )

    CUSTOM = ()

    def __init__(self, *attributes) -> None:
        self.attributes = list(attributes)

    def setAttributes(self, attributes):
        self.attributes = attributes
    
    def load(self, data_source):
        self.data = data_source[['id'] + self.attributes]
        scaler = MinMaxScaler()
        self.data[self.attributes] = scaler.fit_transform(self.data[self.attributes])

    def compare(self, p1, p2):
        plt.style.use('seaborn-v0_8')

        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, subplot_kw=dict(polar=True), figsize=(12, 7))
        
        N = len(self.attributes)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        for ax, p in zip((ax1, ax2), (p1, p2)): 
            id = p['id']
            player = self.data[self.data['id'] == id]
            values = list(player[self.attributes].iloc[0].values)
            values += values[:1]
            ax.plot(angles, values, alpha=0.5)
            ax.set_title(f'{p["name"]} ({id})', y=1.15)
            ax.fill(angles, values, color='blue', alpha=0.2)
            ax.set_ylim(0, 1)
            ax.set_xticks(angles[:-1])
            ax.tick_params(axis='x', pad=25)
            ax.set_xticklabels([f'{att}\n({p[att]})' for att in self.attributes])
            ax.set_yticklabels([])
        
        fig.add_artist(plt.Line2D([0.5, 0.5], [0, 1], transform=fig.transFigure, color="#ccc", linewidth=1))
        plt.tight_layout()
        plt.savefig(f'visualization/compare_{p1["name"]}_and_{p2["name"]}.png')
        plt.show()


def getPlayer(players_df):
    if len(players_df) == 0:
        raise Exception('Player is not found !')
    
    if len(players_df) < 2:
        return players_df.iloc[0]
    
    for index in players_df.index:
        player = players_df.iloc[index]
        print(f'{index}. {player["name"]} - {player["id"]} - {player["team"]}')

    print('Enter index of your player chosen: ', end='')
    
    try: return players_df.iloc[int(input())]
    except: raise Exception('Invalid index')


def getCmp(attributes, pos1, pos2):
    if attributes:
        cmp = Comparator.CUSTOM
        cmp.setAttributes([att.strip() for att in attributes.split(',')])
        return cmp
    
    for pos in pos1.split(','):
        if pos2.__contains__(pos):
            return Comparator[f'{pos}_CMP']
        
    raise Exception('Please input param "--Attribute" or choose 2 players with the same position')


if __name__ == '__main__':
    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument('--p1', required=True, help='Name player1')
        parser.add_argument('--p2', required=True, help='Name player2')
        parser.add_argument('--Attribute', required=False, help='List of att, delimeter = ","')

        # Example:
        # python code/radarChartPlot.py --p1 "Haaland" --p2 "Foden"
        # python code/radarChartPlot.py --p1 "Onana" --p2 "Ederson"
        # python code/radarChartPlot.py --p1 "Rodri" --p2 "Declan Rice"
        # python code/radarChartPlot.py --p1 "Haaland" --p2 "Foden" 
        #       --Attribute "playingTime.minutes,performance.goals,performance.assits,expected.npxG,passing.total.Cmp"


        args = parser.parse_args()

        df = pd.read_csv('data/results.csv')

        p1 = getPlayer(df[df['name'].str.contains(args.p1, case=False)].reset_index())
        p2 = getPlayer(df[df['name'].str.contains(args.p2, case=False)].reset_index())
        
        cmp = getCmp(args.Attribute, p1['position'], p2['position'])
        cmp.load(df)

        cmp.compare(p1, p2)

    except Exception as e:
        print(e)



    