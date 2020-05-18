import numpy as np
import pandas as pd
import plotly as plt
import plotly.graph_objects as go
import dash
import dash_core_components as doc
import dash_html_components as html
from dash.dependencies import Input, Output

import os
os.chdir(r'C:\Users\Franciszek.Grymula\Documents\_Szkoła\Wizualizacja_danych')

df = pd.read_csv('./ceidg_data_surviv_preprocessed.csv')
features = [
    'MainAddressVoivodeshipFromTERCVerbose', 'IsPhoneNoEncoded',
    'IsEmailEncoded', 'IsWWWEncoded', 'HasLicencesEncoded',
    'HasPolishCitizenshipEncoded', 'ShareholderInOtherCompaniesEncoded',
    'SexEncoded', 'CommunityPropertyEncoded'
]
values = {feature: df[feature].unique().tolist() for feature in features}

km_curves_ = pd.read_csv('km_curves.csv')

KM_description = [
    'Krzywa Kaplana-Meiera jest estymatorem funkcji przeżycia danej wzorem',
    'gdzie T jest zmienną losową określającą długość życia spółki.\n\nMa on następującą postać:',
    '''gdzie
    ti są uporządkowanymi niemalejąco miesiącami zamknięcia (śmierci) spółek w próbie,
    ni jest liczbą działających (żywych) spółek w miesiącu ti,
    di jest lcizbą zamknięć (śmierci) spółek w miesiącu ti.
    Im większe wartości krzywej w punkcie ti, tym większe prawdopodobieństwo, że spółki z danej grupy
    dożyją co najmniej do momentu ti'''
]

app = dash.Dash(name='Kaplan-Meier curve')
app.layout = html.Div([
    html.Div([
        doc.Graph(id='KM-curve'),
        doc.Markdown('Wybierz zmienną:'),
        doc.Dropdown(
            id='features',
            options=[
                {'label': f, 'value': f} for f in features
            ] + [
                {'label': 'Cała próba', 'value': 'whole_dataset'}
            ],
            value='whole_dataset'
        ),
        doc.Markdown(KM_description[0]),
        html.Img(
            src='https://wikimedia.org/api/rest_v1/media/math/render/svg/01e97aef4d5ebd2d88d07d2afd392cf12131e657'
        ),
        doc.Markdown(KM_description[1]),
        html.Img(
            src='https://wikimedia.org/api/rest_v1/media/math/render/svg/8575184e8c8133a3fa1c83e039773178fe51872a'
        ),
        doc.Markdown(KM_description[2]),
        ], style={'width': '50%'}
    ),
    html.Div([
        doc.Graph(id='lifetime-hist'),
        doc.Markdown('Wybierz dwa województwa:'),
        doc.Dropdown(
            id='voievodships',
            options=[
                {'label': f, 'value': f}
                    for f in values['MainAddressVoivodeshipFromTERCVerbose']
                    if f is not np.nan
            ] + [
                {'label': 'Whole country', 'value': 'whole_dataset'},
                {'label': 'brak', 'value': 'brak'}
            ],
            value=['whole_dataset', 'MAZOWIECKIE'],
            multi=True
        )
        ], style={'width': '50%'}
    )
])

@app.callback(
    Output('KM-curve', 'figure'),
    [Input('features', 'value')]
)
def update_KM_curve(feature):
    fig = go.Figure()
    if feature == 'whole_dataset':
        fig.add_trace(go.Scatter(
            x=km_curves['timeline'],
            y=km_curves[feature],
            name='Cała próba',
            mode='lines'
        ))
    else:
        for val in values[feature]:
            fig.add_trace(go.Scatter(
                x=km_curves['timeline'],
                y=km_curves[feature + '_' + str(val)],
                name=str(val),
                mode='lines'
            ))
    fig.update_layout(
        title_text='Krzywa Kaplana-Meiera',
        xaxis_title_text='Długość życia w miesiącach',
        yaxis_title_text='P-stwo przeżycia'
    )
    return fig


@app.callback(
    Output('lifetime-hist', 'figure'),
    [Input('voievodships', 'value')]
)
def update_lifetime_hist(value):
    dfs = [0, 0]
    
    for i in [0, 1]:
        if value[i] == 'whole_dataset':
            dfs[i] = df
        elif value[i] == 'brak':
            dfs[i] = df.loc[
                df['MainAddressVoivodeshipFromTERCVerbose'].isna()]
        else:
            dfs[i] = df.loc[
                df['MainAddressVoivodeshipFromTERCVerbose'] == value[i]]
    
    fig = plt.subplots.make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    for i in [0, 1]:
        if value[i] == 'whole_dataset':
            name = 'Cała Polska'
        else:
            name = value[i]
        fig.add_trace(go.Histogram(
            x=dfs[i]['DurationOfExistenceInMonths'],
            histnorm='probability density',
            name=name,
            nbinsx=32
            ), i+1, 1)
    
    fig.update_yaxes(matches='y')
    fig.update_layout(
        title_text='Histogram długości życia (znormalizowany)',
    )
    return fig


app.run_server(debug=True, use_reloader=False)
