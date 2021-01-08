import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from database.sqlalchemy_utils import *
from gensim_dtm.gensim_lda import perform_lda
import plotly.express as px
from text_processing.text_processing_utils import convert_to_raw_text

query_city_names = """
SELECT DISTINCT city FROM collection 
"""

all_teams_df = pd.read_csv('dash_simple_nba_srcdata_shot_dist_compiled_data_2019_20.csv')

conn = create_connection('localhost', 'root', 'Ju5Ky1M@', 'news')
city_names = list(execute_read_query(conn, query_city_names))
conn.close()

app = dash.Dash(__name__)
server = app.server
team_names = all_teams_df.group.unique()
team_names.sort()
app.layout = html.Div([
    dcc.Graph('news-overview-graph', config={'displayModeBar': False}),
    html.P("Select a city to inspect: "),
    html.Div([dcc.Dropdown(id='group-select', options=[{'label': i[0], 'value': i[0]} for i in city_names],
                           value=city_names[0][0], style={'width': '140px'})]),
    dcc.Graph('specific-news-graph', config={'displayModeBar': False})])


@app.callback(
    Output('news-overview-graph', 'figure'),
    [Input('group-select', 'value')]
)
def update_graph(grpname):
    conn = create_connection('localhost', 'root', 'Ju5Ky1M@', 'news')
    city_counts = []
    for city_name in city_names:
        count = execute_read_query(conn, "SELECT COUNT(city) FROM collection WHERE city='{}'".format(city_name[0]))
        city_counts.append([city_name[0], count[0][0]])
    conn.close()
    city_df = pd.DataFrame(city_counts, columns=['city', 'count'])
    return px.pie(city_df, values='count', names='city', title='Proportion of news by city')


@app.callback(
    Output('specific-news-graph', 'figure'),
    [Input('group-select', 'value')]
)
def update_graph(grpname):
    conn = create_connection('localhost', 'root', 'Ju5Ky1M@', 'news')
    query_result = execute_read_query(conn, "SELECT title, article_text FROM collection WHERE city='{}'".format(grpname))
    conn.close()
    news_df = pd.DataFrame(query_result, columns=['title', 'article_text'])
    for column in range(0,len(news_df)):
        news_df.iloc[column]['title'] = convert_to_raw_text(news_df.iloc[column]['title'])
        news_df.iloc[column]['article_text'] = convert_to_raw_text(news_df.iloc[column]['article_text'])
    lda_model = perform_lda(news_df, num_topics=10)
    topic_data_frame = pd.DataFrame(lda_model.show_topics(formatted=False))
    topic_data_frame.loc[:, 'keyword'] = topic_data_frame[1].map(lambda x: x[0][0])
    topic_data_frame.loc[:, 'importance'] = topic_data_frame[1].map(lambda x: x[0][1])
    topic_data_frame['importance'] /= max(topic_data_frame['importance'])
    topic_data_frame.sort_values('importance')
    return px.bar(topic_data_frame, x='keyword', y='importance', title='Key words and their relevance')


if __name__ == '__main__':
    app.run_server(debug=False)
