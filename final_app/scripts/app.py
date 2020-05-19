import numpy as np
import pandas as pd
import plotly as plt
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
import os
os.chdir(r'C:\Users\Franciszek.Grymula\Documents\_Szkoła\CEIDG-data-visualisation\final_app\scripts')


## preparation
df = pd.read_csv('../data/ceidg_data_surviv_preprocessed.zip', compression='zip')
df['MainAddressVoivodeshipFromTERCVerbose'] = df['MainAddressVoivodeshipFromTERCVerbose'].fillna('brak')
df['PKDMainSection'] = df['PKDMainSection'].fillna('brak')

# histograms
# correlation, feature importance
df_corr_feat = pd.read_csv('../data/corrs_and_features.csv',index_col=0)

# KM curves
km_features = [
    'MainAddressVoivodeshipFromTERCVerbose', 'IsPhoneNoEncoded',
    'IsEmailEncoded', 'IsWWWEncoded', 'HasLicencesEncoded',
    'HasPolishCitizenshipEncoded', 'ShareholderInOtherCompaniesEncoded',
    'SexEncoded', 'CommunityPropertyEncoded'
]
km_values = {feature: df[feature].unique().tolist() for feature in km_features}

km_curves = pd.read_csv('../data/km_curves.csv')

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

# heatmap
axis_key = ['MainAddressVoivodeshipFromTERCVerbose', 'PKDMainSection', 'SexEncoded', 'HasPolishCitizenshipEncoded', 'MainAddressCommuneTypeFromTERCVerbose']
axis_name = {
    'MainAddressVoivodeshipFromTERCVerbose': 'Województwo',
    'SexEncoded': 'Płeć właściciela',
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

# map
class MapMaker:
    def __init__(self):
        self.all_data = df
        with open('../data/voivo.geojson') as json_file:
            self.voivo_geo_data = json.load(json_file)
        self.voivo_data = pd.DataFrame({
            'id': pd.Categorical([row['id'] for row in self.voivo_geo_data['features']]),
            'name': pd.Categorical([row['properties']['nazwa'].upper() for row in self.voivo_geo_data['features']])
        })
        with open('../data/county.geojson') as json_file:
            self.county_geo_data = json.load(json_file)
        self.county_data = pd.DataFrame({
            'id': pd.Categorical([row['id'] for row in self.county_geo_data['features']]),
            'name': pd.Categorical([row['properties']['nazwa'][7:] for row in self.county_geo_data['features']])
        })

    def _group_and_join_county(self, filtered_data):
        grouped_data = filtered_data.groupby(['MainAddressCountyFromTERCVerbose'], as_index=False)[
            'DurationOfExistenceInMonths'].mean()
        return self.county_data.join(grouped_data.set_index('MainAddressCountyFromTERCVerbose'), on='name')

    def _group_and_join_voivo(self, filtered_data):
        grouped_data = filtered_data.groupby(['MainAddressVoivodeshipFromTERCVerbose'], as_index=False)[
            'DurationOfExistenceInMonths'].mean()
        return self.voivo_data.join(grouped_data.set_index('MainAddressVoivodeshipFromTERCVerbose'), on='name')

    def _make_map(self, data, geo_data):
        fig = px.choropleth_mapbox(
            data,
            geojson=geo_data,
            locations='id',
            color='DurationOfExistenceInMonths',
            hover_data=('DurationOfExistenceInMonths', 'name'),
            color_continuous_scale="OrRd",
            mapbox_style="carto-positron",
            zoom=6,
            range_color=(0, 100),
            center={'lat': 52.1, 'lon': 19.4},
            opacity=1,
            labels={'DurationOfExistenceInMonths': 'Średni czas życia', 'name': 'Nazwa'},
            height=842)
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            hoverlabel=dict(
                bgcolor="white",
                font_size=16))
        return fig

    def make_county_map(self, filtered_data=None):
        if filtered_data is None:
            filtered_data = self.all_data
        prepared_data = self._group_and_join_county(filtered_data)
        return self._make_map(prepared_data, self.county_geo_data)

    def make_voivo_map(self, filtered_data=None):
        if filtered_data is None:
            filtered_data = self.all_data
        prepared_data = self._group_and_join_voivo(filtered_data)
        return self._make_map(prepared_data, self.voivo_geo_data)

