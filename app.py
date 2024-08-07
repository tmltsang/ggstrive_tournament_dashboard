from dash import Dash, html, dcc, no_update, Output, Input, State
import dash_bootstrap_components as dbc
from graphing import graph
from database.gg_data_client import GGDataClient
from constants import *
import copy

data_client = GGDataClient()
df = data_client.get_all_matches()
df_match_stats = data_client.get_all_match_stats()
df_asuka_stats = data_client.get_all_asuka_data()

full_index = ['tournament', 'tournament_round', 'set_index', 'round_index']
df.set_index(full_index, inplace=True)
df.sort_index(level=full_index, inplace=True)
df_match_stats.set_index(full_index, inplace=True)
df_match_stats.sort_index(level=full_index, inplace=True)
df_asuka_stats.set_index(['tournament', 'tournament_round', 'set_index', 'round_index', 'player_side'], inplace=True)
df_asuka_stats.sort_index(level=['tournament', 'tournament_round', 'set_index', 'round_index', 'player_side'], inplace=True)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
w3schools = 'https://www.w3schools.com/w3css/4/w3.css'
external_stylesheets = [dbc.themes.JOURNAL, dbc_css, w3schools]

app = Dash(__name__, suppress_callback_exceptions = True, external_stylesheets=external_stylesheets)
app.title = 'GG Strive Tournament Stats'
server = app.server


dropdowns = html.Div([
    dbc.Label("Tournament"),
    dcc.Dropdown([{'label': tournament.replace('_', ' ').title(), 'value': tournament} for tournament in df.index.unique(level='tournament')], 'evo', clearable=False, id='tournament-selection', className="dbc"),
    dbc.Label("Tournament Round"),
    dcc.Dropdown(clearable=False, id='tr-selection', className="dbc"),
    dbc.Label("Match number"),
    dcc.Dropdown(id='set-selection', clearable=False, className="dbc"),
])

controls = dbc.Card([dropdowns])
graphs = dbc.Card([dbc.Spinner(dcc.Graph(id='pred_graph', style={'height': '80vh', 'visibility': 'hidden', 'text-align': 'center'}), color="primary"), dcc.Tooltip(id='pred-graph-tooltip')])

hearts_default = [html.Img(src=app.get_asset_url(FULL_HEART), className="sub_heart"), html.Img(src=app.get_asset_url(FULL_HEART), className="main_heart")]

pred_graph_tab = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col(className="player_portrait_container", id="p1_char_portrait", width=2),
            dbc.Col([
            dbc.Row([
                dbc.Col([html.Div(hearts_default)], id="p1_round_count", className='p1', width=5),
                dbc.Label("Round", className="bar_label"),
                dbc.Col([html.Div(hearts_default[::-1])], id="p2_round_count", className='p2', width=5),
            ], justify='center', style={"height": "15%"}),
            dbc.Row([
                dbc.Col([html.Div([html.Div(["100%"], style={"--w": "100%"}, className="p1_health bar_text")], className='p1 bar_container')], id="p1_health_bar", className="p1", width=5),
                dbc.Label("Health", className="bar_label"),
                dbc.Col([html.Div([html.Div(["100%"], style={"--w": "100%"}, className="p2_health bar_text")], className='p2 bar_container')], id="p2_health_bar", className="p2", width=5),
            ], justify='center'),
            dbc.Row([
                dbc.Col([html.Div([html.Div(["100%"], style={"--w": "100%"}, className="p1_burst bar_text")], className='p1 bar_container', style={"width": "33%"})], id="p1_burst_bar", className="p1", width=5),
                dbc.Label("Burst", className="bar_label"),
                dbc.Col([html.Div([html.Div(["100%"], style={"--w": "100%"}, className="p2_burst bar_text")], className='p2 bar_container', style={"width": "33%"})], id="p2_burst_bar", className="p2", width=5),
            ], justify='center'),
            dbc.Row([
                dbc.Col([html.Div([html.Div(["0%"], style={"--w": "0%"}, className="p1_tension bar_text")], className='p1 bar_container')], id="p1_tension_bar", className="p1", width=5),
                dbc.Label("Tension", className="bar_label"),
                dbc.Col([html.Div([html.Div(["0%"], style={"--w": "0%"}, className="p2_tension bar_text")], className='p2 bar_container')], id="p2_tension_bar", className="p2", width=5),
            ], justify='center'),
            dbc.Row([
                dbc.Col([html.Div([0], className='bar_label')], id="p1_counter", className="p1", width=5),
                dbc.Label("Counter", className="bar_label"),
                dbc.Col([html.Div([0], className='bar_label')], id="p2_counter", className="p2", width=5),
            ], justify='center'),
            ], width=8),
            dbc.Col(className="player_portrait_container", id="p2_char_portrait", width=2),
        ]),
        html.Div([
            dbc.Row([
                    dbc.Col(id="p1_spell", className="p1", width=5),
                    dbc.Label("Spells", className="bar_label"),
                    dbc.Col(id="p2_spell", className="p2", width=5),
                ], justify='center'),
            dbc.Row([
                    dbc.Col([html.Div(["0%"])], id="p1_spell_percentile", className="p1", width=5),
                    dbc.Label("Spell Percentile", className="bar_label"),
                    dbc.Col([html.Div(["0%"])], id="p2_spell_percentile", className="p2", width=5),
                ], justify='center'),], style={"display": "none"}, id="spell_info"
        ),
        dbc.Row([
            dbc.Label("Round Win Probability", style={'width': '25%'}, className="bar_label"),
        ], justify='center'),
        dbc.Row([
            html.Div([html.Div([html.Div("50%"), html.Div("50%")], style={"--w": "50%"}, className="win_prob_bar bar_text")], id='round_win_prob_bar', className='bar_container'),
        ], justify='center'),
        dbc.Row([
            dbc.Label("Set Win Probability", style={'width': '25%'}, className="bar_label"),
        ], justify='center'),
            dbc.Row([
            html.Div([html.Div([html.Div("50%"), html.Div("50%")], style={"--w": "50%"}, className="win_prob_bar bar_text")], id='set_win_prob_bar', className='bar_container'),
        ], justify='center'),
        dbc.Row([
            graphs,
        ])
    ])
)

