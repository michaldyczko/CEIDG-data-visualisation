#!/usr/bin/env python
# coding: utf-8

import pandas as pd

df = pd.read_csv('corrs_and_features.csv',index_col=0)


import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

import pandas as pd

columns = {'Correlations': 'correlations', 'Features importances': 'importance'}

app = dash.Dash()

app.layout = html.Div([

    html.Div([
        html.Label('Column'),
        dcc.Dropdown(
            id='column',
            options=[{'label': k, 'value': v} for k,v in columns.items()],
            value = list(columns.items())[0][1],
            placeholder='Select...',
            multi=False,
            clearable=False
        )
    ],    
    style={'width': '20%', 'display': 'inline-block', 'margin-bottom': '20px'}),    

    html.Div([
       html.Label('Showing only top 10 columns (+ last 10 for correlations).'),
       # dcc.Slider(
       #     id='expectancy-slider',
       #     min=3,
       #     max=10,
       #     value=3,
       #     step=None,
       #     marks=dict([(str(v),str(v)) for v in range(3,11)]+[('1000000000000', 'all')])
       # ),
    ],
    style={'width': '20%', 'display': 'inline-block', 'margin-bottom': '20px', 'margin-left': '20px'}),

    html.Div([
        dcc.Graph(id='life-exp-vs-gdp'),
    ],
    style={'width': '70%'}),
])


@app.callback(
    dash.dependencies.Output('life-exp-vs-gdp', 'figure'),
    [
        dash.dependencies.Input('column', 'value')
    ])
def update_graph(country):

    data = df[country].sort_values(ascending=False)
    filtered_df = data[:10]#[data.abs()>=0.03]#.loc[df["life expectancy"] > expectancy]
    if country == 'correlations':
        filtered_df = filtered_df.append(data[-10:])

    traces = []
    traces.append(go.Bar(
        x=filtered_df.index,
        y=filtered_df,
        text=filtered_df.index,
    ))
    
    ranges = {'correlations': [-1,1], 'importance': [0,100]}
    values = {'correlations': 'Correlation', 'importance': 'Feature importance (percent)'}
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Feature name', 'titlefont': dict(size=18, color='darkgrey'), 'zeroline': False, 'ticks': 'outside' },
            yaxis={'title': values[country], 'titlefont': dict(size=18, color='darkgrey'), 'range': ranges[country], 'ticks': 'outside'},
            margin={'l': 60, 'b': 200, 't': 30, 'r': 20},
            legend={'x': 1, 'y': 1},
            hovermode='closest'
        )
    }



app.run_server(debug=True, port=9000)




