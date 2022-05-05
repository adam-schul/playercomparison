import requests
import json
import pandas as pd
import plotly.express as px
from ipywidgets import interact_manual
import plotly.graph_objects as go
import wikipedia
from IPython.display import display, HTML
from PIL import Image
import requests
from basketball_reference_scraper.players import get_player_headshot

display(HTML("<h1><font color='#0b2652'>NBA Player Comparison</font></h1>"))

@interact_manual(stat_type = [' Per Game', ' Season Total'])
def main(stat_type):

    if stat_type == ' Per Game':
        chosen_table = 0
    elif stat_type == ' Season Total':
        chosen_table = 2

    df = pd.read_html(f'https://www.basketball-reference.com/players/j/jordami01.html')[chosen_table]
    cols = []
    for col in df.columns:
        cols.append(col)

    newcols = cols[5:-2]
    
    season_choice = list(range(1970,2021))

    @interact_manual(Player1 = '', Player2 = '', Statistic = newcols, start_season = season_choice)
    def main(Player1, Player2, Statistic, start_season):
        
        try:
            stat = Statistic
            p1 = Player1.title()
            p2 = Player2.title()

            def nameToUrl(name):
                namesplit = name.split(' ')
                newname = namesplit[1][:5] + namesplit[0][:2]
                return newname  

            def getStats(p, state, start_season):

                name = nameToUrl(p)

                df = pd.read_html(f'https://www.basketball-reference.com/players/{name[0].lower()}/{name.lower()}01.html')[chosen_table]

                df.set_index('Season', inplace = True)

                stat_list = []


                d = 5
                for i in range(d):

                    second = str(start_season + 1)

                    sec_season = (second[2:])

                    start_season = int(start_season)

                    try:
                        blue = df.loc[f'{start_season}-{sec_season}'][state]

                        try:
                            blue = float(blue)
                            stat_list.append([f'{start_season}-{sec_season}', blue])

                        except:
                            stat_list.append([f'{start_season}-{sec_season}', None])

                    except KeyError:
                        stat_list.append([f'{start_season}-{sec_season}', None])

                    start_season = start_season+1

                return stat_list, second

            def getLeague(state, start_season):

                stat_list = []

                for i in range(5):

                    df = pd.read_html(f'https://www.basketball-reference.com/leagues/NBA_{start_season+1}.html')[5]

                    df.set_index('Team', inplace = True)

                    second = str(start_season + 1)

                    sec_season = (second[2:])

                    start_season = int(start_season)

                    try:
                        blue = df.loc['League Average'][state]

                        try:
                            blue = float(blue)
                            stat_list.append([f'{start_season}-{sec_season}', blue])

                        except:
                            stat_list.append([f'{start_season}-{sec_season}', None])

                    except KeyError:
                        stat_list.append([f'{start_season}-{sec_season}', None])

                    start_season = start_season+1

                return stat_list

            p1stats, second = getStats(p1, stat, start_season)

            p2stats, blah = getStats(p2, stat, start_season)

            league = getLeague(stat, start_season)

            try:
                p1df = pd.DataFrame(p1stats, columns = ['Season', stat])
                p2df = pd.DataFrame(p2stats, columns = ['Season', stat])
                leaguedf = pd.DataFrame(league, columns = ['Season', stat])
            except:
                pass

            graph = go.Figure()

            graph.add_trace(go.Scatter(
                x=p1df['Season'],
                y=p1df[stat],
                name=p1,
                line=dict(color='firebrick', width=4))
                )

            graph.add_trace(go.Scatter(
                x=p2df['Season'],
                y=p2df[stat],
                name=p2,
                line=dict(color='royalblue', width=4))
                )

            if '%' in stat and stat != 'eFG%':
                graph.add_trace(go.Scatter(
                    x=leaguedf['Season'],
                    y=leaguedf[stat],
                    name='League Average',
                    line=dict(color='green', width=4))
                    )

            ball = ''
            if '%' not in stat and stat != 'G':
                ball = stat_type  
            
            if stat == 'G':
                stat1 = 'Games Played'
            elif stat == 'GS':
                stat1 = 'Games Started'
            elif stat == 'MP':
                stat1 = 'Minutes Played'
            elif stat == 'TRB':
                stat1 = 'Total Rebounds'
            else:
                stat1 = stat
            
            graph.update_layout(
                font_family="Arial",
                font_color='#e9edf7',
                title_font_family="Arial",
                title_font_color="#e9edf7",
                legend_title_font_color="#e9edf7",
                title = {'text': f'<b>Comparison of {stat1}{ball} Between {p1} and {p2}, {start_season}-{second}</b>', 
                        'xanchor': 'center',
                        'y':0.90,
                        'x':0.5,
                        'yanchor': 'top'},
                template="plotly_dark",
                xaxis = dict(showgrid = True),
                yaxis = dict(showgrid = True),
                xaxis_title='Season',
                yaxis_title=stat)

            graph.show()
            
            def printInfo(name):
                try:
                    player_info = wikipedia.summary(name, sentences='2', auto_suggest=False,redirect=True)
                    display(HTML(f"<p><font color='black'>{player_info}</font></p>"))
                except:
                    display(HTML(f"<p><font color='black'>No information found on {name}.</font></p>"))

            def showImage(player):
                url = get_player_headshot(player)
                image_object = requests.get(url, stream=True)
                image = Image.open(image_object.raw)
                display(image)
                
            def playerSum(player):
                showImage(player)
                printInfo(player)
                

            playerSum(p1)
            playerSum(p2)
          
        except:
            display(HTML(f"<p><font color='black'>Player name invalid. Please check your spelling or try another player.</font></p>"))
            
            
