# Importing the modules
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




# Print a title
display(HTML("<h1><font color='#0b2652'>NBA Player Comparison</font></h1>"))

# Let the user choose whether they want per game stats or season totals
@interact_manual(stat_type = [' Per Game', ' Season Total'])
def main(stat_type):
    
    # Stat_type determines which table from the website is chosen.
    # Per game is the first table, and season total is the third
    if stat_type == ' Per Game':
        chosen_table = 0
    elif stat_type == ' Season Total':
        chosen_table = 2
        

    # This section takes the dataframe from the website and reads the column names into a list for the drop down menu
    df = pd.read_html(f'https://www.basketball-reference.com/players/j/jordami01.html')[chosen_table]
    cols = []
    for col in df.columns:
        cols.append(col)

    # Only takes the relevant columns (statistics) and ignores info like the team name and season
    newcols = cols[5:-2]
    
    # This creates a list of the season options for the user
    season_choice = list(range(1970,2021))

    # Here, the user chooses their players, the statistic, and the start season
    @interact_manual(Player1 = '', Player2 = '', Statistic = newcols, start_season = season_choice)
    def main(Player1, Player2, Statistic, start_season):
        
        # Try clause in case the user inputs an invalid name
        try:
            stat = Statistic
            p1 = Player1.title()
            p2 = Player2.title()

            # This function formats the name of the player into the format required to put it in the url
            def nameToUrl(name):
                namesplit = name.split(' ')
                newname = namesplit[1][:5] + namesplit[0][:2]
                return newname  

            # This function returns a list of the player's statistics per season
            def getStats(p, state, start_season):

                name = nameToUrl(p)

                df = pd.read_html(f'https://www.basketball-reference.com/players/{name[0].lower()}/{name.lower()}01.html')[chosen_table]

                # Setting the index to season allows me to take stats from specific seasons easily
                df.set_index('Season', inplace = True)

                # Initialize an empty list for the player's statistics
                stat_list = []

                # Iterate through five seasons, starting at the starting season selected by the user

                d = 5
                for i in range(d):

                    second = str(start_season + 1)

                    sec_season = (second[2:])

                    start_season = int(start_season)

                    try:
                        # Get the desired stat and store it in a variable called blue
                        blue = df.loc[f'{start_season}-{sec_season}'][state]

                        try:
                            blue = float(blue)
                            stat_list.append([f'{start_season}-{sec_season}', blue])

                        # If the statistic can't be converted into a float, we can assume there's no data for that season
                        except:
                            stat_list.append([f'{start_season}-{sec_season}', None])

                    except KeyError:
                        stat_list.append([f'{start_season}-{sec_season}', None])

                    start_season = start_season+1

                # Return the list of statistics and the last season
                return stat_list, second

            def getLeague(state, start_season):

                # Initialize an empty list for the player's statistics
                stat_list = []

                # Iterate through five seasons, starting at the starting season selected by the user
                for i in range(5):

                    df = pd.read_html(f'https://www.basketball-reference.com/leagues/NBA_{start_season+1}.html')[5]

                    # Setting the index to season allows me to take stats from specific seasons easily
                    df.set_index('Team', inplace = True)

                    second = str(start_season + 1)

                    sec_season = (second[2:])

                    start_season = int(start_season)

                    try:
                        # Get the desired stat and store it in a variable called blue
                        blue = df.loc['League Average'][state]

                        try:
                            blue = float(blue)
                            stat_list.append([f'{start_season}-{sec_season}', blue])

                        # If the statistic can't be converted into a float, we can assume there's no data for that season
                        except:
                            stat_list.append([f'{start_season}-{sec_season}', None])

                    except KeyError:
                        stat_list.append([f'{start_season}-{sec_season}', None])

                    start_season = start_season+1

                # Return the list of statistics and the last season
                return stat_list

            # Get statistics for each of the players
            p1stats, second = getStats(p1, stat, start_season)

            p2stats, blah = getStats(p2, stat, start_season)

            league = getLeague(stat, start_season)

            # Turn the list of statistics into dataframes
            try:
                p1df = pd.DataFrame(p1stats, columns = ['Season', stat])
                p2df = pd.DataFrame(p2stats, columns = ['Season', stat])
                leaguedf = pd.DataFrame(league, columns = ['Season', stat])
            except:
                pass

            # Create a graph object
            graph = go.Figure()

            # Add the two lines for each player
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

            # If the type of statistic is a percentage, show the league average on the graph
            if '%' in stat and stat != 'eFG%':
                graph.add_trace(go.Scatter(
                    x=leaguedf['Season'],
                    y=leaguedf[stat],
                    name='League Average',
                    line=dict(color='green', width=4))
                    )

            # If not a percentage stat, add season total or per game to the title of the graph
            ball = ''
            if '%' not in stat:
                ball = stat_type     

            # Add more formatting to the graph
            graph.update_layout(
                font_family="Arial",
                font_color='#e9edf7',
                title_font_family="Arial",
                title_font_color="#e9edf7",
                legend_title_font_color="#e9edf7",
                title = {'text': f'<b>Comparison of {stat}{ball} Between {p1} and {p2}, {start_season}-{second}</b>', 
                        'xanchor': 'center',
                        'y':0.90,
                        'x':0.5,
                        'yanchor': 'top'},
                template="plotly_dark",
                xaxis = dict(showgrid = True),
                yaxis = dict(showgrid = True),
                xaxis_title='Season',
                yaxis_title=stat,
            )

            # Function for printing info about the players
            def printInfo(name):
                try:
                    player_info = wikipedia.summary(name, sentences='2', auto_suggest=False,redirect=True)
                    display(HTML(f"<p><font color='black'>{player_info}</font></p>"))
                except:
                    display(HTML(f"<p><font color='black'>No information found on {name}.</font></p>"))

            # Display the graph
            graph.show()

            # Print information about the players
            printInfo(p1)
            url1 = get_player_headshot(p1)
            im1 = Image.open(requests.get(url1, stream=True).raw)
            display(im1)

            printInfo(p2)
            url2 = get_player_headshot(p2)
            im2 = Image.open(requests.get(url2, stream=True).raw)
            display(im2)
          
        except:
            display(HTML(f"<p><font color='black'>Player name invalid. Please check your spelling or try another player.</font></p>"))
            
            