import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from database.sqlalchemy_utils import *

query_city_names = """
SELECT DISTINCT city FROM collection 
"""

query_city_count = """
SELECT COUNT(city) FROM collection WHERE city='JUBA'
"""

conn = create_connection('localhost', 'root', 'Ju5Ky1M@', 'news')
city_names = list(execute_read_query(conn, query_city_names))


city_counts = []
for city_name in city_names:
    count = execute_read_query(conn, "SELECT COUNT(city) FROM collection WHERE city='{}'".format(city_name[0]))
    city_counts.append([city_name[0], count[0][0]])
city_df = pd.DataFrame(city_counts, columns=['city', 'count'])
fig = px.pie(city_df, values='count', names='city', title='Proportion of news by city')
fig.show()
conn.close()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.P("Select a city:"),
    dcc.Dropdown(id='city-dropdown',
                 options=[{'label': i[0], 'value': i[0]} for i in city_names],
                 value=city_names[0][0]),
    dcc.Graph(id='live-update-graph')])


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              [Input('city_dropdown', 'value')])
def update_graph(n):
    conn = create_connection('localhost', 'root', 'Ju5Ky1M@', 'news')
    city_counts = []
    for city_name in city_names:
        count = execute_read_query(conn, "SELECT COUNT(city) FROM collection WHERE city='{}'".format(city_name[0]))
        city_counts.append([city_name[0], count[0][0]])
    conn.close()
    city_df = pd.DataFrame(city_counts, columns=['city', 'count'])
    fig = px.pie(city_df, values='count', names='city', title='Proportion of news by city')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
