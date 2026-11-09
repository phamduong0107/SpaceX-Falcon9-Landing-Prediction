# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Get unique launch sites
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                  [{'label': site, 'value': site} for site in launch_sites]

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Thêm Dropdown chọn địa điểm phóng
    html.Div([
        html.Label('Select Launch Site:'),
        dcc.Dropdown(
            id='site-dropdown',
            options=dropdown_options,
            value='ALL',
            placeholder='Select a Launch Site here',
            searchable=True
        )
    ]),
    html.Br(),

    # TASK 2: Biểu đồ Tròn Tỷ Lệ Thành Công
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Thanh Trượt Chọn Khối Lượng
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Biểu đồ Phân Tán Khối Lượng & Kết Quả
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback cho Biểu đồ Tròn
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Tất cả địa điểm — tổng hợp thành công theo địa điểm
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Success Launches by Site'
        )
    else:
        # Lọc theo địa điểm được chọn
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Total Success vs Failed Launches for site {entered_site}',
            color_discrete_map={0: 'red', 1: 'green'},
            labels={0: 'Failed', 1: 'Success'}
        )
    return fig

# TASK 4: Callback cho Biểu đồ Phân Tán
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Lọc theo khoảng khối lượng
    mask = (spacex_df['Payload Mass (kg)'] >= low) & \
           (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'ALL':
        # Tất cả địa điểm
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites',
            labels={'class': 'Launch Outcome (1=Success)'}
        )
    else:
        # Lọc thêm theo địa điểm
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs Success for {entered_site}',
            labels={'class': 'Launch Outcome (1=Success)'}
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