match_stats = dbc.Card(
    dbc.CardBody([
        dcc.Graph(id='burst_graph', style={'height': '45vh', 'visibility': 'hidden'}),
        dcc.Graph(id='burst_bar_graph', style={'height': '45vh', 'visibility': 'hidden'}),
        dcc.Graph(id='tension_graph', style={'height': '45vh', 'visibility': 'hidden'}),
        dcc.Graph(id='stats_graph', style={'height': '45vh', 'visibility': 'hidden'})
    ])
)

app.layout = dbc.Container(
    [
        html.H1(children=html.Img(src='https://dustloop.com/wiki/images/5/55/GGST_Logo.png', style={'display':'block', 'width':'25%', 'height':'auto'}), style={'display': 'flex', 'justify-content': 'center'} ,className="dbc"),
        dbc.Row([
            dbc.Col([
                controls,
            ], width=2),
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(pred_graph_tab, id="pred_tab", tab_id="pred_tab", label="Match Prediction"),
                    dbc.Tab(match_stats, id="match_tab", tab_id="match_tab", label="Match Stats"),
#                    dbc.Tab(asuka_stats, id="asuka_tab", tab_id="asuka_tab", label="Asuka Spells", tab_style={'display': 'none'})
                ], id="tabs", active_tab="pred_tab")
            ], width={"size": 10}),
        ])

    ],
    fluid=True,
    className="dbc"
)

@app.callback(
    Output('tr-selection', 'options'),
    [Input('tournament-selection', 'value')]
)
def update_tr_dropdown(tournament):
    return [{'label': f'{TOURNAMENT_ROUND_MAPPINGS[tr_round[0]]}: {tr_round[1]} vs {tr_round[2]}', 'value': tr_round[0]} for tr_round in df.loc[tournament].reset_index().set_index(['tournament_round', 'p1_player_name', 'p2_player_name']).index.unique()]

@app.callback(
    Output('tr-selection', 'value'),
    [Input('tr-selection', 'options')]
)
def set_initial_tr_value(options):
    return options[0]['value']


@app.callback(
    Output('set-selection', 'options'),
    [Input('tr-selection', 'value')],
    State('tournament-selection', 'value')
)
def update_match_dropdown(tr, tournament):
    return [{'label': match+1, 'value':match} for match in df.loc[(tournament, tr)].index.unique(level='set_index')]

@app.callback(
    Output('set-selection', 'value'),
    [Input('set-selection', 'options')]
)
def set_initial_set_value(options):
    return options[0]['value']

