import bs4
import requests
import json
import time

BASE_URL = "https://fbref.com"
EPL_23_24_PATH = "/en/comps/9/2023-2024/2023-2024-Premier-League-Stats"

response = requests.get(BASE_URL + EPL_23_24_PATH)
document = bs4.BeautifulSoup(response.text, 'html.parser') #tạo đối tượng bs4.BeautifulSoup

def fetch(url):
    res = requests.get(url)
    return bs4.BeautifulSoup(res.text, 'html.parser')

def f(container, selector, cast = str):
    try: return cast(container.select_one(selector).get_text())
    except: return 'N/A'  
       
def crawlPlayers():
    def getNation(url):
        # example: /en/country/ENG/England-Football
        if not url: return None
        return url.split('/')[4][0:-9]
    
    players = []
     
    for linkElement in document.select('#stats_squads_keeper_for tbody tr a'):
        link = linkElement['href']
        page = fetch(BASE_URL + link)
        
        standard_stats = page.select('#stats_standard_9 tbody tr')
        
        keeper_table = page.select_one('#stats_keeper_9 tbody')  #goalKeeping
        advanced_GK_table = page.select_one('#stats_keeper_adv_9')
        shooting_table = page.select_one('#stats_shooting_9 tbody') #shooting
        passing_table = page.select_one('#stats_passing_9 tbody') #passing
        pass_types = page.select_one('#stats_passing_types_9 tbody') #passType
        gca_table = page.select_one('#stats_gca_9 tbody') #gca
        def_actions = page.select_one('#stats_defense_9 tbody') #defensive
        possesion_table = page.select_one('#stats_possession_9 tbody') #possesion
        playing_time = page.select_one('#stats_playing_time_9 tbody') #playingTime
        miscellaneous_table = page.select_one('#stats_misc_9 tbody') #Miscellaneous_stats
        
        team = linkElement.get_text()
        print(f'start scan {team}:')
        
        index = 0
        for row in standard_stats:
            
            minutesPlaying = f(row, '[data-stat="minutes"]', lambda r: int(r.replace(',', '')))
            if minutesPlaying == 'N/A' or minutesPlaying < 90:
                continue
            
            id = row.select_one('th')['data-append-csv']
            selector = f'tr:has(th[data-append-csv="{id}"])' #css selector
                
            print(f'player {index}') 
            player = {
                "id": id,
                "name": f(row, 'th a'),
                "nation": getNation(row.select_one('[data-stat="nationality"] a')['href']),
                "team": team, 
                "position": f(row, '[data-stat="position"]'),
                "age": f(row, '[data-stat="age"]', int),
                "playingTime": {
                    "matchesPlayed": f(row, '[data-stat="games"]', int),
                    "starts": f(row, '[data-stat="games_starts"]', int),
                    "minutes": minutesPlaying
                },
                "performance": {
                    "nonPenaltyGoals": f(row, '[data-stat="goals_pens"]', int),
                    "goals": f(row, '[data-stat="goals"]', int),
                    "assits": f(row, '[data-stat="assists"]', int),
                    "yellowCards": f(row, '[data-stat="cards_yellow"]', int),
                    "redCards": f(row, '[data-stat="cards_red"]', int),
                },
                "expected": {
                    "xG": f(row, '[data-stat="xg"]', float),
                    "npxG": f(row, '[data-stat="npxg"]', float),
                    "xAG": f(row, '[data-stat="xg_assist"]', float)
                },
                "progression": {
                    "prgC": f(row, '[data-stat="progressive_carries"]', int),
                    "prgP": f(row, '[data-stat="progressive_passes"]', int),
                    "prgR": f(row, '[data-stat="progressive_passes_received"]', int)
                },
                "per90Minutes": {
                    "Gls": f(row, '[data-stat="goals_per90"]', float),
                    "Ast": f(row, '[data-stat="assists_per90"]', float),
                    "G+A": f(row, '[data-stat="goals_assists_per90"]', float),
                    "G-PK": f(row, '[data-stat="goals_pens_per90"]', float),
                    "G+A-PK": f(row, '[data-stat="goals_assists_pens_per90"]', float),
                    "xG": f(row, '[data-stat="xg_per90"]', float),
                    "xAG": f(row, '[data-stat="xg_assist_per90"]', float),
                    "xG+xAG": f(row, '[data-stat="xg_xg_assist_per90"]', float),
                    "npxG": f(row, '[data-stat="npxg_per90"]', float),
                    "npxG+xAG": f(row, '[data-stat="npxg_xg_assist_per90"]', float)
                },
                "goalKeeping": {
                    "performance": {
                        "GA": f(keeper_table.select_one(selector), '[data-stat="gk_goals_against"]', int),
                        "GA90": f(keeper_table.select_one(selector), '[data-stat="gk_goals_against_per90"]', float),
                        "SoTA": f(keeper_table.select_one(selector), '[data-stat="gk_shots_on_target_against"]', int),
                        "Saves": f(keeper_table.select_one(selector), '[data-stat="gk_saves"]', int),
                        "Save%": f(keeper_table.select_one(selector), '[data-stat="gk_save_pct"]', float),
                        "W": f(keeper_table.select_one(selector), '[data-stat="gk_wins"]', int),
                        "D": f(keeper_table.select_one(selector), '[data-stat="gk_ties"]', int),
                        "L": f(keeper_table.select_one(selector), '[data-stat="gk_losses"]', int),
                        "CS": f(keeper_table.select_one(selector), '[data-stat="gk_clean_sheets"]', int),
                        "CS%": f(keeper_table.select_one(selector), '[data-stat="gk_clean_sheets_pct"]', float)
                    },
                    "penaltyKicks": {
                        "PKatt": f(keeper_table.select_one(selector), '[data-stat="gk_pens_att"]', int),
                        "PKA": f(keeper_table.select_one(selector), '[data-stat="gk_pens_allowed"]', int),
                        "PKsv": f(keeper_table.select_one(selector), '[data-stat="gk_pens_saved"]', int),
                        "PKm": f(keeper_table.select_one(selector), '[data-stat="gk_pens_missed"]', int),
                        "Save%": f(keeper_table.select_one(selector), '[data-stat="gk_pens_save_pct"]', float)
                    }
                },
                "advancedGoalkeeping": {
                    "goals": {
                        "GA": f(advanced_GK_table.select_one(selector), '[data-stat="gk_goals_against"]', int),
                        "PKA": f(advanced_GK_table.select_one(selector), '[data-stat="gk_pens_allowed"]', int),
                        "FK": f(advanced_GK_table.select_one(selector), '[data-stat="gk_free_kick_goals_against"]', int),
                        "CK": f(advanced_GK_table.select_one(selector), '[data-stat="gk_corner_kick_goals_against"]', int),
                        "OG": f(advanced_GK_table.select_one(selector), '[data-stat="gk_own_goals_against"]', int)
                    },
                    "expected": {
                        "PSxG": f(advanced_GK_table.select_one(selector), '[data-stat="gk_psxg"]', float),
                        "PSxG/SoT": f(advanced_GK_table.select_one(selector), '[data-stat="gk_psnpxg_per_shot_on_target_against"]', float),
                        "PSxG+/-": f(advanced_GK_table.select_one(selector), '[data-stat="gk_psxg_net"]', float),
                        "/90": f(advanced_GK_table.select_one(selector), '[data-stat="gk_psxg_net_per90"]', float)
                    },
                    "launched": {
                        "Cmp": f(advanced_GK_table.select_one(selector), '[data-stat="gk_passes_completed_launched"]', int),
                        "Att": f(advanced_GK_table.select_one(selector), '[data-stat="gk_passes_launched"]', int),
                        "Cmp%": f(advanced_GK_table.select_one(selector), '[data-stat="gk_passes_pct_launched"]', float)
                    },
                    "passes": {
                        "Att(GK)": f(advanced_GK_table.select_one(selector), '[data-stat="gk_passes"]', int),
                        "Thr": f(advanced_GK_table.select_one(selector), '[data-stat="gk_passes_throws"]', int),
                        "Launch%": f(advanced_GK_table.select_one(selector), '[data-stat="gk_pct_passes_launched"]', float),
                        "AvgLen": f(advanced_GK_table.select_one(selector), '[data-stat="gk_goal_kick_length_avg"]', float)
                    },
                    "goalKicks": {
                        "Att": f(advanced_GK_table.select_one(selector), '[data-stat="gk_goal_kicks"]', int),
                        "Launch%": f(advanced_GK_table.select_one(selector), '[data-stat="gk_pct_goal_kicks_launched"]', float),
                        "AvgLen": f(advanced_GK_table.select_one(selector), '[data-stat="gk_goal_kick_length_avg"]', float)
                    },
                    "crosses": {
                        "Opp": f(advanced_GK_table.select_one(selector), '[data-stat="gk_crosses"]', int),
                        "Stp": f(advanced_GK_table.select_one(selector), '[data-stat="gk_crosses_stopped"]', int),
                        "Stp%": f(advanced_GK_table.select_one(selector), '[data-stat="gk_crosses_stopped_pct"]', float)
                    },
                    "sweeper": {
                        "#OPA": f(advanced_GK_table.select_one(selector), '[data-stat="gk_def_actions_outside_pen_area"]', int),
                        "#OPA/90": f(advanced_GK_table.select_one(selector), '[data-stat="gk_pens_allowed"]', float),
                        "AvgDist": f(advanced_GK_table.select_one(selector), '[data-stat="gk_avg_distance_def_actions"]', float)
                    },
                },
                "shooting": {
                    "standards": {
                        "Gls": f(shooting_table.select_one(selector), '[data-stat="goals"]', int),
                        "Sh": f(shooting_table.select_one(selector), '[data-stat="shots"]', int),
                        "SoT": f(shooting_table.select_one(selector), '[data-stat="shots_on_target"]', int),  
                        "SoT%": f(shooting_table.select_one(selector), '[data-stat="shots_on_target_pct"]', float),
                        "Sh/90": f(shooting_table.select_one(selector), '[data-stat="shots_per90"]', float),
                        "SoT/90": f(shooting_table.select_one(selector), '[data-stat="shots_on_target_per90"]', float),
                        "G/Sh": f(shooting_table.select_one(selector), '[data-stat="goals_per_shot"]', float),
                        "G/SoT": f(shooting_table.select_one(selector), '[data-stat="goals_per_shot_on_target"]', float),
                        "dist": f(shooting_table.select_one(selector), '[data-stat="average_shot_distance"]', float),
                        "FK": f(shooting_table.select_one(selector), '[data-stat="shots_free_kicks"]', int),
                        "PK": f(shooting_table.select_one(selector), '[data-stat="pens_made"]', int),
                        "PKatt": f(shooting_table.select_one(selector), '[data-stat="pens_att"]', int)
                    },
                    "expected": {
                        "xG": f(shooting_table.select_one(selector), '[data-stat="xg"]', float),
                        "npxG": f(shooting_table.select_one(selector), '[data-stat="npxg"]', float),
                        "npxG/Sh": f(shooting_table.select_one(selector), '[data-stat="npxg_per_shot"]', float),
                        "G-xG": f(shooting_table.select_one(selector), '[data-stat="xg_net"]', float),
                        "np:G-xG": f(shooting_table.select_one(selector), '[data-stat="npxg_net"]', float)
                    }
                },
                "passing": {
                    "total": {
                        "Cmp": f(passing_table.select_one(selector), '[data-stat="passes_completed"]', int),
                        "Att": f(passing_table.select_one(selector), '[data-stat="passes"]', int),
                        "Cmp%": f(passing_table.select_one(selector), '[data-stat="passes_pct"]', float),
                        "TotDist": f(passing_table.select_one(selector), '[data-stat="passes_total_distance"]', int),
                        "PrgDist": f(passing_table.select_one(selector), '[data-stat="passes_progressive_distance"]', int)
                    },
                    "short": {
                        "Cmp": f(passing_table.select_one(selector), '[data-stat="passes_completed_short"]', int),
                        "Att": f(passing_table.select_one(selector), '[data-stat="passes_short"]', int),
                        "Cmp%": f(passing_table.select_one(selector), '[data-stat="passes_pct_short"]', float)
                    },
                    "medium": {
                        "Cmp": f(passing_table.select_one(selector), '[data-stat="passes_completed_medium"]', int),
                        "Att": f(passing_table.select_one(selector), '[data-stat="passes_medium"]', int),
                        "Cmp%": f(passing_table.select_one(selector), '[data-stat="passes_pct_medium"]', float)
                    },
                    "long": {
                        "Cmp": f(passing_table.select_one(selector), '[data-stat="passes_completed_long"]', int),
                        "Att": f(passing_table.select_one(selector), '[data-stat="passes_long"]', int),
                        "Cmp%": f(passing_table.select_one(selector), '[data-stat="passes_pct_long"]', float)
                    },
                    "expected": {
                        "Ast": f(passing_table.select_one(selector), '[data-stat="assists"]', int),
                        "xAG": f(passing_table.select_one(selector), '[data-stat="xg_assist"]', float),
                        "xA": f(passing_table.select_one(selector), '[data-stat="xg_assist"]', float),
                        "A-xAG": f(passing_table.select_one(selector), '[data-stat="xg_assist_net"]', float),
                        "KP": f(passing_table.select_one(selector), '[data-stat="assisted_shots"]', int),
                        "1/3": f(passing_table.select_one(selector), '[data-stat="passes_into_final_third"]', int),
                        "PPA": f(passing_table.select_one(selector), '[data-stat="passes_into_penalty_area"]', int),
                        "CrsPA": f(passing_table.select_one(selector), '[data-stat="crosses_into_penalty_area"]', int),
                        "PrgP": f(passing_table.select_one(selector), '[data-stat="progressive_passes"]', int)
                    }
                },
                "passTypes": {
                    "passTypes": {
                        "Live": f(pass_types.select_one(selector), '[data-stat="passes_live"]', int),
                        "Dead": f(pass_types.select_one(selector), '[data-stat="passes_dead"]', int),
                        "FK": f(pass_types.select_one(selector), '[data-stat="passes_free_kicks"]', int),
                        "TB": f(pass_types.select_one(selector), '[data-stat="through_balls"]', int),
                        "Sw": f(pass_types.select_one(selector), '[data-stat="passes_switches"]', int),
                        "Crs": f(pass_types.select_one(selector), '[data-stat="crosses"]', int),
                        "TI": f(pass_types.select_one(selector), '[data-stat="throw_ins"]', int),
                        "CK": f(pass_types.select_one(selector), '[data-stat="corner_kicks"]', int)
                    },
                    "cornerKicks": {
                        "In": f(pass_types.select_one(selector), '[data-stat="corner_kicks_in"]', int),
                        "Out": f(pass_types.select_one(selector), '[data-stat="corner_kicks_out"]', int),
                        "Str": f(pass_types.select_one(selector), '[data-stat="corner_kicks_straight"]', int)
                    },
                    "outcomes": {
                        "Cmp": f(pass_types.select_one(selector), '[data-stat="passes_completed"]', int),
                        "Off": f(pass_types.select_one(selector), '[data-stat="passes_offsides"]', int),
                        "Blocks": f(pass_types.select_one(selector), '[data-stat="passes_blocked"]', int)
                    }
                },
                "goalShotCreation": {
                    "SCA": {
                        "SCA": f(gca_table.select_one(selector), '[data-stat="sca"]', int),
                        "SCA90": f(gca_table.select_one(selector), '[data-stat="sca_per90"]', float)
                    },
                    "SCAtypes": {
                        "PassLive": f(gca_table.select_one(selector), '[data-stat="sca_passes_live"]', int),
                        "PassDead": f(gca_table.select_one(selector), '[data-stat="sca_passes_dead"]', int),
                        "TO": f(gca_table.select_one(selector), '[data-stat="sca_take_ons"]', int),
                        "Sh": f(gca_table.select_one(selector), '[data-stat="sca_shots"]', int),
                        "Fld": f(gca_table.select_one(selector), '[data-stat="sca_fouled"]', int),
                        "Def": f(gca_table.select_one(selector), '[data-stat="sca_defense"]', int)
                    },
                    "GCA": {
                        "GCA": f(gca_table.select_one(selector), '[data-stat="gca"]', int),
                        "GCA90": f(gca_table.select_one(selector), '[data-stat="gca_per90"]', float)
                    },
                    "GCAtypes": {
                        "PassLive": f(gca_table.select_one(selector), '[data-stat="gca_passes_live"]', int),
                        "PassDead": f(gca_table.select_one(selector), '[data-stat="gca_passes_dead"]', int),
                        "TO": f(gca_table.select_one(selector), '[data-stat="gca_take_ons"]', int),
                        "Sh": f(gca_table.select_one(selector), '[data-stat="gca_shots"]', int),
                        "Fld": f(gca_table.select_one(selector), '[data-stat="gca_fouled"]', int),
                        "Def": f(gca_table.select_one(selector), '[data-stat="gca_defense"]', int)
                    }
                },
                "defensiveActions": {
                    "tackles": {
                        "Tkl": f(def_actions.select_one(selector), '[data-stat="tackles"]', int),
                        "TklW": f(def_actions.select_one(selector), '[data-stat="tackles_won"]', int),
                        "Def 3rd": f(def_actions.select_one(selector), '[data-stat="tackles_def_3rd"]', int),
                        "Mid 3rd": f(def_actions.select_one(selector), '[data-stat="tackles_mid_3rd"]', int),
                        "Att 3rd": f(def_actions.select_one(selector), '[data-stat="tackles_att_3rd"]', int)
                    },
                    "challenges": {
                        "Tkl": f(def_actions.select_one(selector), '[data-stat="challenges"]', int),
                        "Att": f(def_actions.select_one(selector), '[data-stat="challenges"]', int),
                        "Tkl%": f(def_actions.select_one(selector), '[data-stat="challenge_tackles_pct"]', float),
                        "Lost": f(def_actions.select_one(selector), '[data-stat="challenges_lost"]', int)
                    },
                    "blocks": {
                        "Blocks": f(def_actions.select_one(selector), '[data-stat="blocks"]', int),
                        "Sh": f(def_actions.select_one(selector), '[data-stat="blocked_shots"]', int),
                        "Pass": f(def_actions.select_one(selector), '[data-stat="blocked_passes"]', int),
                        "Int": f(def_actions.select_one(selector), '[data-stat="interceptions"]', int),
                        "Tkl+Int": f(def_actions.select_one(selector), '[data-stat="tackles_interceptions"]', int),
                        "Clr": f(def_actions.select_one(selector), '[data-stat="clearances"]', int),
                        "Err": f(def_actions.select_one(selector), '[data-stat="errors"]', int)
                    }
                },
                "possession": {
                    "touches": {
                        "Touches": f(possesion_table.select_one(selector), '[data-stat="touches"]', int),
                        "Def Pen": f(possesion_table.select_one(selector), '[data-stat="touches_def_pen_area"]', int),
                        "Def 3rd": f(possesion_table.select_one(selector), '[data-stat="touches_def_3rd"]', int),
                        "Mid 3rd": f(possesion_table.select_one(selector), '[data-stat="touches_mid_3rd"]', int),
                        "Att 3rd": f(possesion_table.select_one(selector), '[data-stat="touches_att_3rd"]', int),
                        "Att Pen": f(possesion_table.select_one(selector), '[data-stat="touches_att_pen_area"]', int),
                        "Live": f(possesion_table.select_one(selector), '[data-stat="touches_live_ball"]', int)
                    },
                    "takeOns": {
                        "Att": f(possesion_table.select_one(selector), '[data-stat="take_ons"]', int),
                        "Succ": f(possesion_table.select_one(selector), '[data-stat="take_ons_won"]', int),
                        "Succ%": f(possesion_table.select_one(selector), '[data-stat="take_ons_won_pct"]', float),
                        "Tkld": f(possesion_table.select_one(selector), '[data-stat="take_ons_tackled"]', int),
                        "Tkld%": f(possesion_table.select_one(selector), '[data-stat="take_ons_tackled_pct"]', float)
                    },
                    "carries": {
                        "Carries": f(possesion_table.select_one(selector), '[data-stat="carries"]', int),
                        "TotDist": f(possesion_table.select_one(selector), '[data-stat="carries_distance"]', int),
                        "PrgDist": f(possesion_table.select_one(selector), '[data-stat="carries_progressive_distance"]', int),
                        "ProgC": f(possesion_table.select_one(selector), '[data-stat="carries_progressive_distance"]', int),
                        "1/3": f(possesion_table.select_one(selector), '[data-stat="carries_into_final_third"]', int),
                        "CPA": f(possesion_table.select_one(selector), '[data-stat="carries_into_penalty_area"]', int),
                        "Mis": f(possesion_table.select_one(selector), '[data-stat="miscontrols"]', int),
                        "Dis": f(possesion_table.select_one(selector), '[data-stat="dispossessed"]', int)
                    },
                    "receiving": {
                        "Rec": f(possesion_table.select_one(selector), '[data-stat="passes_received"]', int),
                        "PrgR": f(possesion_table.select_one(selector), '[data-stat="progressive_passes_received"]', int)
                    }
                },
                "playingTime_details": {
                    "starts": {
                        "Starts": f(playing_time.select_one(selector), '[data-stat="games_starts"]', int),
                        "Mn/Start": f(playing_time.select_one(selector), '[data-stat="minutes_per_start"]', int),
                        "Compl": f(playing_time.select_one(selector), '[data-stat="games_complete"]', int)
                    },
                    "subs": {
                        "Subs": f(playing_time.select_one(selector), '[data-stat="games_subs"]', int),
                        "Mn/Sub": f(playing_time.select_one(selector), '[data-stat="minutes_per_sub"]', int),
                        "unSub": f(playing_time.select_one(selector), '[data-stat="unused_subs"]', int)
                    },
                    "teamSuccess": {
                        "PPM": f(playing_time.select_one(selector), '[data-stat="points_per_game"]', float),
                        "onG": f(playing_time.select_one(selector), '[data-stat="on_goals_for"]', int),
                        "onGA": f(playing_time.select_one(selector), '[data-stat="on_goals_against"]', int)
                    },
                    "teamSuccessxG": {
                        "onxG": f(playing_time.select_one(selector), '[data-stat="on_xg_for"]', float),
                        "onxGA": f(playing_time.select_one(selector), '[data-stat="on_xg_against"]', float)
                    }
                },
                "miscellaneousStats": {
                    "performance": {
                        "Fls": f(miscellaneous_table.select_one(selector), '[data-stat="fouls"]', int),
                        "Fld": f(miscellaneous_table.select_one(selector), '[data-stat="fouled"]', int),
                        "Off": f(miscellaneous_table.select_one(selector), '[data-stat="offsides"]', int),
                        "Crs": f(miscellaneous_table.select_one(selector), '[data-stat="crosses"]', int),
                        "OG": f(miscellaneous_table.select_one(selector), '[data-stat="own_goals"]', int),
                        "Recov": f(miscellaneous_table.select_one(selector), '[data-stat="ball_recoveries"]', int)
                    },
                    "aerialDuels": {
                        "Won": f(miscellaneous_table.select_one(selector), '[data-stat="aerials_won"]', int),
                        "Lost": f(miscellaneous_table.select_one(selector), '[data-stat="aerials_lost"]', int),
                        "Won%": f(miscellaneous_table.select_one(selector), '[data-stat="aerials_won_pct"]', float)
                    }
                }
            }
            players.append(player)
            index += 1
            print(player['name'], 'done !')
            
        time.sleep(5)

    players.sort(key=lambda p: (p['name'].split()[0], -p['age']))

    with open('data/players.json', 'w', encoding='utf-8') as file:
        json.dump(players, file, ensure_ascii=False, indent=4)
        
        
