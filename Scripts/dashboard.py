# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 08:35:46 2021

@author: cnpol
"""

import pandas as pd
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import numpy as np
import folium


# function loads and preprocesses df
def loadDF():
    """
    Function loads and preprocesses df. Does the formatting work

    Returns
    -------
    df : DataFrame
        datframe containing data in the required format.

    """
    
    # df with main housing data
    mainDF = pd.read_excel(r'C:\Users\cnpol\Documents\ISE 435\Project\Data\HousingInfo.xlsx',
                       index_col=0)
    # df with housing specifics (amenities, policies, etc.)
    specsDF = pd.read_excel(r'C:\Users\cnpol\Documents\ISE 435\Project\Data\HousingSpecifics.xlsx',
                        index_col=0)
    
    # combine dfs (on index) into one df
    df = mainDF.join(specsDF)
    
    df.dropna(inplace=True) # drop all rows with nan values

    # drop times from availability column, keep dates
    df.Availability = df.Availability.apply(lambda x: x.date())
    
    return df

df = loadDF() # create df full of data


# Function generates Folium map from df
def genMap(df):
    """
    Function Generates Folium Map from df data.

    Parameters
    ----------
    df : DataFrame
        dataframe with data to be plotted, have lat values in column 'Latitude' and longitude values in column 'Longitude'.

    Returns
    -------
    str
        path to html document containing generated map.

    """
    raleigh_loc = [35.7796, -78.6382] # starting location of map
    m = folium.Map(location=raleigh_loc) # create empty map of raleigh
    houses = folium.map.FeatureGroup() # create feature group for houses
      
    # str vars to form each houselink in house marker popup
    str1 = "<a href="
    str2=" target='_blank'>Click Here to see House Listing</a>"
    
    # mark each house on the map with a circle marker
    for lat, long, link in zip(df.Latitude, df.Longitude, df.Links):
        houses.add_child(
            folium.features.CircleMarker(
                [lat, long], 
                radius=5,            # radius of circle marker
                color='yellow',        # color of circle marker
                fill=True,            # want circle to be filled
                fill_color='blue',     # fill circle with this color
                fill_opacity=0.6,
                popup= str1 + link + str2,  # info to about listing to show when circle marker clicked on
                tooltip = 'Click me!'
            )
        )
    
    m.add_child(houses) # add house markers to map
    
    # locations of interest (not houses)
    work_loc = {'Carol Work':[35.65407465, -78.86340163251529],
                'Regan Work':[35.9938221,-78.9051647],
                'Glenwood':[35.787455, -78.647305], 
                'Ili House':[35.789299150000005, -78.67869863680241]
                }
    
    work = folium.map.FeatureGroup() # create feature group for work
    
    # add circle marker on workplace locations
    for loc in work_loc:
        work.add_child(
            folium.features.CircleMarker(
                work_loc[f'{loc}'],
                radius=7,                # make bigger to differentiate from house markers
                color='red',             # outline w/ diff color to differentiate from house markers
                fill=True, 
                fill_color='blue', 
                fill_opacity=0.6, 
                popup=f'{loc}',
                tooltip=f'{loc}'
                )
            )
    
    m.add_child(work) # add to map
    
    # save map to html file
    m.save(r'C:\Users\cnpol\Documents\ISE 435\Project\Data\Housing_map.html')
    
    # return location of created html file with map
    return r'C:\Users\cnpol\Documents\ISE 435\Project\Data\Housing_map.html'

app = dash.Dash() # initiate a dash object (application)

# define/construct the applicaiton layout
app.layout = html.Div([
    # add header (title)
    html.H1('Raleigh Housing', 
            style={'color':'blue', 'fontsize':40, 'border-style':'outset'}
            ),
    # add small paragraph explaining the purpose of the dashboard
    html.P('This dashboard presents houses currently for rent in Raleigh NC.',
           style={'fontsize':30}
           ),
    # new division
    html.Div([
        html.Div([
            html.Label('Rent Slider'), # rent slider label
            # add bin for slider output
            html.Div(
                id='slider-output', 
                style={'display':'inline-block'}
                ),
            # add slider to allow user to define acceptable rent range
            dcc.RangeSlider(
                id='rent-slider',
                min=df.Rent.min(),                  # min slider value
                max=df.Rent.max(),                  # max slider value
                step=50,                            # amount btwn selectable values on range
                marks={
                    int(i):f'{i}' for i in np.arange(df.Rent.min(), df.Rent.max(), 150)
                    },                              # add tickmarks with labels
                value=[df.Rent.min(), df.Rent.max()],   # starts with whole range selected
                )
            ]),
        html.Div([
            html.Label('Rent Per Person Slider'), # rent per person slider label
            # add bin for slider output
            html.Div(
                id='sliderPP-output', 
                style={'display':'inline-block'}
                ),
            # add slider to allow user to define acceptable rent per person range
            dcc.RangeSlider(
                id='rentPP-slider',
                min=df['Rent Per Person'].min(),    # min slider value
                max=df['Rent Per Person'].max(),    # max slider value
                step=50,                            # amount btwn selectable values on range
                marks={
                    int(i):f'{i}' for i in np.arange(df['Rent Per Person'].min(), df['Rent Per Person'].max(),150)
                    },                              # add tickmarks with labels
                value=[df['Rent Per Person'].min(), df['Rent Per Person'].max()]    # starts with whole range selected
                )
            ], style={'width':'100%'}
            )
        ]),
    html.Div([
        html.Div([
            html.Label('Num Bedroom Dropdown'),     # dropdown label
            # add dropdown to allow user to select the number of bedrooms
            dcc.Dropdown(
                id='bedrm-dropdown',
                options=[
                    {'label':i,'value':i} for i in set(df['No. Bedrooms'])
                    ],                          # define dropdown options
                value=None,                     # starts with no selections
                multi=True                      # allow multiple selections
                )
            ], style={'width':'25%', 'display':'inline-block'}
            ),
        html.Div([
            html.Label('Num Bathroom Dropdown'),    # dropdown label
            # add dropdown to allow user to select the number of bathrooms
            dcc.Dropdown(
                id='bathrm-dropdown',
                options=[
                    {'label':i,'value':i} for i in set(df['No. Bathrooms'])
                    ],                          # define dropdown options
                value=None,                     # start with no selections
                multi=True                      # allow multiple selections
                )
            ], style={'width':'25%', 'display':'inline-block'}
            )
        ]),
    html.Div([
        html.Div([
            html.H2('Housing Map'), # Header for the map
            # add folium map using Iframe
            html.Iframe(
                id='map',
                srcDoc=open(genMap(df),"r").read(),
                width='600',
                height='400'
                )
            ]),
        html.Div([
            html.H2('Available Houses'), # header for the data table
            # add datatable with housing data
            dash_table.DataTable(
                id='houseDF-datatable',
                columns=[
                    {'name':i, 'id':i} for i in ['Address', 'Area', 'Rent', 'No. Bedrooms', 'Square Footage',
                                                 'Rent Per Person', 'No. Bathrooms', 'Availability',
                                                 'Dist to Carol Work', 'Dist to Ili', 'Dist to Glenwood',
                                                 'Dist to Regan Work']
                    ],                          # define data table columns
                data=df.to_dict('records'),     # give table for data table
                editable=False,                 # do not allow the user to edit the datatable
                filter_action='native'          # allow the user to filter the data table
                )
            ])
        ])
    ], style={'border-style':'ridge', 'border-color':'blue'}
    )

# callback to update the numbers of the range selected for the rent slider
@app.callback(
    Output('slider-output','children'),
    Input('rent-slider','value')
    )
# callback function, updates the numbers
def updateRentSlider(value):
    """
    callback function to update the printed rent slider range

    Parameters
    ----------
    value : list
        range of the slider, 1st element is the min, 2nd element is the max.

    Returns
    -------
    str
        prints the range

    """
    return f': ${value}' # display the selected range

# callback to update the numbers of the range selected for the rent per person slider
@app.callback(
    Output('sliderPP-output','children'),
    Input('rentPP-slider','value')
    )
# callback function, updates the numbers
def updateRentPPSlider(value):
    """
    callback function to update the printed rent per person slider range

    Parameters
    ----------
    value : list
        range of the slider, 1st element is the min, 2nd element is the max.

    Returns
    -------
    str
        prints the range

    """
    return f': ${value}' # display the selected range

# callback to update the datatable when any of these criteria changed:
    # rent, rent per person, num bedrooms, num bathrooms
@app.callback(
    Output('houseDF-datatable','data'),
    [Input('rent-slider','value'),
     Input('rentPP-slider','value'),
     Input('bedrm-dropdown','value'),
     Input('bathrm-dropdown','value')]
    )
# callback function updates the rows shown on the datatable
def updateDF(rent, rentPP,  bdrm, bathrm):
    """
    callback function to update the datatable based on filtering criteria

    Parameters
    ----------
    rent : lsit
        range of the rent slider, 1st element is the min, 2nd element is the max.
    rentPP : list
        range of the rent per person slider, 1st element is the min, 2nd element is the max.
    bdrm : list
        desired number of bedrooms in a house, an empty list indicates all.
    bathrm : list
        desired number of bathrooms in a house, an empty list indicates all.

    Returns
    -------
    dictionary
        contains the data with houses meeting the filtering criteria.

    """
    df = loadDF() # load a new df with all the data
    
    # keep rows with rent inside of the slider range
    df = df[df.Rent <= rent[1]]     # max
    df = df[df.Rent >= rent[0]]     # min
    
    # keep rows with rent per person inside of the slider range
    df = df[df['Rent Per Person'] <= rentPP[1]]     # max
    df = df[df['Rent Per Person'] >= rentPP[0]]     # min
    
    # filter df by num of selected bedrooms, as long as the selection isn't empty
    # note: empty lists evaluate to false
    if bdrm:
        df = df[df['No. Bedrooms'].isin(bdrm)]
    # filter df by num of selected bathrooms, as long as the selection isn't empty
    if bathrm:
        df = df[df['No. Bathrooms'].isin(bathrm)]
    
    return df.to_dict('records') # update datatable with filtered df

# callback to update the map when any of these criteria changed:
    # rent, rent per person, num bedrooms, num bathrooms
@app.callback(
    Output('map','srcDoc'),
    [Input('rent-slider','value'),
     Input('rentPP-slider','value'),
     Input('bedrm-dropdown','value'),
     Input('bathrm-dropdown','value')]
    )
# callback function updates the markers shown on the map
def updateMap(rent, rentPP, bdrm, bathrm):
    """
    callback function to update the map based on filtering criteria

    Parameters
    ----------
    rent : lsit
        range of the rent slider, 1st element is the min, 2nd element is the max.
    rentPP : list
        range of the rent per person slider, 1st element is the min, 2nd element is the max.
    bdrm : list
        desired number of bedrooms in a house, an empty list indicates all.
    bathrm : list
        desired number of bathrooms in a house, an empty list indicates all.

    Returns
    -------
    folium.map
        folium map with houses meeting the filtering criteria.

    """

    df = loadDF() # load a new df with all the data
    
    # keep rows with rent inside of the slider range
    df = df[df.Rent <= rent[1]]     # max
    df = df[df.Rent >= rent[0]]     # min
    
    # keep rows with rent per person inside of the slider range
    df = df[df['Rent Per Person'] <= rentPP[1]]     # max
    df = df[df['Rent Per Person'] >= rentPP[0]]     # min

    # filter df by num of selected bedrooms, as long as the selection isn't empty
    if bdrm:
        df = df[df['No. Bedrooms'].isin(bdrm)]
    # filter df by num of selected bathrooms, as long as the selection isn't empty
    if bathrm:
        df = df[df['No. Bathrooms'].isin(bathrm)]
    
    return open(genMap(df),'r').read() # generate a new map with filtered df

# run the dash application
if __name__ =='__main__':
    app.run_server(port=8050, 
                   host='127.0.0.1')

