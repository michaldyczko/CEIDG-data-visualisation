import plotly.express as px
import pandas as pd
import json

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State


DATA_PATH = 'ceidg_data_surviv_preprocessed.csv'


class MapMaker:

    def __init__(self):
        print('Reading data...')
        self.all_data = pd.read_csv(DATA_PATH)
        self.all_data = self.all_data[self.all_data['Terminated'] == True]

        with open('voivo.geojson') as json_file:
            self.voivo_geo_data = json.load(json_file)

        self.voivo_data = pd.DataFrame({
            'id': pd.Categorical([row['id'] for row in self.voivo_geo_data['features']]),
            'name': pd.Categorical([row['properties']['nazwa'].upper() for row in self.voivo_geo_data['features']])
        })

        with open('county.geojson') as json_file:
            self.county_geo_data = json.load(json_file)

        self.county_data = pd.DataFrame({
            'id': pd.Categorical([row['id'] for row in self.county_geo_data['features']]),
            'name': pd.Categorical([row['properties']['nazwa'][7:] for row in self.county_geo_data['features']])
        })

        print('Data has been read correctly')

    def _group_and_join_county(self, filtered_data):
        grouped_data = filtered_data.groupby(['MainAddressCountyFromTERCVerbose'], as_index=False)[
            'DurationOfExistenceInMonths'].mean()
        return self.county_data.join(grouped_data.set_index('MainAddressCountyFromTERCVerbose'), on='name')

    def _group_and_join_voivo(self, filtered_data):
        grouped_data = filtered_data.groupby(['MainAddressVoivodeshipFromTERCVerbose'], as_index=False)[
            'DurationOfExistenceInMonths'].mean()
        return self.voivo_data.join(grouped_data.set_index('MainAddressVoivodeshipFromTERCVerbose'), on='name')

    def _make_map(self, data, geo_data):
        fig = px.choropleth_mapbox(data,
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
                font_size=16
            )
        )
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
app = dash.Dash(__name__)


def option_div(label, child):
    return html.Div(
        [
            html.Label(label,
                       style={'font-weight': 'bold', 'font-size': 'large', 'width': '100%', 'text-align': 'center',
                              'margin-bottom': '8px'}),
            child
        ],
        style={'border-style': 'solid', 'padding': '8px', 'margin': '8px', 'border-radius': '16px', 'text-align': 'center'}
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


app.layout = html.Div(children=[
    html.Div([
        html.Div(
            [
                html.Div(
                    [
                        html.Button(
                            children=['Odśwież'],
                            type='button',
                            id='refresh_button',
                            style={'border': 'solid', 'width': '100%', 'font-size': 'large', 'text-transform': 'uppercase',
                                   'color': 'white', 'background': 'black', 'border-radius': '16px', 'border-color': 'black'}
                        )
                    ],
                    style={'padding': '8px'}
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
                create_check_list('Płeć:', 'sex', [1, 0], ['Female', 'Male']),
                create_check_list('Numer telefonu:', 'phone', [1, 0], ['Podano', 'Nie podano']),
                create_check_list('Strona internetowa:', 'www', [1, 0], ['Podano', 'Nie podano']),
                create_check_list('Adres e-mail:', 'email', [1, 0], ['Podano', 'Nie podano']),
                create_check_list('Posiadanie licencji:', 'has_licences', [1, 0], ['Tak', 'Nie']),
                create_check_list('Kwartał załozenia firmy:', 'start_quarter',
                                  [0, 1, 2, 3],
                                  ['Pierwszy', 'Drugi', 'Trzeci', 'Czwarty']
                                  ),
            ],
            style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top',
                   'box-sizing': 'border-box'}
        ),
        html.Div(
            [
                html.Label('Średni czas życia firmy w miesiącach',
                           style={'font-weight': 'bold', 'font-size': 'x-large', 'width': '100%',
                                  'text-align': 'center', 'border-bottom-style': 'solid', 'display': 'inline-block'}),
                dcc.Graph(
                    id='voivo-map',
                    figure=map_maker.make_county_map()
                )
            ],
            style={'width': '70%', 'display': 'inline-block', 'border-left-style': 'solid',
                   'box-sizing': 'border-box'}
        )
    ],
        style={'border': 'solid', 'box-sizing': 'border-box', 'border-width': '4px'}
    )
])


@app.callback(
    output=Output('voivo-map', 'figure'),
    inputs=[
        Input('refresh_button', 'n_clicks'),
    ],
    state=[
        State('map_type', 'value'),
        State('sex', 'value'),
        State('phone', 'value'),
        State('www', 'value'),
        State('email', 'value'),
        State('has_licences', 'value'),
        State('start_quarter', 'value'),
    ]
)
def login(n_clicks, map_type, sex, phone, www, email, has_licences, start_quarter):
    filtered = map_maker.all_data
    filtered = filtered[filtered['SexEncoded'].isin(sex)]
    filtered = filtered[filtered['IsEmailEncoded'].isin(email)]
    filtered = filtered[filtered['IsPhoneNoEncoded'].isin(phone)]
    filtered = filtered[filtered['IsWWWEncoded'].isin(www)]
    filtered = filtered[filtered['HasLicencesEncoded'].isin(has_licences)]
    filtered = filtered[pd.to_numeric(filtered['DateOfStartingOfTheBusiness'].str[5:7]).apply(lambda x: int((x - 1) / 3)).isin(start_quarter)]

    return map_maker.make_voivo_map(filtered) if map_type == 'voivo' else map_maker.make_county_map(filtered)


if __name__ == '__main__':
    app.run_server(debug=True)