def crawlClubs():
    teams = []
    for teamElement in document.select('#results2023-202491_overall tbody tr'):
        name = f(teamElement, 'td a')
        print(f'scan club {name}')
        team = {
            "name": name,
            "wins": f(teamElement, '[data-stat="wins"]', int),
            "draws": f(teamElement, '[data-stat="ties"]', int),
            "losses": f(teamElement, '[data-stat="losses"]', int),
            "goals": f(teamElement, '[data-stat="goals_for"]', int),
            "goalsAgainst": f(teamElement, '[data-stat="goals_against"]', int),
            "goalDiff": f(teamElement, '[data-stat="goal_diff"]', int),
            "points": f(teamElement, '[data-stat="points"]', int),
            "Pts/MP": f(teamElement, '[data-stat="points_avg"]', float), #điểm / trận
            "xG": f(teamElement, '[data-stat="xg_for"]', float), #số bàn tháng kỳ vọng
            "xGA": f(teamElement, '[data-stat="xg_against"]', float), #số bàn thua kỳ vọng
            "xGD": f(teamElement, '[data-stat="xg_diff"]', float), #hiệu suất kỳ vọng
            "xGD/90": f(teamElement, '[data-stat="xg_diff_per90"]', float) #hiệu suất kỳ vọng / 90ph
        }
        teams.append(team)
        
    with open('data/clubs.json', 'w', encoding='utf-8') as file:
        json.dump(teams, file, ensure_ascii=False, indent=4)
        
        
if __name__ == "__main__":
    crawlPlayers()
    crawlClubs()
        

        
    
                
        







