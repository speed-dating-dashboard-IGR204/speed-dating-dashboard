#! /bin/python

import pathlib
import datetime
from sys import stderr, stdout
from functools import reduce

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, ClientsideFunction

import pandas as pd

from meta_data import id2race, id2study, id2gender, id2goal, hobbies, id2age
from sankey import generate_sankey, generate_sankey_multi
from cleanDf import cleanDF


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
app.title = "Speed Dating Dashboard"

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

df = pd.read_csv(DATA_PATH / "SpeedDating.csv")
df = cleanDF(df)


def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Speed Dating Analytics"),
            html.H3("Welcome to the Speed Dating Analytics Dashboard"),
            html.Div(
                id="intro",
                children="Explore the bla bla bla ... .",
            ),
        ],
    )


def generate_user_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="user-card",
        children=[
            html.P("Select Gender"),
            dcc.Dropdown(
                id="gender-select",
                options=([{"label": "Unselected", "value": "Unselected"}] +
                         [{"label": id2gender[i], "value": i} for i in df["gender"].dropna().unique()]),
                value="Unselected",
            ),
            html.Br(),
            html.P("Select Age"),
            dcc.Dropdown(
                id="age-select",
                options=([{"label": "Unselected", "value": "Unselected"}] +
                         [{"label": id2age[i], "value": i} for i in df["age_class"].dropna().unique()]),
                value="Unselected",
            ),
            html.Br(),
            html.P("Select Ethnicity"),
            dcc.Dropdown(
                id="race-select",
                options=([{"label": "Unselected", "value": "Unselected"}] +
                         [{"label": id2race[i], "value": i} for i in df["race"].sort_values().dropna().unique()]),
                value="Unselected",
            ),
            html.Br(),
            html.Div(
                id="religion_div",
                children=[
                    html.P("Filter by Religion Importance ?"),
                    html.Br(),
                    dcc.RadioItems(
                        id='check_rel',
                        options=[
                            {'label': 'Yes', 'value': 'True'},
                            {'label': 'No', 'value': 'False'},
                        ],
                        value='True',
                        labelStyle={'display': 'inline-block'}
                    ),  
                    html.Br(),
                    html.Div(
                        id="religion_slider",
                        hidden=False,
                        children=[
                            html.P("How is religion important for you ?"),
                            dcc.Slider(
                                id="imprelig",
                                min=0,
                                max=10,
                                value=5,
                                marks={
                                    0: {'label': '0 - Not Important'},
                                    5: {'label': '5'},
                                    10: {'label': '10 - Very Important'}
                                }
                            )
                        ]
                    ), 
                ]
            ),
            #html.Br(),
            #html.P("Select "),
            #dcc.Dropdown(
            #    id="gout-target",
            #    options=[{"label": i, "value": i} for i in df.columns.dropna().unique()], #à changer plus tard df.columns.dropna().unique()
            #    value="a",
            #    multi=True,
            #),
            #html.Br(),
            #html.P("Select Check-In Time"),
            #dcc.DatePickerRange(
            #    id="date-picker-select",
            #    start_date=datetime.datetime(2014, 1, 1),
            #    end_date=datetime.datetime(2014, 1, 15),
            #    min_date_allowed=datetime.datetime(2014, 1, 1),
            #    max_date_allowed=datetime.datetime(2014, 12, 31),
            #    initial_visible_month=datetime.datetime(2014, 1, 1),
            #),
            html.Br(),
            html.P("Select hobbies"),
            dcc.Dropdown(
                id="admit-select",
                options=[{"label": i, "value": i} for i in hobbies],
                value="a",
                multi=True,
            ),
            html.Br(),
            html.Div(
                id="reset-btn-outer",
                children=html.Button(id="reset-btn", children="Reset", n_clicks=0),
            ),
        ],
    )


app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url("Breve-Speed-Dating.jpg"))],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(), generate_user_card()]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                # Sankey Diagram
                html.Div(
                    id="sankey_diagram_div",
                    children=[
                        # html.B("Patient Volume"),
                        html.Hr(),
                        dcc.Graph(id="sankey_diagram",  figure=generate_sankey_multi(df=df, target_dict={"age": 28}, criteria_cols=["field_cd", "race", "goal"])),
                    ],
                ),
                html.Div(
                    id="histo_money_div",
                    children=[
                        dcc.Graph(id='histo_money')
                    ]
                ),
                # Patient Wait time by Department
                # html.Div(
                #     id="wait_time_card",
                #     children=[
                #         html.B("Patient Wait Time and Satisfactory Scores"),
                #         html.Hr(),
                #         html.Div(id="wait_time_table", children=initialize_table()),
                #     ],
                # ),
            ],
        ),
    ],
)


@app.callback(
    # [
    Output("sankey_diagram", "figure"),
    # Output('histo_money', 'figure')],
    [
        Input("age-select", "value"),
        Input("gender-select", "value"),
        Input("race-select", "value"),
        # Input("imprelig", "value"),
    ],
)
def update_sankey(age, gender, race):
    target_dict = {}
    if age != "Unselected":
        target_dict.update({"age_class": age})
    if gender != "Unselected":
        target_dict.update({"gender": gender})
    if race != "Unselected":
        target_dict.update({"race": race})
    # "imprelig": imprelig
    return generate_sankey_multi(df=df, target_dict=target_dict, criteria_cols=["field_cd", "race", "goal"])


# @app.callback(
#     [
#         Output("age-select", "options"),
#         Output("gender-select", "options"),
#         Output("race-select", "options"),
#     ],
#     [
#         Input("age-select", "value"),
#         Input("gender-select", "value"),
#         Input("race-select", "value"),
#         # Input("imprelig", "value"),
#     ],
# )
# def update_dropdown_options(age, gender, race):
#     """Dynamically update the dropdown options
#
#     The goal is to offer only those options for which some data is present in the data frame"""
#
#     target_dict = {}
#     if age != "Unselected":
#         target_dict.update({"age": age})
#     if gender != "Unselected":
#         target_dict.update({"gender": gender})
#     if race != "Unselected":
#         target_dict.update({"race": race})
#     # "imprelig": imprelig
#
#     target_select = reduce(lambda x, y: x.__and__(y), [(df[k] == v) for k, v in target_dict.items()])
#     df_target = df[target_select]
#
#     return generate_sankey_multi(df=df, target_dict=target_dict, criteria_cols=["field_cd", "race"])


""" @app.callback(
     #Output('click-data', 'children'),
    Input('basic-interactions', 'clickData'))
def display_click_data(clickData):
    pass """

@app.callback(
    [Output("religion_slider",'hidden'),Output("imprelig", "value")],
    [Input('check_rel','value')]
)
def show_relimp(toggle_value):
    if toggle_value == 'True':
        return (False,5)
    else:
        return (True,None)

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
