
import pandas as pd


from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import datetime
import numpy as np
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go

# import plotly       #(version 4.4.1)
# import plotly.express as px

df = pd.read_csv("Data/NYPD_Complaint_Data_Current__Year_To_Date.csv")
# Extracting month from complaint date

#df['complaint_month'] = pd.to_datetime(df['CMPLNT_FR_DT'],errors = 'coerce')
#df['complaint_month'] = df['complaint_month'].dt.strftime('%m')
df['Suspect Race'] = df['SUSP_RACE']
df['Complaint Number'] = df['CMPLNT_NUM']
#cmpl_type_df = df.OFNS_DESC.value_counts().reset_index()
#cmpl_type_df = cmpl_type.head(6)
boro_list= ['MANHATTAN', 'BRONX', 'BROOKLYN', 'QUEENS', 'STATEN ISLAND']
value_list = [2925, 2917, 2133, 1843, 1815]


#-------------------------------------------------------------------------------------
# # Drop rows w/ no animals found or calls w/ varied age groups
# df = df[(df['# of Animals']>0) & (df['Age']!='Multiple')]

# # Extract month from time call made to Ranger
# df['Month of Initial Call'] = pd.to_datetime(df['Date and Time of initial call'])
# df['Month of Initial Call'] = df['Month of Initial Call'].dt.strftime('%m')

# # Copy columns to new columns with clearer names
# df['Amount of Animals'] = df['# of Animals']
# df['Time Spent on Site (hours)'] = df['Duration of Response']
#-------------------------------------------------------------------------------------

app = Dash(__name__)

#-------------------------------------------------------------------------------------
app.layout = html.Div([

        html.Div([
            html.Pre(children= "Complaint Classification",
            style={"text-align": "center", "font-size":"100%", "color":"black"})
        ]),

        html.Div([
            html.Label(['Choose a category:'],style={'font-weight': 'bold'}),
            dcc.RadioItems(
                id='xaxis_raditem',
                options=[
                         #{'label': 'Month Complaint Made', 'value': 'complaint_month'},
                         {'label': 'Suspect Race', 'value': 'boro_list'},
                ],
                value='boro_list',
                style={"width": "50%"}
            ),
        ]),

        html.Div([
            html.Br(),
            html.Label(['Y-axis values to compare:'], style={'font-weight': 'bold'}),
            dcc.RadioItems(
                id='yaxis_raditem',
                options=[
                         {'label': 'Number of complaints', 'value': 'value_list'},
                         #{'label': 'Amount of Animals', 'value': 'Amount of Animals'},
                ],
                value='value_list',
                style={"width": "50%"}
            ),
        ]),

    html.Div([
        dcc.Graph(id='the_graph')
    ]),

])

#-------------------------------------------------------------------------------------
@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input(component_id='xaxis_raditem', component_property='value'),
     Input(component_id='yaxis_raditem', component_property='value')]
)
# Arguments in this function refer to the values of input from callback
def update_graph(x_axis, y_axis):

    #dff = df
    # print(dff[[x_axis,y_axis]][:1])

    barchart=px.bar(
            #data_frame=dff,
            x=x_axis,
            y=y_axis,
            title=y_axis+': by '+x_axis,
            # facet_col='BORO_NM',
            # color='BORO_NM',
            # barmode='group',
            )

    barchart.update_layout(xaxis={'categoryorder':'total ascending'},
                           title={'xanchor':'center', 'yanchor': 'top', 'y':0.9,'x':0.5,})

    return (barchart)

if __name__ == '__main__':
    app.run_server(debug=True, port = 4000)