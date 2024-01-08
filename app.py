import dash_bootstrap_components as dbc
from dash import Dash, html, Input, Output, State, dcc
from dash.exceptions import PreventUpdate

from scraper import get_app_id_name_from_appstore_url, retrieve_appstore_reviews, formate_appstore_reviews, \
    get_app_id_from_playstore_url, retrieve_playstore_reviews, format_playstore_reviews

app = Dash(__name__,
           external_stylesheets=[
               dbc.icons.BOOTSTRAP,
               dbc.themes.BOOTSTRAP,
           ])
app.title = "Revscrap"

app.layout = html.Div([
    html.H1("REVIEW SCRAPER", style={"text-align": "center", 'margin-top': '1%'}),
    dbc.Col([
        dbc.Row([
            dbc.Input(
                placeholder="Enter app url...",
                size="lg",
                id='input-url',
                style={'width': '70%', 'margin-right': '1%'}
            ),
            dbc.Button([
                html.I(className='bi bi-search', style={'font-size': '30px'}),
            ],
                id='search-button',
                type='button',
                style={'width': '5%', 'margin-right': '1%'}
            ),
        ], justify="center"),
    ], style={'margin-top': '1%', 'margin-bottom': '1%'}),
    dcc.Download(id="download-data"),
    dcc.Interval(id='interval-log', interval=1000, n_intervals=0),
])


@app.callback(
    Output('download-data', 'data'),
    [Input('search-button', 'n_clicks'),
     Input('input-url', 'n_submit')],
    State('input-url', 'value'),
    prevent_initial_call=True
)
def start_review_scraping(n_clicks, n_submits, url):
    if n_clicks == 0 and n_submits == 0:
        raise PreventUpdate
    if "apps.apple.com" in url:
        app_id, app_name = get_app_id_name_from_appstore_url(url)
        appstore_reviews = retrieve_appstore_reviews(app_name=app_name, app_id=app_id)
        appstore_dataset = formate_appstore_reviews(appstore_reviews)
        return dcc.send_data_frame(appstore_dataset.to_csv,
                                   filename=f"appstore_{app_name}_reviews.csv",
                                   index=False)
    elif "play.google.com" in url:
        app_id = get_app_id_from_playstore_url(url)
        playstore_reviews = retrieve_playstore_reviews(app_id=app_id)
        playstore_dataset = format_playstore_reviews(playstore_reviews)
        return dcc.send_data_frame(playstore_dataset.to_csv,
                                   filename=f"playstore_{app_id.replace('.', '_')}_reviews.csv",
                                   index=False)
    else:
        raise ValueError("Invalid url. Make sure to use a Playstore or Appstore url.")


if __name__ == '__main__':
    app.run_server(debug=False)
