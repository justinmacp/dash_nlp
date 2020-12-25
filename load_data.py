import pandas as pd
import plotly.express as px
import nba_utils

all_teams_df = pd.read_csv('dash_simple_nba_srcdata_shot_dist_compiled_data_2019_20.csv')

all_teams_df.head()

fig = px.scatter(all_teams_df[all_teams_df.group == 'NOP'], x='min_mid', y='player', size='shots_freq', color='pl_pps')
fig.show()

fig = nba_utils.make_shot_dist_chart(
    all_teams_df[all_teams_df.group == 'SAS'], col_col='pl_pps', range_color=[90, 120], size_col='shots_freq')
nba_utils.clean_chart_format(fig)
fig.update_layout(height=500, width=1250)
fig.show()
