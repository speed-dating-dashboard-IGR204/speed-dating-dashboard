import pathlib
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import pandas as pd

from meta_data import id2race, id2study, id2gender
from sankey import generate_sankey


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
app.title = "Speed Dating Dashboard"

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

df = pd.read_csv(DATA_PATH / "SpeedDating.csv")


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
                options=[{"label": id2gender[i], "value": i} for i in df["gender"].dropna().unique()],
                value=min(df["gender"].dropna().unique()),
            ),
            html.Br(),
            html.P("Select Age"),
            dcc.Dropdown(
                id="age-select",
                options=[{"label": i, "value": i} for i in df["age"].dropna().unique()],
                value=min(df["age"].dropna().unique()),
            ),
            html.Br(),
            html.P("Select Check-In Time"),
            dcc.DatePickerRange(
                id="date-picker-select",
                start_date=datetime.datetime(2014, 1, 1),
                end_date=datetime.datetime(2014, 1, 15),
                min_date_allowed=datetime.datetime(2014, 1, 1),
                max_date_allowed=datetime.datetime(2014, 12, 31),
                initial_visible_month=datetime.datetime(2014, 1, 1),
            ),
            html.Br(),
            html.Br(),
            html.P("Select "),
            dcc.Dropdown(
                id="admit-select",
                options=[{"label": i, "value": i} for i in ["a", "b", "c"]],
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
                    id="sankey_diagram",
                    children=[
                        html.B("Patient Volume"),
                        html.Hr(),
                        dcc.Graph(id="sankey_diagram_hm", figure=generate_sankey(df=df)),
                    ],
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

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