@app.callback(
    [Output('p1_char_portrait', 'children'),
    Output('p2_char_portrait', 'children'),
    Output('pred_graph', 'figure'),
    Output('pred_graph', 'style'),
    Output('burst_graph', 'figure'),
    Output('burst_graph', 'style'),
    Output('burst_bar_graph', 'figure'),
    Output('burst_bar_graph', 'style'),
    Output('tension_graph', 'figure'),
    Output('tension_graph', 'style'),
    Output('stats_graph', 'figure'),
    Output('stats_graph', 'style'),
    Output('spell_info', 'style')],
    [Input('tr-selection', 'value'),
    Input('set-selection', 'value'),],
    [State('tabs', 'active_tab'),
     State('tournament-selection', 'value')],
)
def update_graph(tr, set_num, active_tab, tournament):
    dff = df.loc[(tournament, tr, set_num)]
    match_stats_dff = df_match_stats.loc[(tournament, tr, set_num)]
    asuka_stats_dff = None
    spell_info_style = {'display': 'none'}
    p1_player_name = dff['p1_player_name'].iat[0]
    p2_player_name = dff['p2_player_name'].iat[0]

    p1_char_name = dff['p1_name'].iat[0]
    p2_char_name = dff['p2_name'].iat[0]

    p1_set_win = dff['p1_set_win'].iat[0]
    p1_round_win = dff['p1_round_win'].groupby("round_index").first().tolist()
    fig = graph.create_pred_graph(dff, p1_player_name, p2_player_name, p1_char_name, p2_char_name)
    if df_asuka_stats.index.isin([(tournament, tr, set_num)]).any():
        asuka_stats_dff = df_asuka_stats.loc[(tournament, tr, set_num)]
        spell_info_style = {}
        fig = graph.create_asuka_graph(fig, asuka_stats_dff, p1_player_name, p2_player_name)
    else:
        if active_tab == 'asuka_tab':
            active_tab = 'pred_tab'

    match_stats_style = {'height': '45vh', 'visibility': 'visible'}
    burst_match_stats_fig = graph.create_pie_match_stats_graph(match_stats_dff, p1_player_name, p2_player_name, p1_set_win, p1_round_win, 'burst_count', 'Psych Burst Count')
    burst_bar_match_stats_fig = graph.create_pie_match_stats_graph(match_stats_dff, p1_player_name, p2_player_name, p1_set_win, p1_round_win, 'burst_use', 'Burst Bar Used')
    tension_match_stats_fig = graph.create_pie_match_stats_graph(match_stats_dff, p1_player_name, p2_player_name, p1_set_win, p1_round_win, 'tension_use', 'Tension Used')
    # burst_match_stats_fig = graph.create_sunburst_match_stats_graph(match_stats_dff, 'burst_count', 'Psych Burst Count', player_root=False)
    # burst_bar_match_stats_fig = graph.create_sunburst_match_stats_graph(match_stats_dff, 'burst_use', 'Burst Bar Used', player_root=False)
    # tension_match_stats_fig = graph.create_sunburst_match_stats_graph(match_stats_dff, 'tension_use', 'Tension Used', player_root=False)
    fh_match_stats_fig = graph.create_sunburst_match_stats_graph(match_stats_dff, 'first_hit', 'First Hits', player_root=False)

    p1_player_name_div = [html.Img(src=app.get_asset_url(f'images/portraits/{p1_char_name}.png'), className="player_portrait"), html.Div([p1_player_name.upper()], className="player_name_overlay name_shadow", style={"--outline": PLAYER_COLOURS(P1)})]
    p2_player_name_div = [html.Img(src=app.get_asset_url(f'images/portraits/{p2_char_name}.png'), className="player_portrait"), html.Div([p2_player_name.upper()], className="player_name_overlay name_shadow", style={"--outline": PLAYER_COLOURS(P2)})]

    return p1_player_name_div, p2_player_name_div, fig,  {'height': '50vh', 'visibility': 'visible'},\
            burst_match_stats_fig, match_stats_style,\
            burst_bar_match_stats_fig, match_stats_style,\
            tension_match_stats_fig, match_stats_style,\
            fh_match_stats_fig, match_stats_style,\
            spell_info_style

