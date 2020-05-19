import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

import pandas as pd
import os
os.chdir(r'C:\Users\Franciszek.Grymula\Documents\_Szkoła\CEIDG-data-visualisation\final_app\scripts')

df_corr_feat = pd.read_csv('../data/corrs_and_features.csv',index_col=0)

app = dash.Dash()

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='life-exp-vs-gdp'),
        html.Label('Wybierz metrykę'),
        dcc.Dropdown(
            id='column',
            options=[{'label': 'Korelacja', 'value': 'correlations'},
                     {'label': 'Feature importance', 'value': 'importance'}],
            value = 'importance',
            clearable=False
        ),
    #    html.Label('Show top'),
    #    dcc.Slider(
    #        id='expectancy-slider',
    #        min=3,
    #        max=10,
    #        value=3,
    #        step=None,
    #        marks=dict([(str(v),str(v)) for v in range(3,11)]+[('1000000000000', 'all')])
    #    ),
    ], style={'width': '70%', 'display': 'inline-block'})
])


@app.callback(
    Output('life-exp-vs-gdp', 'figure'), [Input('column', 'value')])
def update_graph(country):

    data = df_corr_feat[country]
    filtered_df_corr_feat = data[data.abs()>0.05]#.loc[df_corr_feat["life expectancy"] > expectancy]

    #if (country != '' and country is not None):
    #    filtered_df_corr_feat = filtered_df_corr_feat[df_corr_feat.country.str.contains('|'.join(country))]
    
    df_corr_feat_by_continent = filtered_df_corr_feat.sort_values(ascending=False)#[:expectancy]
    fig = go.Figure(go.Bar(
        x=df_corr_feat_by_continent.index,
        y=df_corr_feat_by_continent,
        text=df_corr_feat_by_continent.index))
    
    ranges = {'correlations': [-1, 1], 'importance': [0, 100]}
    values = {'correlations': 'Korelacja',
              'importance': 'Feature importance [%]'}
    titles = {'correlations': 'Korelacja z czasem życia',
              'importance': 'Feature importance w modelu lasu losowego'}
    
    fig.update_layout(go.Layout(
        title=titles[country],
        yaxis={'title': values[country], 'titlefont': {'size': 16, 'color': 'darkgrey'}, 'range': ranges[country], 'ticks': 'outside'},
        margin={'l': 60, 'b': 200, 't': 30, 'r': 20},
        legend={'x': 1, 'y': 1},
        hovermode='closest'
    ))    
    return fig


app.run_server(debug=True, use_reloader=False, port=9000)