map_maker = MapMaker()

def option_div(label, child):
    return html.Div([
        html.Label(label,
                   style={'font-weight': 'bold', 'font-size': 'large', 'width': '100%', 'text-align': 'center',
                              'margin-bottom': '8px'}),
        child
        ], style={'border-style': 'solid', 'padding': '8px', 'margin': '8px', 'border-radius': '16px', 'text-align': 'center'}
    )

def create_check_list(name, id_name, values, labels):
    return option_div(
        name,
        dcc.Checklist(
            id=id_name,
            options=[{'value': val, 'label': lab} for val, lab in zip(values, labels)],
            value=values,
            labelStyle={'display': 'inline-block', 'margin-right': '4px'},
            style={'width': '100%', 'margin-top': '12px'}
        )
    )


## app initialization
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)


## app layout
app.layout = html.Div([
    
    # histograms
    html.Div([
        dcc.Graph(id='lifetime-hist'),
        html.Label('Wybierz dwa województwa:'),
        dcc.Dropdown(
            id='voievodships',
            options=[
                {'label': f, 'value': f}
                    for f in km_values['MainAddressVoivodeshipFromTERCVerbose']
                    if f is not np.nan
            ] + [
                {'label': 'Whole country', 'value': 'whole_dataset'},
                {'label': 'brak', 'value': 'brak'}
            ],
            value=['whole_dataset', 'MAZOWIECKIE'],
            multi=True
        )
        ], style={'width': '70%', 'display': 'inline-block'}),

    # correlation, feature importance
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
    ], style={'width': '70%', 'display': 'inline-block'}),
    
    # KM curve
    html.Div([
        dcc.Graph(id='KM-curve'),
        html.Label('Wybierz zmienną:'),
        dcc.Dropdown(
            id='KM-features',
            options=[
                {'label': f, 'value': f} for f in km_features
            ] + [
                {'label': 'Cała próba', 'value': 'whole_dataset'}
            ],
            value='whole_dataset'
        ),
        dcc.Markdown(KM_description[0]),
        html.Img(
            src='https://wikimedia.org/api/rest_v1/media/math/render/svg/01e97aef4d5ebd2d88d07d2afd392cf12131e657'
        ),
        dcc.Markdown(KM_description[1]),
        html.Img(
            src='https://wikimedia.org/api/rest_v1/media/math/render/svg/8575184e8c8133a3fa1c83e039773178fe51872a'
        ),
        dcc.Markdown(KM_description[2]),
        ], style={'width': '70%', 'display': 'inline-block'}),
    
    # heatmap
    html.Div([
        dcc.Graph(id='heatmap'),
        html.Div([
            html.Label('Wybierz zmienną na osi Y'),
            dcc.Dropdown(
                id='Y_dropdown',
                options=[{'label': axis_name[i], 'value': i} for i in axis_key],
                value=axis_key[0],
                placeholder="Wybierz"
            )
        ], style={'width': '22%', 'display': 'inline-block'}),
        html.Div([
            html.Label('Wybierz zmienną na osi X'),
            dcc.Dropdown(
                id='X_dropdown',
                options=[{'label': axis_name[i], 'value': i} for i in axis_key],
                value=axis_key[1],
                placeholder="Wybierz"
            )
        ], style={'width': '22%', 'float': 'right', 'display': 'inline-block'}),
        html.Div([
            html.Label('Wybierz wartości zmiennej X'),
            dcc.Dropdown(
                id='multiX_dropdown',
                options=[{'label': i, 'value': i} for i in df[axis_key[1]].unique()],
                multi=True,
                value=df[axis_key[1]].unique().tolist()
            )
        ], style={'width': '22%', 'float': 'right', 'display': 'inline-block'}),
        html.Div([
            html.Label('Wybierz wartości zmiennej Y'),
            dcc.Dropdown(
                id='multiY_dropdown',
                options=[{'label': i, 'value': i} for i in df[axis_key[0]].unique()],
                multi=True,
                value=df[axis_key[0]].unique().tolist()
            )
        ], style={'width': '22%', 'display': 'inline-block'}),
        html.Div([
            html.Label('Ustawienia skali:'),
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
    ]),
    
    # map
    html.Div([
        html.Div([
            html.Div([
                html.Button(
                    children=['Odśwież'],
                    type='button',
                    id='refresh_button',
                    style={'border': 'solid', 'width': '100%', 'font-size': 'large', 'text-transform': 'uppercase',
                           'color': 'white', 'background': 'black', 'border-radius': '16px', 'border-color': 'black'}
                    )
                ], style={'padding': '8px'}
            ),
            option_div(
                "Wybierz rodzaj mapy:",
                dcc.Dropdown(
                    id='map_type',
                    options=[
                        {'label': 'Powiaty', 'value': 'county'},
                        {'label': 'Wojewodztwa', 'value': 'voivo'},
                        ],
                    value='county',
                    style={'margin-top': '12px'}
                )
            ),
            create_check_list(
                'Płeć:', 'sex', [1, 0], ['Kobieta', 'Mężczyzna']),
            create_check_list(
                'Numer telefonu:', 'phone', [1, 0], ['Podano', 'Nie podano']),
            create_check_list(
                'Strona internetowa:', 'www', [1, 0], ['Podano', 'Nie podano']),
            create_check_list(
                'Adres e-mail:', 'email', [1, 0], ['Podano', 'Nie podano']),
            create_check_list(
                'Posiadanie licencji:', 'has_licences', [1, 0], ['Tak', 'Nie']),
            create_check_list(
                'Kwartał załozenia firmy:', 'start_quarter', [0, 1, 2, 3],
                ['Pierwszy', 'Drugi', 'Trzeci', 'Czwarty']),
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top', 'box-sizing': 'border-box'}
        ),
        html.Div([
            html.Label('Średni czas życia firmy w miesiącach',
                       style={'font-weight': 'bold', 'font-size': 'x-large', 'width': '100%',
                              'text-align': 'center', 'border-bottom-style': 'solid', 'display': 'inline-block'}),
            dcc.Graph(
                id='voivo-map',
#                figure=map_maker.make_county_map()
                )
        ], style={'width': '70%', 'display': 'inline-block', 'border-left-style': 'solid', 'box-sizing': 'border-box'}
        )
    ], style={'border': 'solid', 'box-sizing': 'border-box', 'border-width': '4px'}
    )
])

              
## app callbacks
# histograms
@app.callback(
    Output('lifetime-hist', 'figure'), [Input('voievodships', 'value')])
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


# correlation, feature importance
@app.callback(
    Output('life-exp-vs-gdp', 'figure'), [Input('column', 'value')])
def update_corr_feat(country):
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


# KM curves
@app.callback(
    Output('KM-curve', 'figure'), [Input('KM-features', 'value')])
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
        for val in km_values[feature]:
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


# heatmap
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
def update_multiY_dropdown(tag):
    return [{'label': i, 'value': i} for i in df[tag].unique()]

@app.callback(
    Output('multiY_dropdown', 'value'), [Input('Y_dropdown', 'value')])
def update_multiY_dropdown_value(tag):
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


# map
@app.callback(
    Output('voivo-map', 'figure'),
    [Input('refresh_button', 'n_clicks'),
     Input('map_type', 'value'),
     Input('sex', 'value'),
     Input('phone', 'value'),
     Input('www', 'value'),
     Input('email', 'value'),
     Input('has_licences', 'value'),
     Input('start_quarter', 'value')],
    )
def login(n_clicks, map_type, sex, phone, www, email, has_licences, start_quarter):
    filtered = map_maker.all_data
    filtered = filtered[filtered['SexEncoded'].isin(sex)]
    filtered = filtered[filtered['IsEmailEncoded'].isin(email)]
    filtered = filtered[filtered['IsPhoneNoEncoded'].isin(phone)]
    filtered = filtered[filtered['IsWWWEncoded'].isin(www)]
    filtered = filtered[filtered['HasLicencesEncoded'].isin(has_licences)]
    filtered = filtered[pd.to_numeric(filtered['DateOfStartingOfTheBusiness'].str[5:7]).apply(lambda x: int((x - 1) / 3)).isin(start_quarter)]
    if map_type == 'voivo':
        result = map_maker.make_voivo_map(filtered)
    else:
        result = map_maker.make_county_map(filtered)
    return result


## run server
#app.run_server(debug=True, use_reloader=False, port=9000)
app.run_server(port=9000)