@app.callback(
    Output('p1_round_count', 'children'),
    Output('p2_round_count', 'children'),
    Output('p1_health_bar', 'children'),
    Output('p2_health_bar', 'children'),
    Output('p1_burst_bar', 'children'),
    Output('p2_burst_bar', 'children'),
    Output('p1_tension_bar', 'children'),
    Output('p2_tension_bar', 'children'),
    Output('p1_counter', 'children'),
    Output('p2_counter', 'children'),
    Output('p1_spell', 'children'),
    Output('p2_spell', 'children'),
    Output('p1_spell_percentile', 'children'),
    Output('p2_spell_percentile', 'children'),
    Output('round_win_prob_bar', 'children'),
    Output('set_win_prob_bar', 'children'),
    Input('pred_graph', 'hoverData'),
    State("pred_graph", "figure")
)
def display_hover_data(hoverData, figure):
    bars = {}
    bars[P1] = {}
    bars[P2] = {}
    data_dict = {}
    spell_data = []
    if hoverData != None:
        for point in hoverData["points"]:
            if "customdata" in point.keys():
                trace_name = figure['data'][point['curveNumber']]['name']
                if trace_name.endswith(' Spells'):
                    spell_data.append(point)
                else:
                    player_side = point['customdata'][PRED_HD_INDEX['side']]
                    data_dict[player_side] = {}
                    data_dict[player_side]['customdata'] = point['customdata']
                    data_dict[player_side]['set_win_prob'] = point['y']
    else:
        data_dict = DEFAULT_PRED_HD

    spells = display_asuka_spell_data(spell_data)

    p1_round_win_prob =  round(data_dict[P1]['customdata'][PRED_HD_INDEX['round_win']], 1)

    bars['round_win_prob'] = html.Div([html.Div(f'{p1_round_win_prob}%'), html.Div(f'{round(100 - p1_round_win_prob, 1)}%')], style={"--w": f'{p1_round_win_prob}%'}, className="win_prob_bar bar_text")
    p1_set_win_prob =  round(data_dict[P1]['set_win_prob'], 1)
    bars['set_win_prob'] = html.Div([html.Div(f'{p1_set_win_prob}%'), html.Div(f'{round(100 - p1_set_win_prob, 1)}%')], style={"--w": f'{p1_set_win_prob}%'}, className="win_prob_bar bar_text")

    for player_side in data_dict.keys():
        data = data_dict[player_side]['customdata']
        for bar in ["health", "burst", "tension"]:
            value = round(100 * data[PRED_HD_INDEX[bar]], 2)
            background_style = {}
            bar_class_name = f'{player_side}_{bar} bar_text'
            background_class_name = f'bar_container {player_side}'
            if bar == "health" and data[PRED_HD_INDEX['curr_damaged']]:
                background_class_name += " curr_dmg"
                background_style = {"--cd_w": f'{value+10}%'}
            elif bar == "burst":
                background_style = {"width": "40%"}
            bars[player_side][bar] = html.Div([html.Div([f"{value}%"], style={"--w": f"{value}%"}, className=bar_class_name)], className=background_class_name, style=background_style)
        bars[player_side]["counter"] = html.Div([data[PRED_HD_INDEX["counter"]]], className=f"bar_label {player_side}", style={"font-size": "30px"})
        curr_hearts = copy.deepcopy(hearts_default)
        for i in range(data[PRED_HD_INDEX['round_count']]):
            curr_hearts[i].src = app.get_asset_url(EMPTY_HEART)
        heart_side = "p1" if player_side == P2 else "p2"
        curr_hearts = curr_hearts if heart_side == P1 else curr_hearts[::-1]
        bars[heart_side]["round_count"] = html.Div(curr_hearts)

    return bars[P1]["round_count"], bars[P2]["round_count"],\
            bars[P1]["health"], bars[P2]["health"],\
            bars[P1]["burst"], bars[P2]["burst"],\
            bars[P1]["tension"], bars[P2]["tension"],\
            bars[P1]["counter"], bars[P2]["counter"],\
            spells[P1]['spell'], spells['p2']['spell'],\
            spells[P1]['percentile'], spells['p2']['percentile'],\
            bars['round_win_prob'], bars['set_win_prob']

# @app.callback(
#     Output('spells', 'children'),
#     Input('asuka_graph', 'hoverData')
# )
def display_asuka_spell_data(spell_data):
    spells = {}
    spells[P1] = {}
    spells['p2'] = {}
    spells[P1]['spell'] = html.Div()
    spells['p2']['spell'] = html.Div()
    spells[P1]['percentile'] = html.Div()
    spells['p2']['percentile'] = html.Div()

    for trace in spell_data:
        player_data = trace["customdata"]
        player_side = player_data[ASUKA_HD_INDEX["player_side"]]
        spell_list = []
        for spell in player_data[ASUKA_HD_INDEX["spell_1"]:ASUKA_HD_INDEX["spell_4"]+1]:
            opactiy = 1.0 if spell != 'used_spell' else 0.0
            src = app.get_asset_url(f'images/spells/{spell}.png')
            style={"opacity": opactiy}
            spell_list.append(html.Img(src=src, style=style, className='spell'))
        spells[player_side]['spell'] = [html.Div(spell_list, className="spell_background")]
        spells[player_side]['percentile'] = [dbc.Label(f"{trace['y']}%", className='spell_label')]

    return spells

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)