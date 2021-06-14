import os
import glob
from importlib import import_module
import numpy as np

import flask
import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html



# Add a static route to serve static images (c.f. the serve_image callback down below)
# For the moment this is only needed to serve the data2i logo!
image_directory = pyntakt.config.root_dir.resolve() / 'dashboard' / 'images'
list_of_images = [os.path.basename(x) for x in glob.glob(str(image_directory / '*.png'))]
static_route = '/static/'

sensor_select_dropdown = dcc.Dropdown(
    id='sensor-multi-select', placeholder="Sélection des capteurs...",
    multi=True, searchable=True
)

page_title = dbc.Row(
    [
        html.A(
            dbc.Col(html.Img(src=os.path.join(static_route, 'data2i.png'), height="25px",
                             style={'align': 'right'})),
            href="https://www.data2i.fr",
            target='_blank'
        ),
        html.Div("INTAKT", style={'font-size': '20px', 'font-weight': 'bold', 'color': 'white'}),
        html.Span(style={'width': '10px'}, ),
        html.Span(u"\u2630", style={"font-size": "20px", "cursor": "pointer", 'color': 'white', 'font-weight': 'bold'},
                  id='toggle-menu')
    ],
    style={'height': '30px', 'position': 'fixed', 'top': '0px', 'width': '100%',
           'background-color': '#008D4C', 'z-index': 10}
)


body = dbc.Container(
    [
        dbc.Row(
            [
                sidenav.sidenav,
                # Tab content
                html.Div(id="tab_content", className="row", style={"margin": "2% 3%"})
            ]
        )
    ],
    className="mt-4", id='body', style={}
)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "intakt"
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([page_title, body], id='main', style={})


# @app.callback(
#     Output("sensor-multi-select", "options"),
#     [Input("select-data-source", "value")],
# )
def sensor_mselect_fill(value):
    if value:
        pipeline_module = import_module('pyntakt.poc.' + value)
        sensor_list = pipeline_module.get_data_info()['sensor_ids']
        return [{'label': s, 'value': s} for s in sensor_list]
    else:
        return []


@app.callback(
    Output('mySidenav', 'style'),
    [Input('toggle-menu', 'n_clicks')],
    [State('mySidenav', 'style')],
)
def toggle_sidenav_update(n_clicks, old_style):
    new_style = old_style if old_style else {}
    if n_clicks:
        if n_clicks % 2 != 0:
            new_style['left'] = '-180px'
        elif n_clicks % 2 == 0:
            new_style['left'] = '0px'
    return new_style


@app.callback(
    Output('body', 'style'),
    [Input('toggle-menu', 'n_clicks')],
    [State('body', 'style')],
)
def toggle_main_update(n_clicks, old_style):
    new_style = old_style if old_style else {}
    if n_clicks:
        if n_clicks % 2 != 0:
            new_style['marginLeft'] = '0px'
        elif n_clicks % 2 == 0:
            new_style['marginLeft'] = '180px'
    return new_style


# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
@app.server.route('{}<image_path>'.format(static_route))
def serve_image(image_path):
    if image_path not in list_of_images:
        raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(image_directory, image_path)


@app.callback(Output("tab_content", "children"), [Input("select-data-source", "value")])
def render_content(data_source):
    if data_source == "demo":
        return pyntakt.dashboard.demo.layout


@app.callback(
    Output('demo-plots', 'children'),
    [Input('generate-plot-button', 'n_clicks')],
    [State('n-latent', 'value'), State('n-features', 'value'), State('n-samples', 'value'),
     State('model-seed', 'value'), State('noise-amplitude', 'value'),
     State('shifted-feature', 'value'), State('shift-amplitude', 'value')],
)
def generate_data_and_plot(n_clicks, n_latent, n_features, n_samples, model_seed, noise_amplitude,
                           shifted_feature, shift_amplitude):
    if n_clicks:
        get_demo_data = pyntakt.poc.demo.get_demo_data
        demo_data = get_demo_data(n_dof=n_latent, n_features=n_features, n_samples=n_samples,
                                  model_seed=model_seed, noise_amplitude=float(noise_amplitude),
                                  shifted_feature=int(shifted_feature), shift_amplitude=float(shift_amplitude))

        return dcc.Graph(figure=pyntakt.plotting.fig_line_grid(np.concatenate(demo_data)))


@app.callback(
    Output('train-error-plots', 'children'),
    [Input('train-model-button', 'n_clicks')],
    [State('n-latent', 'value'), State('n-features', 'value'), State('n-samples', 'value'),
     State('model-seed', 'value'), State('noise-amplitude', 'value'),
     State('shifted-feature', 'value'), State('shift-amplitude', 'value'),
     State('n-epochs', 'value')],
)
def train_model_and_plot(n_clicks, n_latent, n_features, n_samples, model_seed, noise_amplitude,
                         shifted_feature, shift_amplitude, n_epochs):
    if n_clicks:
        get_demo_data = pyntakt.poc.demo.get_demo_data
        _, _, test_data, anomalous_data = get_demo_data(
            n_dof=n_latent, n_features=n_features, n_samples=n_samples,
            model_seed=model_seed, noise_amplitude=float(noise_amplitude),
            shifted_feature=int(shifted_feature), shift_amplitude=float(shift_amplitude))

        get_autoencoder2 = pyntakt.poc.demo.get_autoencoder2
        model = get_autoencoder2(n_epochs=n_epochs, n_dof=n_latent, n_features=n_features, n_samples=n_samples,
                                 model_seed=model_seed, noise_amplitude=float(noise_amplitude),
                                 shifted_feature=int(shifted_feature), shift_amplitude=float(shift_amplitude),
                                 )

        prediction_abs_error_test = np.abs(model.predict(test_data) - test_data)
        prediction_abs_error_anomalous = np.abs(model.predict(anomalous_data) - anomalous_data)

        return dcc.Graph(figure=pyntakt.plotting.fig_histogram_grid_compare(prediction_abs_error_test,
                                                                            prediction_abs_error_anomalous,
                                                                            n_columns=3))


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)