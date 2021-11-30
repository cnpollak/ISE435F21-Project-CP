# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 21:44:28 2021

@author: cnpol
"""

import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim

# read data from excel file
df = pd.read_excel(r'C:\Users\cnpol\Documents\ISE 435\Project\Data\HousingInfo.xlsx', 
                   index_col=0)

# Function finds longitude and latitude of address
def locate(address):
    """
    Function gets longitude and latitude for address.

    Parameters
    ----------
    address : str
        Address to be located.

    Returns
    -------
    float
        Latitude.
    float
        Longitude.

    """
    loc = address # specify address to be located
    geolocator = Nominatim(user_agent="my_request") # create Nominatim object
    location = geolocator.geocode(loc) # get location
    try:
        return location.latitude, location.longitude # return lat, long
    except:
        return None, None

# find lat and long for each house address
lats = []
longs = []
for addy in df['Address']:
    lat, long = locate(addy)
    lats.append(lat)
    longs.append(long)
df['Latitude'] = lats; df['Longitude'] = longs

# workplace loc
roviAddy = '480 Green Oaks Pkwy, Holly Springs, NC 27540' # address
roviLat, roviLong = locate(roviAddy) # lat and long

# best friend loc
bfAddy = '3101 Hillsborough St, Raleigh, NC 27607' # address
bfLat, bfLong = locate(bfAddy)

# bar loc
barAddy = '603 Glenwood Ave, Raleigh, NC 27603' # address
barLat, barLong = locate(barAddy)

# roomate's work loc
roomWorkAddy = '324 Blackwell St, Durham, NC 27701'
roomWorkLat, roomWorkLong = locate(roomWorkAddy)


# calc great cicle distance between 2 points
def gcd(pt1, pt2, circFactor=1.2):
    """
    Function calculates the great cicle distance between 2 points.
    GCD takes into account the earth's radius.

    Parameters
    ----------
    pt1 : list
        Latitude and longitude of 1st coordinate
    pt2 : list
        Latitude and longitude of 2nd coordinate.
    circFactor : float, optional
        Circular factor to be used in gcd formula. The default is 1.2.

    Returns
    -------
    gcd_ : float
        Great circle distance value.

    """
    # If one of the lats or longs is missing, return nan for distance
    if (np.nan in pt1) or (np.nan in pt2):
        return np.nan
        
    lat1 = pt1[0] * 2 * np.pi / 360 # Change lat from deg to rad                
    lat2 = pt2[0] * 2 * np.pi / 360
    deltaLat = (pt1[0] - pt2[0]) / 2 # Change lat from deg to rad
    deltaLong = (pt1[1] - pt2[1]) / 2 # Change long from deg to rad
    deltaLatRad = deltaLat * 2 * np.pi / 360 # Change lat from deg to rad
    deltaLongRad = deltaLong * 2 * np.pi / 360 # Change long from deg to rad
    
    r = 3958.8 # Earth Radius

    gcd_1 = np.sqrt((np.sin(deltaLatRad)**2) + np.cos(lat1) * np.cos(lat2) * (np.sin(deltaLongRad)**2))
    gcd_ = round(2 * r * np.arcsin(gcd_1), 2) * circFactor
    
    return round(gcd_, 2)

# calc distance between each house and the locations of interest
distanceRovi = []
distanceBF = []
distanceBar = []
distanceRoomWork = []
# iterate through each row in df
for row in range(len(df)):
    distanceRovi.append(gcd(df.loc[row, ['Latitude','Longitude']], (roviLat, roviLong))) # distance to work
    distanceBF.append(gcd(df.loc[row, ['Latitude','Longitude']], (bfLat, bfLong))) # distance to best friend
    distanceBar.append(gcd(df.loc[row, ['Latitude','Longitude']], (barLat, barLong))) # distance to downtown
    distanceRoomWork.append(gcd(df.loc[row, ['Latitude','Longitude']], (roomWorkLat, roomWorkLong))) # distance to roomate work
# add distances to df
df['Dist to Carol Work'] = distanceRovi
df['Dist to Ili'] = distanceBF
df['Dist to Glenwood'] = distanceBar
df['Dist to Regan Work'] = distanceRoomWork

# drop unnamed columns (old index columns)
cols = df.columns
for col in cols:
    if 'Unnamed' in col:
        df.drop(columns=[col], inplace=True)

# write new df into the houseing info excel file
df.to_excel(r'C:\Users\cnpol\Documents\ISE 435\Project\Data\HousingInfo.xlsx',
            sheet_name='General Info')










