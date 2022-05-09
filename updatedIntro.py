
import pandas as pd
import seaborn as sns
import plotly 
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import datetime
import numpy as np
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import plotly.io as pio
import json
from urllib.request import urlopen

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])


with urlopen('https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/new-york-city-boroughs.geojson') as response:
    ny_boroughs = json.load(response)


df = pd.read_csv("Data/NYPD_Complaint_Data_Cleaned.csv")
df_rate = pd.read_csv("data/Complaint_Rate_Population_Borough.csv")
# You can change this to "Data/NYPD_Complaint_Data_Cleaned.csv" or the csv needed for the dashboard
# some data Filtering and cleaning 
sex_list = ['M', 'F']
condition = df.susp_sex.isin(sex_list)
df = df[condition]
df = df[df['boro_nm'].notna()]
df['boro_nm'] = df['boro_nm'].str.title()

# Rename columns with clearer names
df = df.rename(columns={'complaint_month': 'Month'})
df = df.rename(columns={'cmplnt_num': 'Complaint Count'})


# Group by month, gender, borough and count the complaint id
df_gb= df.groupby(['Month','susp_sex','boro_nm'],as_index=False)['Complaint Count'].count()

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Jorge Granda ", href="#")),
        dbc.NavItem(dbc.NavLink("David Guzman", href="https://davidguzman1999.github.io/davidguzman.github.io/")),
    ],
    brand= "Dashboard Repo",
    brand_href="https://github.com/DavidGuzman1999/CTPDataScienceProject",
    color="primary",
    dark=True,
)


#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
app.layout = html.Div([
        navbar,
        html.Div([
            html.H1(children= "NYPD Complaint Data Dashboard",
            style={"text-align": "center", "font-size":"300%", "color":"black"})
        ]),
          html.Br(),


# --------------------------------------------------------------------------------

    # the map graph
        dcc.Graph(id='nyc_map'),
        html.Div(id='nyc_map_value'),

    # ----------------------------------------------------------------------------------
    # second chart
        dcc.Dropdown(
        id="br_selected",
        options=[{"label": x, "value": x} 
                 for x in df.boro_nm.unique()],
        value='Manhattan',
        style={'width': "40%"},
        clearable=False,
    ),
    # dcc.Graph
        dcc.Graph(id="boro-complaint-chart"),

    #----------------------------------------------------------------------------------
    ## bar plots dropdown
        dcc.Dropdown(
            id="boro_selected",
            options=[{"label": x, "value": x} 
                    for x in df_gb.boro_nm.unique()],
            value='Manhattan',
            style={'width': "40%"},
            clearable=False,
    ),
    # Div where the complaint by month graphs will go.
        html.Div( 
            children=[
                dcc.Graph(
                    id="boro-bar-plot", 
                    style={'display': 'inline-block'}),

            # The state month chart will go in here
                dcc.Graph(
                    id="state-bar-plot", 
                    style={'display': 'inline-block'})
            ]
    ),
    
    # Div where the output of the the selected borough will go
        html.Div(id='output_container', children=[])

])
# @end of app.layout

#------------------------------------------------------------------
# first map call back and func definition

@app.callback(
    Output("nyc_map", "figure"),
    [Input('nyc_map_value', 'children')])

def borough_map(nyc_map_value):
    
    dff = df.copy()

    # id needed to map the json file to dataframe
    boro_id_map = {}
    for feature in ny_boroughs["features"]:
         feature["id"] = feature["properties"]["cartodb_id"]
         boro_id_map[feature["properties"]["name"]] = feature["id"]
    
    
    dff["id"] = dff["boro_nm"].apply(lambda x: boro_id_map[x])
    fig = px.choropleth_mapbox(
    dff,
    locations="id",
    geojson=ny_boroughs,
    color="boro_nm",
    hover_name="boro_nm",
    #hover_data=["Density"],
    title="NYC Complaint Data statistics",
    mapbox_style="open-street-map",
    center={"lat": 40.730610, "lon": -73.9749},
    zoom=9.5,
    opacity=0.5,)

    return fig

#-------------------------------------------------------------------------------------
# Second Graph callback
@app.callback(
    Output(component_id='boro-complaint-chart', component_property='figure'),
    [Input(component_id='br_selected', component_property='value')]
)

def boro_cmpl_type(br_selected):

    dff = df.copy()
    #dff['boro_nm'] = dff['boro_nm'].str.title()
    
    dff = dff[dff['boro_nm']== br_selected]

    boro_cmpl_count = dff.ofns_desc.value_counts().reset_index().head()

    fig = px.bar(
        boro_cmpl_count, 
        x='index', 
        y='ofns_desc',
        color="index",
        opacity=0.9,                  # set opacity of markers (from 0 to 1)
        orientation="v",              # 'v','h': orientation of the marks
        #barmode='group',
        template='gridon',
        labels={"index":"Ofense Description"}, 
        title=("Complaints with the hightest count in %s" % br_selected)
    )
    #fig.update_layout(xaxis={'categoryorder':'total descending'})#,
                           #title={'xanchor':'center', 'yanchor': 'top', 'y':0.9,'x':0.5,})
    return fig 


# ----------------------------------------------------------------
# Time charts  call back and func definition below
 
@app.callback(
    [Output(component_id="boro-bar-plot", component_property="figure"),
    Output(component_id="state-bar-plot", component_property="figure"),
    Output(component_id='output_container', component_property='children')], 
    [Input("boro_selected", "value")])

def display_time_series(boro_selected):
    dff = df_gb
    
    # Use the input from the user to render some text and return it
    display_text = "Borough Selected: %s" % boro_selected

    dff_rate = df_rate
    #['Borough', 'Complaint Count', 'Population', 'rate_100k'
    # Make a bar plot of entire state
    state_figure = px.bar(
        dff_rate, 
        x='Borough', 
        y='rate_100k',
        color="Borough",
        opacity=0.9,                  # set opacity of markers (from 0 to 1)
        orientation="v",              # 'v','h': orientation of the marks
        #barmode='group',
        template='gridon',
        labels={"rate_100k":"Complaint Count",
        "Borough":"Region"},
        title="Number of Complaints Per 100k")
    state_figure.update_layout(xaxis={'categoryorder':'total descending'},
                            title={'xanchor':'center', 'yanchor': 'top', 'y':0.9,'x':0.5,})

    # use user input for borough value
    boro_df = dff[dff['boro_nm'] == boro_selected]
    # Make a bar chart of just the selected borough.
    boro_figure = px.bar(
        boro_df, 
        x='Month', 
        y='Complaint Count',
        color="susp_sex",
        opacity=0.9,                  # set opacity of markers (from 0 to 1)
        orientation="v",              # 'v','h': orientation of the marks
        barmode='group',
        template='gridon',
        labels={"susp_sex":"Gender"}, 
        title=("Complaint by Month in %s" % boro_selected))

    return boro_figure, state_figure, display_text

#---------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True, port = 4000)