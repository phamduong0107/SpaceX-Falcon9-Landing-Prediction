#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px

# === Tải dữ liệu ===
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv')

# === Khởi tạo ứng dụng Dash ===
app = dash.Dash(__name__)

# === Danh sách năm ===
year_list = [i for i in range(1980, 2024, 1)]

# === Bố cục giao diện ===
app.layout = html.Div([
    # Tiêu đề chính
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': '24px'}
    ),

    # Dropdown chọn loại báo cáo
    html.Div([
        html.Label("Select Report Type:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            value='Select Statistics',
            placeholder='Select a report type',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        )
    ]),

    # Dropdown chọn năm
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value='Select-year',
            placeholder='Select-year',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        )
    ]),

    # Khu vực hiển thị biểu đồ
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexWrap': 'wrap'})
    ])
])

# === Callback 1: Bật/tắt dropdown chọn năm ===
@callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False  # Bật chọn năm
    else:
        return True   # Tắt chọn năm

# === Callback 2: Vẽ biểu đồ theo lựa chọn ===
@callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    # ===== BÁO CÁO GIAI ĐOẠN SUY THOÁI =====
    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]

        # Biểu đồ 1: Doanh số trung bình theo năm trong suy thoái
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, x='Year', y='Automobile_Sales',
                           title="Average Automobile Sales Fluctuation Over Recession Period"))

        # Biểu đồ 2: Doanh số trung bình theo loại xe
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales',
                          title="Average Number of Vehicles Sold by Vehicle Type"))

        # Biểu đồ 3: Biểu đồ tròn chi phí quảng cáo theo loại xe
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type',
                          title="Total Advertising Expenditure Share by Vehicle Type During Recessions"))

        # Biểu đồ 4: Ảnh hưởng tỷ lệ thất nghiệp đến doanh số theo loại xe
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
                          labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                          title="Effect of Unemployment Rate on Vehicle Type and Sales"))

        # Trả về 4 biểu đồ: 2 trên, 2 dưới
        return [
            html.Div(className='chart-item', children=[R_chart1, R_chart2], style={'display': 'flex', 'width': '100%'}),
            html.Div(className='chart-item', children=[R_chart3, R_chart4], style={'display': 'flex', 'width': '100%'})
        ]

    # ===== BÁO CÁO THEO NĂM =====
    elif (input_year and selected_statistics == 'Yearly Statistics'):
        yearly_data = data[data['Year'] == input_year]

        # Biểu đồ 1: Doanh số trung bình toàn kỳ
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, x='Year', y='Automobile_Sales',
                           title="Yearly Automobile Sales (1980–2023)"))

        # Biểu đồ 2: Doanh số theo tháng trong năm được chọn
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(mas, x='Month', y='Automobile_Sales',
                           title=f"Total Monthly Automobile Sales in {input_year}"))

        # Biểu đồ 3: Doanh số trung bình theo loại xe trong năm được chọn
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
                         title=f"Average Vehicles Sold by Vehicle Type in {input_year}"))

        # Biểu đồ 4: Chi phí quảng cáo theo loại xe trong năm được chọn
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
                         title=f"Total Advertising Expenditure by Vehicle Type in {input_year}"))

        # Trả về 4 biểu đồ
        return [
            html.Div(className='chart-item', children=[Y_chart1, Y_chart2], style={'display': 'flex', 'width': '100%'}),
            html.Div(className='chart-item', children=[Y_chart3, Y_chart4], style={'display': 'flex', 'width': '100%'})
        ]

    else:
        return None

# === Chạy ứng dụng ===
if __name__ == '__main__':
    app.run(debug=True)
