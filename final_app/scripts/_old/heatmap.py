import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from dash.dependencies import Input, Output

import os
os.chdir(r'C:\Users\Franciszek.Grymula\Documents\_Szkoła\CEIDG-data-visualisation\final_app\scripts')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


df = pd.read_csv('../data/ceidg_data_surviv_preprocessed.csv')

#przygotowanie danych
#df = df.loc[df['Terminated'] == 1] #tylko firmy upadłe
df = df[['DurationOfExistenceInMonths', 'MainAddressVoivodeshipFromTERCVerbose', 'Sex', 'PKDMainSection', 'HasPolishCitizenshipEncoded', 'MainAddressCommuneTypeFromTERCVerbose']]
df = df.dropna()
df['Sex'] = np.where(df['Sex'] == 'F', 'Kobieta', 'Mężczyzna')
df['HasPolishCitizenshipEncoded'] = np.where(df['HasPolishCitizenshipEncoded'] == 1, 'Tak', 'Nie')

axis_key = ['MainAddressVoivodeshipFromTERCVerbose', 'PKDMainSection', 'Sex', 'HasPolishCitizenshipEncoded', 'MainAddressCommuneTypeFromTERCVerbose']
axis_name = {
    'MainAddressVoivodeshipFromTERCVerbose': 'Województwo',
    'Sex': 'Płeć właściciela',
    'PKDMainSection': 'Rodzaj działalności',
    'HasPolishCitizenshipEncoded': 'Polskie obywatelstwo',
    'MainAddressCommuneTypeFromTERCVerbose': 'Typ gminy',
}
PKD_dict = {
    'A': 'Agrokultura',
    'B': 'Górnictwo',
    'C': 'Produkcja',
    'D': 'Energetyka',
    'E': 'Gospodarka komunalna',
    'F': 'Budownictwo',
    'G': 'Handel i usługi motoryzacyjne',
    'H': 'Transport i przechowywanie',
    'I': 'Zakwaterowanie i gastronomia',
    'J': 'Informacja i komunikacja',
    'K': 'Finanse',
    'L': 'Nieruchomości',
    'M': 'Nauka i technika',
    'N': 'Administracja i wsparcie',
    'O': 'Administracja publiczna',
    'P': 'Edukacja',
    'Q': 'Zdrowie',
    'R': 'Sztuka',
    'S': 'Inne usługi',
    'T': 'Gospodarstwa domowe',
    'U': 'Organizacje pozaterytorialne',
}

df = df.replace({'PKDMainSection': PKD_dict})


app = dash.Dash(external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Div([
        html.H1('Czas życia spółek'),
        html.Div([
            html.H4('Wybierz zmienną Y'),
            dcc.Dropdown(
                id='Y_dropdown',
                options=[{'label': axis_name[i], 'value': i} for i in axis_key],
                value=axis_key[0],
                placeholder="Wybierz"
            )
        ], style={'width': '22%', 'display': 'inline-block'}),

        html.Div([
            html.H4('Wybierz zmienną X'),
            dcc.Dropdown(
                id='X_dropdown',
                options=[{'label': axis_name[i], 'value': i} for i in axis_key],
                value=axis_key[1],
                placeholder="Wybierz"
            )
        ], style={'width': '22%', 'float': 'right', 'display': 'inline-block'}),

        html.Div([
            html.H4('Wybierz wartości zmiennej X'),
            dcc.Dropdown(
                id='multiX_dropdown',
                options=[{'label': i, 'value': i} for i in df[axis_key[1]].unique()],
                multi=True,
                value=[i for i in df[axis_key[1]].unique()]
            )
        ], style={'width': '22%', 'float': 'right', 'display': 'inline-block'}),

        html.Div([
            html.H4('Wybierz wartości zmiennej Y'),
            dcc.Dropdown(
                id='multiY_dropdown',
                options=[{'label': i, 'value': i} for i in df[axis_key[0]].unique()],
                multi=True,
                value=[i for i in df[axis_key[0]].unique()]
            )
        ], style={'width': '22%', 'display': 'inline-block'}),

        html.Div([
            html.H4('Ustawienia skali:'),
            dcc.RadioItems(
                id='scale_radio',
                options=[
                    {'label': 'skala stała', 'value': 'CONST'},
                    {'label': 'skala dopasowująca', 'value': 'AUTO'},
                ],
                value='CONST',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '22%', 'display': 'inline-block'}),
        
        dcc.Graph(id='heatmap')
    ])
])

@app.callback(
    Output('multiX_dropdown', 'options'), [Input('X_dropdown', 'value')])
def update_multiX_dropdown(tag):
    return [{'label': i, 'value': i} for i in df[tag].unique()]

@app.callback(
    Output('multiX_dropdown', 'value'), [Input('X_dropdown', 'value')])
def update_multiX_dropdown_value(tag):
    return [i for i in df[tag].unique()]

@app.callback(
    Output('multiY_dropdown', 'options'), [Input('Y_dropdown', 'value')])
def update_multiX_dropdown(tag):
    options = [{'label': i, 'value': i} for i in df[tag].unique()]
    return options

@app.callback(
    Output('multiY_dropdown', 'value'), [Input('Y_dropdown', 'value')])
def update_multiX_dropdown_value(tag):
    return [i for i in df[tag].unique()]

@app.callback(
    Output('heatmap', 'figure'),
    [Input('X_dropdown', 'value'),
     Input('Y_dropdown', 'value'),
     Input('multiX_dropdown', 'value'),
     Input('multiY_dropdown', 'value'),
     Input('scale_radio', 'value')]
)
def update_graph(X_dropdown, Y_dropdown, multiX_dropdown, multiY_dropdown, scale):
    if Y_dropdown == X_dropdown:
        heatmap_data = df.groupby([Y_dropdown], as_index=False).mean()
        heatmap_data = heatmap_data.loc[heatmap_data[Y_dropdown].isin(multiY_dropdown)]
        heatmap_data = heatmap_data.loc[heatmap_data[Y_dropdown].isin(multiX_dropdown)]
    else:
        heatmap_data = df.groupby([Y_dropdown, X_dropdown], as_index=False).mean()
        heatmap_data = heatmap_data.loc[heatmap_data[Y_dropdown].isin(multiY_dropdown)]
        heatmap_data = heatmap_data.loc[heatmap_data[X_dropdown].isin(multiX_dropdown)]

    maxsale = heatmap_data[heatmap_data['DurationOfExistenceInMonths'] == heatmap_data['DurationOfExistenceInMonths'].max()]
    maxsale = maxsale.reset_index()
    if scale == 'CONST':
        autoscaling=False
    else:
         autoscaling=True
    fig = go.Figure(go.Heatmap(
            x=heatmap_data[X_dropdown],
            y=heatmap_data[Y_dropdown],
            z=round(heatmap_data['DurationOfExistenceInMonths'], 2),
            zauto=autoscaling,
            zmax=60,
            zmin=10,
            xgap=2,
            ygap=2,
            hoverongaps=False,
            hovertemplate=axis_name[X_dropdown]+': %{x}<br>'+axis_name[Y_dropdown]+': %{y}<br>'+'Miesiące: %{z}<extra></extra>',
            colorscale='Viridis'))
    
    title_text = f'Średni czas życia w zależności od zmiennych: {axis_name[Y_dropdown]}, {axis_name[X_dropdown]}.<br>' + \
        f'Najlepszy wynik: {maxsale[Y_dropdown][0].upper()}, {maxsale[X_dropdown][0]}'    
    fig.update_layout(
        title_text=title_text
    )
    return fig


app.run_server(debug=True, use_reloader=False, port=9000)

