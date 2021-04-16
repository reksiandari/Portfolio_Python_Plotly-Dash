
# IMPORT LIBRARY 

import dash # aplikasi
import dash_core_components as dcc # komponen komponen dashboard yang sering digunakan 
import dash_html_components as html # kerangka layout
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# DATA WRANGLING PART


house = pd.read_csv('data_input/household.csv', sep=",", index_col=0)
## Merubah dtypes
house['purchase_time'] = house['purchase_time'].astype('datetime64')
house[['category', 'sub-category']] = house[['category', 'sub_category']].astype('category')
## create new columns
house["salesvolume"] = house["unit_price"] * house["quantity"]
house['purchase_date'] = house['purchase_time'].dt.date
house['purchase_date'] = house['purchase_date'].astype('Datetime64')


# sampai disini data wrangling 

app.title = "Household Expenses Dashboard"

app.layout = html.Div(
    children=[
        html.Div(
            className="header",
            children=[
                #ini untuk isi header.
                html.H1( # header 1
                    children = "Household Expenses Dashboard", className = "header-title"),
                html.P (# paragraph
                    children = "Analysis on the household spending on grocery items"
                    " and the price of those items" 
                    " between Nov 2017 and Sept 2018"
                    " "
                    " ",
                    className = "header-description"),
            ]
        ),
        html.Div(
            className="wrapper",
            children=[
                # ini untuk isi body 
                html.Div( # ini untuk filter
                    className='menu',
                    children=[
                        html.Div( ## filter seller
                            className = 'dropdown',
                            children = [ 
                                html.Div(children="Seller", className="menu-title"),
                                dcc.Dropdown(id="seller-filter",
                                            options=[
                                                {"label": Seller, "value": Seller}
                                                for Seller in np.sort(house.format.unique())],
                                            value="format",
                                            clearable=True, # clearable allows the user to leave this field empty if set to True
                                            className="dropdown")]
                         ),
                        html.Div( ## filter category
                                    children=[
                                        html.Div(children="Category", className="menu-title"),
                                        dcc.Dropdown(
                                            id="category-filter",
                                            options=[
                                                {"label": item_category, "value": item_category}
                                                for item_category in house.category.unique()],
                                            value="category",
                                            clearable=True,
                                            searchable=False,
                                            className="dropdown")]
                            ),
                         html.Div( ## filter date range
                                    children=[
                                        html.Div(
                                            children="Date Range",
                                            className="menu-title"
                                            ),
                                        dcc.DatePickerRange(
                                            id="date-range",
                                            min_date_allowed=house.purchase_date.min().date(),
                                            max_date_allowed=house.purchase_date.max().date(),
                                            start_date=house.purchase_date.min().date(),
                                            end_date=house.purchase_date.max().date())]
                            )
                    ]
         ),
                html.Div(
                    className="card",
                    children=[
                        dcc.Graph(id= 'transaction-chart')]
                ),
                html.Div(
                    className="card",
                    children=[
                        dcc.Graph(id= 'discount-chart')]
                ),
            ]
        ),   
    ]
)

@app.callback(
    [Output("transaction-chart", "figure"), 
     Output("discount-chart", "figure")],
    [Input(component_id = "seller-filter", component_property = "value"), # these 4 inputs goes on to `def` below
     Input(component_id = "category-filter", component_property = "value"),
     Input(component_id = "date-range", component_property = "start_date"),
     Input(component_id = "date-range", component_property = "end_date")],
)

def update_charts(Seller, item_category, start_date, end_date): # for 4 inputs
    data_filter = (
        (house.format == Seller)
        & (house.category == item_category)
        & (house.purchase_date >= start_date)
        & (house.purchase_date <= end_date)
    )
    filtered_data = house.loc[data_filter, :] # data prep for grouping
    house_groupdate = filtered_data.groupby('purchase_date').mean().reset_index() # data grouping for graph
    # house_groupform = filtered_data.groupby("format").sum().reset_index()
    
    transaction_chart_figure = px.line(house_groupdate, # chart 1
             x = "purchase_date",
             y = "salesvolume",
             title = "Average Household Expense Daily Transaction",
             labels = {'purchase_date' : 'Date',
                        'sales_volume' : 'Sales Volume'})

    discount_chart_figure = px.bar(filtered_data, # chart 2
                           y = "format", 
                           x = "discount",
                           color = "salesvolume",
                           title = "Seller with the Biggest Discount",
                           labels = {'format' : 'Seller Type',
                                     'discount' : 'Total Discount Given'})
    
    return transaction_chart_figure, discount_chart_figure



if __name__ == "__main__":
    app.run_server(debug=True)