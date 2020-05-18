import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

input_data = pd.read_csv('ceidg_data_surviv_preprocessed.csv')

#przygotowanie danych
data = input_data.loc[input_data['Terminated'] == 1] #tylko firmy upadłe
data = data[['DurationOfExistenceInMonths', 'MainAddressVoivodeshipFromTERCVerbose', 'Sex', 'PKDMainSection', 'HasPolishCitizenshipEncoded', 'MainAddressCommuneTypeFromTERCVerbose']]
data = data.dropna()
data['Sex'] = np.where(data['Sex'] == 'F', 'Kobieta', 'Mężczyzna')
data['HasPolishCitizenshipEncoded'] = np.where(data['HasPolishCitizenshipEncoded'] == 1, 'Tak', 'Nie')

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

data = data.replace({'PKDMainSection': PKD_dict})



app.layout = html.Div([
    html.H1('Czas działalności biznesów'),
    html.Div([

        html.Div([
            html.H4('Wybierz zmienną Y'),
            dcc.Dropdown(
                id='Y_dropdown',
                options=[{'label': axis_name[i], 'value': i} for i in axis_key],
                value=axis_key[0],
                placeholder="Wybierz",
            ),

        ],
            style={'width': '22%', 'display': 'inline-block'}),

        html.Div([
            html.H4('Wybierz zmienną X'),
            dcc.Dropdown(
                id='X_dropdown',
                options=[{'label': axis_name[i], 'value': i} for i in axis_key],
                value=axis_key[1],
                placeholder="Wybierz",
            ),

        ], style={'width': '22%', 'float': 'right', 'display': 'inline-block'}),

        html.Div([
            html.H4('Filtr zmiennych X'),
            dcc.Dropdown(
                id='multiX_dropdown',
                options=[{'label': i, 'value': i} for i in data[axis_key[1]].unique()],
                multi=True,
                value=[i for i in data[axis_key[1]].unique()],
            ),

        ], style={'width': '22%', 'float': 'right', 'display': 'inline-block'}),

        html.Div([
            html.H4('Filtr zmiennych Y'),
            dcc.Dropdown(
                id='multiY_dropdown',
                options=[{'label': i, 'value': i} for i in data[axis_key[0]].unique()],
                multi=True,
                value=[i for i in data[axis_key[0]].unique()],
            ),

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
            ),

        ], style={'width': '22%', 'display': 'inline-block'}),

        dcc.Graph(id='heatmap',
                  figure={
                      'data': [go.Heatmap(
                          x=data['PKDMainSection'],
                          y=data['MainAddressVoivodeshipFromTERCVerbose'],
                          z=data['DurationOfExistenceInMonths'],
                          name='first legend group',
                          hoverongaps=False,
                          colorscale='Viridis')],
                      'layout': go.Layout(
                          xaxis=dict(title='Rodzaj biznesu'),
                          yaxis=dict(title='Województwo'),
                      )

                  })
    ]),

])

@app.callback(
    dash.dependencies.Output(component_id='multiX_dropdown', component_property='options'),
    [dash.dependencies.Input(component_id='X_dropdown', component_property='value')]
)

def update_multiX_dropdown(tag):
    return [{'label': i, 'value': i} for i in data[tag].unique()]

@app.callback(
    dash.dependencies.Output(component_id='multiX_dropdown', component_property='value'),
    [dash.dependencies.Input(component_id='X_dropdown', component_property='value')]
)
def update_multiX_dropdown_value(tag):
    return [i for i in data[tag].unique()]

@app.callback(
    dash.dependencies.Output(component_id='multiY_dropdown', component_property='options'),
    [dash.dependencies.Input(component_id='Y_dropdown', component_property='value')]
)

def update_multiX_dropdown(tag):
    options = [{'label': i, 'value': i} for i in data[tag].unique()]
    return options

@app.callback(
    dash.dependencies.Output(component_id='multiY_dropdown', component_property='value'),
    [dash.dependencies.Input(component_id='Y_dropdown', component_property='value')]
)
def update_multiX_dropdown_value(tag):
    return [i for i in data[tag].unique()]




@app.callback(
    dash.dependencies.Output(component_id='heatmap', component_property='figure'),
    [dash.dependencies.Input(component_id='X_dropdown', component_property='value'),
     dash.dependencies.Input(component_id='Y_dropdown', component_property='value'),
     dash.dependencies.Input(component_id='multiX_dropdown', component_property='value'),
     dash.dependencies.Input(component_id='multiY_dropdown', component_property='value'),
     dash.dependencies.Input(component_id='scale_radio', component_property='value')]
)
def update_graph(X_dropdown, Y_dropdown, multiX_dropdown, multiY_dropdown, scale):
    if Y_dropdown == X_dropdown:
        heatmap_data = data.groupby([Y_dropdown], as_index=False).mean()
        heatmap_data = heatmap_data.loc[heatmap_data[Y_dropdown].isin(multiY_dropdown)]
        heatmap_data = heatmap_data.loc[heatmap_data[Y_dropdown].isin(multiX_dropdown)]
    else:
        heatmap_data = data.groupby([Y_dropdown, X_dropdown], as_index=False).mean()
        heatmap_data = heatmap_data.loc[heatmap_data[Y_dropdown].isin(multiY_dropdown)]
        heatmap_data = heatmap_data.loc[heatmap_data[X_dropdown].isin(multiX_dropdown)]
    print(X_dropdown, Y_dropdown)
    maxsale = heatmap_data[heatmap_data['DurationOfExistenceInMonths'] == heatmap_data['DurationOfExistenceInMonths'].max()]
    maxsale = maxsale.reset_index()
    if scale == 'CONST':
        autoscaling=False
    else:
         autoscaling=True
    #print(maxsale)
    return {
        'data': [go.Heatmap(
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
            colorscale='Viridis')],
        'layout': go.Layout(
            title='Średni czas trwania działaności w zależności od zmiennych: ' + axis_name[Y_dropdown] + ' i ' + axis_name[X_dropdown] + '. \nNajlepszy wynik: '+str.lower(axis_name[Y_dropdown])+' ' + str.upper(
                maxsale[Y_dropdown][0]) +' '+ str.lower(axis_name[X_dropdown]) + ' ' + str(maxsale[X_dropdown][0])
        )

    }


if __name__ == '__main__':
    app.run_server(debug=True)