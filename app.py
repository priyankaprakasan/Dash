
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

df=pd.read_csv('carbon.csv',header=0)



# Data for the choropleth
# df = pd.DataFrame({
#     "country": ["Belgium", "Netherlands", "France"],
#     "carbon-intensity": [120, 150, 90],
#     "low-carbon": [45.0, 50.0, 70.0],
#     "renewable": [30.0, 35.0, 50.0],
# })

app = dash.Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap'
])

app.title = "European Carbon Dashboard"

# Define color scheme
colors = {
    'background': '#8B94A3',
    'text': '#2c3e50',
    'primary': '#06BA63',
    'secondary': '#E8CE4D',
    'accent': '#E8CE4D'
}

app.layout = html.Div([
    html.Div([
        html.H1("European Carbon Intensity Dashboard", 
                style={'color': colors['text'], 'textAlign': 'center', 'fontWeight': '700', 'fontSize': '2.5rem', 'marginBottom': '0.5rem'}),
        html.P("Interactive visualization of carbon intensity, low-carbon, and renewable energy data across Europe.", 
               style={'color': colors['text'], 'textAlign': 'center', 'fontWeight': '300', 'fontSize': '1.1rem', 'marginBottom': '1.5rem'}),
    ], style={'backgroundColor': 'white', 'padding': '2rem', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)', 'margin': '2rem 0'}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='choropleth-map', config={'displayModeBar': False},
                      style={'height': '60vh', 'width': '100%'})
        ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.Div([
                dcc.Graph(id='low-carbon-donut', style={'height': '28vh'}),
            ], style={'marginBottom': '2rem'}),
            
            html.Div([
                dcc.Graph(id='renewable-donut', style={'height': '28vh'}),
            ]),
        ], style={'width': '38%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '2%'}),
    ], style={'backgroundColor': 'white', 'padding': '1.5rem', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
    
    dcc.Interval(id='interval-component', interval=50, n_intervals=0),
    dcc.Store(id='hover-store', data={'country': None, 'n_intervals': 0})
], style={'backgroundColor': colors['background'], 'fontFamily': 'Roboto, sans-serif', 'padding': '2rem', 'maxWidth': '1400px', 'margin': '0 auto'})

@app.callback(
    Output('choropleth-map', 'figure'),
    Input('choropleth-map', 'hoverData')
)
def update_map(hover_data):
    fig = px.choropleth(
        df,
        locations="country",
        locationmode="country names",
        color="carbon-intensity",
        hover_data=["country", "low-carbon", "renewable", "carbon-intensity"],
        color_continuous_scale=[
            [0, 'darkgreen'], 
            [1, 'lightgreen']
        ],
        title="Low Carbon Energy Percentage by Country",
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
        margin=dict(l=0, r=0, t=50, b=0)
    ) 
    fig.update_coloraxes(showscale=False)

    return fig

@app.callback(
    Output('hover-store', 'data'),
    Input('choropleth-map', 'hoverData'),
    Input('interval-component', 'n_intervals'),
    State('hover-store', 'data')
)
def update_hover_store(hover_data, n_intervals, store_data):
    if hover_data:
        country = hover_data['points'][0]['location']
        if country != store_data['country']:
            return {'country': country, 'n_intervals': 0}
        else:
            return {'country': country, 'n_intervals': store_data['n_intervals'] + 1}
    return {'country': None, 'n_intervals': 0}

@app.callback(
    [Output('low-carbon-donut', 'figure'),
     Output('renewable-donut', 'figure')],
    Input('hover-store', 'data')
)
def update_donut_charts(hover_store):
    country = hover_store['country']
    print(country)
    if country==None:
        country='Belgium'
        n_intervals=20
    else:
        n_intervals = hover_store['n_intervals']
    
  
    if country:
        print("Intervals",n_intervals)
        country_data = df[df['country'] == country].iloc[0]
        print(country_data)
        max_intervals = 20
        progress = min(n_intervals / max_intervals, 1)
        
        carbon_progress = country_data['low-carbon'] * progress
        renew_progress = country_data['renewable'] * progress
        
        low_carbon_fig = go.Figure(data=[go.Pie(
            values=[carbon_progress, 100 - carbon_progress],
            hole=0.7,
            textinfo='none',
            marker_colors=[colors['primary'], '#e0e0e0'],
            showlegend=False
        )])
        low_carbon_fig.update_layout(
            annotations=[dict(text=f'{carbon_progress:.1f}%', x=0.5, y=0.5, font_size=24, showarrow=False, font_family="Roboto", font_color=colors['primary'])],
            showlegend=False,
            title=dict(text=f"Low Carbon Energy in {country}", font=dict(size=18, family="Roboto", color=colors['text']), x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=0, l=0, r=0)
        )
        
        renewable_fig = go.Figure(data=[go.Pie(
            values=[renew_progress, 100 - renew_progress],
            hole=0.7,
            textinfo='none',
            marker_colors=[colors['secondary'], '#e0e0e0'],
            showlegend=False
        )])
        renewable_fig.update_layout(
            annotations=[dict(text=f'{renew_progress:.1f}%', x=0.5, y=0.5, font_size=24, showarrow=False, font_family="Roboto", font_color=colors['secondary'])],
            showlegend=False,
            title=dict(text=f"Renewable Energy in {country}", font=dict(size=18, family="Roboto", color=colors['text']), x=0.5, xanchor='center'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=0, l=0, r=0)
        )
        
        return low_carbon_fig, renewable_fig

    return go.Figure(), go.Figure()

if __name__ == '__main__':
    app.run_server('0.0.0.0',port=8050)
