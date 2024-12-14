import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Read the SpaceX dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Define the maximum and minimum payload values
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create the Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    html.Br(),

    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),

    # Pie chart for total successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # Slider for Payload Range
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(i): f'{int(i)} kg' for i in range(int(min_payload), int(max_payload) + 1, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # Scatter chart for Payload vs. Success correlation
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(site_dropdown):
    if site_dropdown == 'ALL':
        # Pie chart for all sites
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches by Site'
        )
    else:
        # Filtered pie chart for a specific site
        filtered_df = spacex_df[spacex_df['Launch Site'] == site_dropdown]
        success_count = filtered_df['class'].value_counts()
        fig = px.pie(
            values=success_count,
            names=success_count.index,
            title=f"Success vs Failed Launches for Site {site_dropdown}"
        )
    return fig

# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(site_dropdown, payload_slider):
    low, high = payload_slider
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if site_dropdown == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == site_dropdown]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f"Payload vs. Outcome for Site {site_dropdown}"
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)