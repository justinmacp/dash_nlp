import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly
import plotly.express as px
from database.sqlalchemy_utils import *

from pyorbital.orbital import Orbital

query_city_names = """
SELECT DISTINCT city FROM collection 
"""

satellite = Orbital('TERRA')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
conn = create_connection('localhost', 'root', 'Ju5Ky1M@', 'news')
city_names = list(execute_read_query(conn, query_city_names))

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    dcc.Dropdown(id='demo-dropdown',
                 options=[{'label': i[0], 'value': i[0]} for i in city_names],
                 value=city_names[0][0]),
    html.Div(id='dd-output-container'),
    dcc.Graph(id='live-update-graph')
])


@app.callback(Output('live-update-text', 'children'), Input('interval-component', 'n_intervals'))
def update_metrics(n):
    lon, lat, alt = satellite.get_lonlatalt(datetime.datetime.now())
    style = {'padding': '5px', 'fontSize': '16px'}
    return [html.Span('Longitude: {0:.2f}'.format(lon), style=style),
            html.Span('Latitude: {0:.2f}'.format(lat), style=style),
            html.Span('Altitude: {0:0.2f}'.format(alt), style=style)]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
