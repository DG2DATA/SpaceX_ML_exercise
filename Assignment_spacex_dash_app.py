# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                
                                 dcc.Dropdown(id='site-dropdown',
                                 options=[
                                     {'label': 'All Sites', 'value': 'ALL'},
                                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
				                 	 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
				                 	 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
				                 	 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                 ],
                                 value='ALL',
                                 placeholder="Please enter the name of a site from the list",
                                 searchable=True
                                 ),
                                
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                
                                dcc.RangeSlider(id='payload-slider',
                                min=0, max=10000, step=1000,
                                marks={0: '0',
                                       100: '100'},
                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
       filtered_df['class_one'] = filtered_df['class'].mask(filtered_df['class'].ne(1))
       all_sites_df = filtered_df.groupby('Launch Site')['class_one'].count().to_frame(name="values").reset_index()
       fig = px.pie(all_sites_df, values='values', names='Launch Site', title='Total Success Launches By Site')
       return fig
    else:
       tgt_site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
       tgt_site_grouped_df = tgt_site_df.groupby("class")["class"].count().to_frame(name="values").reset_index()
       fig = px.pie(tgt_site_grouped_df, values='values', names='class', title='Total Success Launches for site '+entered_site, color="class",color_discrete_map={0:'red',1:'darkgreen'})
       return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

# https://stackoverflow.com/questions/74747238/using-multiple-sliders-with-plotly-dashboard-scatter-plot-3d

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def success_payload_scatter_chart(entered_site,entered_payload):
	df = spacex_df
	#
	low_x, high_x = entered_payload
	#
	mask_all = (df['Payload Mass (kg)'] > low_x) & (df['Payload Mass (kg)'] < high_x) 
	if entered_site == 'ALL':
		fig = px.scatter(df[mask_all], x='Payload Mass (kg)', y='class', color="Booster Version Category", title='Correlation between Payload and Success for all Sites')
		return fig
	else:
		mask_tgt_site = (df['Payload Mass (kg)'] > low_x) & (df['Payload Mass (kg)'] < high_x) & (df['Launch Site'] == entered_site)
		fig = px.scatter(df[mask_tgt_site], x='Payload Mass (kg)', y='class', color="Booster Version Category", title='Correlation between Payload and Success for site '+entered_site)
		return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
