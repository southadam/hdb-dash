import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SUPERHERO])
server = app.server

df = pd.read_csv("hdb.csv")
new = df["month"].str.split("-", n = 1, expand = True)
df.drop(columns =["month"], inplace = True)
df['year']=new[0]
df['month']=new[1]
df['year']=df['year'].astype('int64')
df['month']=df['month'].astype('int64')
min_year = df['year'].min()
max_year = df['year'].max()

df_median = df.groupby(["town","flat_type","year"])["resale_price"].median().reset_index()


flattype = df['flat_type'].unique()
flattype.sort()

#fig = px.bar(df, x="flat_type", y="resale_price", color="town", barmode="group")

app.layout = dbc.Container([
    html.Div([
        html.H1(children="Singapore HDB Resale Town & Flat Type Analysis"),
        html.P(
            children="Analyze HDB Resale"
            " between 2017 and 2021",
            className="header-desc",
        ),
    ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='graph-scatter')
                    ],md=12, className="scatter"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='graph-scatter2')
                    ],md=12, className="scatter"),
                ]),
                    dbc.Row([
                        dbc.Col([
                            html.H2(children="HDB Year Slider"),
                            dcc.RangeSlider(
                                id='year-slider',
                                min=min_year,
                                max=max_year,
                                step=1,
                                value=[min_year, max_year],
                                marks=dict([(y, {'label': str(y)}) for y in list(range(min_year, max_year + 1))])
                            ),
                        ], className="slider-panel"),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.H2(children="Choose Flat Type"),
                            dcc.Dropdown(
                                id='flattype-column',
                                options=[{'label': i, 'value': i} for i in flattype],
                                value=flattype[:],
                                multi=True,
                                searchable=False,
                                style={"color":"black"}
                            ),
                        ],className="slider-panel"),
                    ]),
                    dbc.Col([
                        dcc.Graph(id='graph-with-slider')
                    ],md=12),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='graph-with-pie')
                    ], md=6),
                    dbc.Col([
                        dcc.Graph(id='graph-with-pie2')
                    ], md=6),
                ]),
])

@app.callback(
    Output('graph-with-slider', 'figure'),
    Output('graph-with-pie', 'figure'),
    Output('graph-with-pie2', 'figure'),
    Output('graph-scatter', 'figure'),
    Output('graph-scatter2', 'figure'),
    Input('flattype-column','value'),
    Input('year-slider', 'value'))
def update_figure(selected_flat_type, selected_year):
    xdf = df[(df['year'] >= selected_year[0]) & (df['year'] <= selected_year[1]) & (df['flat_type'].isin(selected_flat_type))]
    xmedian = df_median[(df_median['year'] >= selected_year[0]) & (df_median['year'] <= selected_year[1]) & (df_median['flat_type'].isin(selected_flat_type))]
    fig = px.histogram(xdf, x='town', y="resale_price",
                 labels={
            'town': 'Township',
            'resale_price': 'Resale Value'
        }, title='Total Resale Value by Township', height=500)
    pie = px.pie(xdf, names='flat_model',values='resale_price', title='Resale % by Flat Model')
    pie2 = px.pie(xdf, names='storey_range', values='resale_price', title='Resale % by Storey Range')
    fig2 = px.scatter(df, y="town", x="resale_price", color="flat_type", symbol="flat_model",
                      labels={
                          'town': 'Township',
                          'resale_price': 'Resale Value',
                          'flat_type': 'Flat Type',
                          'flat_model': 'Flat Model'
                      },
    title='Understanding the HDB Flat Area & Types', height=500)
    fig3 = px.scatter(xmedian, y="town", x="resale_price", color="flat_type",
    labels = {
                 'town': 'Township',
                 'resale_price': 'Resale Value',
                 'flat_type': 'Flat Type'
             }, title='Understanding the HDB Flat Area & Types'
    )
    fig.update_layout(transition_duration=500,paper_bgcolor="#2B3E50",font_color="white")
    fig2.update_layout(transition_duration=500, paper_bgcolor="#2B3E50", font_color="white")
    fig3.update_layout(transition_duration=500, paper_bgcolor="#2B3E50", font_color="white")
    pie.update_layout(transition_duration=500,paper_bgcolor="#2B3E50",font_color="white")
    pie2.update_layout(transition_duration=500, paper_bgcolor="#2B3E50", font_color="white")

    return (fig,pie,pie2,fig2,fig3)

if __name__ == '__main__':
    app.run_server(debug=True)