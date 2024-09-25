import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df['Launch Site'].unique()

app = dash.Dash(__name__)

app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(
                                                id='site-dropdown',
                                                options=[{'label': 'All', 'value': 'All'}] + [{'label': site, 'value': site} for site in launch_sites],
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                    	                        searchable=True
                                            ),
                                html.Br(),

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                
                                dcc.RangeSlider(
                                                    id='payload-slider',
                                                    min=0, max=10000, step=500,
                                                    marks={i: f'{i}' for i in range(0, 10001, 2500)},  # Exibe as marcas de 2500 em 2500
                                                    value=[np.min(spacex_df['Payload Mass (kg)']), np.max(spacex_df['Payload Mass (kg)'])],  # Valor inicial similar ao da imagem
                                                    tooltip={"placement": "bottom", "always_visible": True},  # Tooltip sempre visível
                                                    updatemode='drag',  # Atualiza em tempo real ao arrastar
                                                ),
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def update_pie_chart(selected_site):
    if selected_site == 'All':
        all_sites_success_count = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='count')

        fig = px.pie(all_sites_success_count, values='count', names='Launch Site',
                    title='Total Success Launches By Site',
                    labels={'Launch Site': 'Launch Site'})
    
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        site_success_count = filtered_df['class'].value_counts().reset_index()
        site_success_count.columns = ['class', 'count']  # Rename columns

        fig = px.pie(site_success_count, values='count', names='class', 
                     title=f'Success and Failure Launches for site {selected_site}',
                     labels={'class': 'Launch Outcome'})

    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='payload-slider', component_property='value')
)
def update_scatter_chart(payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category', 
                     title='Correlation between Payload and Success for all Sites',
                     labels={'class': 'Launch Outcome'})
    
    return fig

if __name__ == '__main__':
    app.run_server(port=8051)