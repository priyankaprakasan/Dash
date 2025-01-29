import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

df = pd.read_csv('carbon.csv', header=0)

app = dash.Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap'
])

app.title = "European Carbon Dashboard"

# Define color scheme
colors = {
    'background': '#F0F2F6',
    'text': '#2c3e50',
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'accent': '#e74c3c'
}

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("European Carbon Dashboard", 
                style={'color': colors['text'], 'textAlign': 'center', 'fontWeight': '700', 'fontSize': '2.5rem', 'marginBottom': '0.5rem'}),
        html.P("Interactive visualization of carbon intensity and renewable energy data across Europe.", 
               style={'color': colors['text'], 'textAlign': 'center', 'fontWeight': '300', 'fontSize': '1.1rem', 'marginBottom': '1.5rem'}),
    ], style={'backgroundColor': 'white', 'padding': '2rem', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)', 'marginBottom': '2rem'}),
    
    # Main content
    html.Div([
        # Choropleth map
        html.Div([
            dcc.Graph(id='choropleth-map', config={'displayModeBar': False, 'scrollZoom': False},
                      style={'height': '60vh'})
        ], style={'width': '100%', 'marginBottom': '2rem'}),
        
        # Donut charts
        html.Div([
            html.Div([
                dcc.Graph(id='low-carbon-donut', config={'displayModeBar': False, 'scrollZoom': False},
                          style={'height': '40vh'})
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(id='renewable-donut', config={'displayModeBar': False, 'scrollZoom': False},
                          style={'height': '40vh'})
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
        ]),
    ], style={'backgroundColor': 'white', 'padding': '2rem', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
    dcc.Store(id='initial-selection', data='Belgium'),
    dcc.Store(id='hover-data')
], style={'backgroundColor': colors['background'], 'fontFamily': 'Roboto, sans-serif', 'padding': '2rem'})

@app.callback(
    Output('choropleth-map', 'figure'),
    Output('hover-data', 'data'),
    Input('choropleth-map', 'hoverData'),
    Input('initial-selection', 'data')
)
def update_map(hover_data, initial_selection):
    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color="carbon-intensity",
        hover_data=["country", "low-carbon", "renewable", "carbon-intensity"],
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Carbon Intensity Across Europe",
    )

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="mercator",
            lonaxis=dict(range=[-10, 25]),
            lataxis=dict(range=[35, 60]),
            center=dict(lon=5, lat=50),
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Roboto"
        ),
        title=dict(
            font=dict(size=22, family="Roboto", color=colors['text']),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=50, b=0),
        hovermode='closest'
    )

    if hover_data is None:
        hover_data = {'points': [{'location': initial_selection}]}

    return fig, hover_data
@app.callback(
    [Output('low-carbon-donut', 'figure'),
     Output('renewable-donut', 'figure')],
    Input('hover-data', 'data'),
    Input('initial-selection', 'data')
)
def update_donut_charts(hover_data, initial_selection):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'initial-selection' or not hover_data:
        country = initial_selection
    elif hover_data and 'points' in hover_data:
        country = hover_data['points'][0]['location']
    else:
        return go.Figure(), go.Figure()

    country_data = df[df['country'] == country].iloc[0]
    
    low_carbon_fig = go.Figure(data=[go.Pie(
        values=[country_data['low-carbon'], 100 - country_data['low-carbon']],
        hole=0.7,
        textinfo='none',
        marker_colors=[colors['primary'], '#e0e0e0'],
        showlegend=False
    )])
    low_carbon_fig.update_layout(
        annotations=[dict(text=f'{country_data["low-carbon"]:.1f}%', x=0.5, y=0.5, font_size=24, showarrow=False, font_family="Roboto", font_color=colors['primary'])],
        showlegend=False,
        title=dict(text=f"Low Carbon Energy in {country}", font=dict(size=18, family="Roboto", color=colors['text']), x=0.5, xanchor='center'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=0, l=0, r=0)
    )
    
    renewable_fig = go.Figure(data=[go.Pie(
        values=[country_data['renewable'], 100 - country_data['renewable']],
        hole=0.7,
        textinfo='none',
        marker_colors=[colors['secondary'], '#e0e0e0'],
        showlegend=False
    )])
    renewable_fig.update_layout(
        annotations=[dict(text=f'{country_data["renewable"]:.1f}%', x=0.5, y=0.5, font_size=24, showarrow=False, font_family="Roboto", font_color=colors['secondary'])],
        showlegend=False,
        title=dict(text=f"Renewable Energy in {country}", font=dict(size=18, family="Roboto", color=colors['text']), x=0.5, xanchor='center'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=0, l=0, r=0)
    )
    
    return low_carbon_fig, renewable_fig

if __name__ == '__main__':
    app.run_server('0.0.0.0',port=8050)

