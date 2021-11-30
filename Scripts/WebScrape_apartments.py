# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# import required libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime as dt
from datetime import date
import numpy as np

# function that creates a Chrome webdriver driver insance
def getDriver():
    """
    Function creates a Chrome webdriver instance.

    Returns
    -------
    driver : webdriver.chrome.webdriver.WebDriver
        Google chrome webdriver object.

    """
    # randomize user agent to get past Captcha
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    #print(userAgent)
    options.add_argument(f'user-agent={userAgent}')
        
    # open chrome
    driver = webdriver.Chrome(options=options, executable_path=r"C:\Users\cnpol\Downloads\chromedriver_win32\chromedriver.exe")
    
    return driver
    
    
# function gets content of specified webpage
def webpage_content(link, driver):
    """
    Function gets content of specified webpage.

    Parameters
    ----------
    link : str
        Webpage link.
    driver : webdriver.chrome.webdriver.WebDriver
        Google chrome webdriver object.

    Returns
    -------
    soup : bs4.BeautifulSoup
        BeautifulSoup object containing webpage content.
    content : str
        Str variable of webpage content.

    """
        
    driver.get(link) # go to website

    # get content from web page, store content in variable
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    
    return soup, content

# get content from apartments.com of raleigh house rentals (page 1 only)
driver = getDriver() # create driver instance
soup, content = webpage_content("https://www.apartments.com/houses/raleigh-nc/", driver)


# function finds all links within specified webpage tag
def find_links(soup, tag, attr, label, one_link=False):
    """
    Function finds links within a specific tag.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        BeautifulSoup object containing webpage content.
    tag : str
        Tag name to be searched for, ex: h1, div, li, etc.
    attr : str
        Attribute name of tag, ex: class, id, etc.
    label : str
        Attribute value.
    one_link : bool, optional
        If you only want one link per instance of specified tag found. The default is False.

    Returns
    -------
    links : list
        Contains all links found.

    """
    # find all instances of tag
    result = [str(a) for a in soup.findAll(tag, attrs={attr:label})]
    elems = [elem.split('"') for elem in result] # split each instance into sublists by element
    
    # initiate empty variable/list
    links = []
    # loop through each item (list) in list
    for lst in elems:
        # loop through each item within each inner listF
        for val in lst:
            # add the value to the links list if it contains https
            if 'https' in val:
                links.append(val)
                # if specified only one link per inner list
                if one_link == True:
                    break # once it finds a link, stop, move onto next inner list
    
    return links


# get links of house listings on current webpage (page 1)
houseLinks = []
houseLinks = find_links(soup, 'li','class','mortar-wrapper', True)

# get number of pages of house listings
num = soup.find('span', attrs={'class':'pageRange'})
numPages = int(num.text.split(' ')[-1])

# get links of house listings on rest of webpages
i = 2
# go to each page, grab links for each house listing
while i <= numPages:
    soup, content = webpage_content(f'https://www.apartments.com/houses/raleigh-nc/{i}/', driver) # webpage content
    houseLinksTemp = find_links(soup, 'li','class','mortar-wrapper', True) # get house listing links
    [houseLinks.append(a) for a in houseLinksTemp] # add house listing links to list
    i += 1 # go to next page


# function removes extra spacing in list values, makes formatting consistent
def removeSpace(list_):
    """
    Function removes unnecessary spacing from strings in list, makes formatting more consistent.

    Parameters
    ----------
    list_ : list
        List with strings that contain too much spacing.

    Returns
    -------
    temp : list
        List with spaces only between words.

    """
    newElem = []
    for elem in list_:
        newElem.append(' '.join(char for char in elem.split()))
    return newElem


# initiate empty strings for loop
address=[]
rentInfo = []
availability = []
amenities = []
specifics = []
policyTitle = []
policies = []

# set up loop stops to refresh chrome browser with new driver instance
numLinks = len(houseLinks) # get tot num of house listing links
stop1 = numLinks / 3
stop2 = 2 * numLinks / 3

# collect info for each house listing
for link in houseLinks:
    
    # stop and refresh chrome driver if at one of the stops
    if houseLinks.index(link) == stop1 or houseLinks.index(link) == stop2:
        driver.quit() # close old driver
        driver = getDriver() # initiate new chrome webdriver driver
    
    soup, content = webpage_content(link, driver) # webpage content
    
    # address
    addr = soup.find('div', attrs={'class':'propertyAddressContainer'})
    address.append(addr.text)
    
    # main info of rental
    rentInfo_i = [elem.text for elem in soup.findAll('p', attrs={'class':'rentInfoDetail'})]
    try:
        rentInfo.append(rentInfo_i)
    except:
        rentInfo.append(None)
    
    # lease start
    availability_i = soup.find('span', attrs={'class':'availabilityInfo'})
    try:
        availability.append(availability_i.text)
    except:
        availability.append('blank')
    
    
    # amenities
    amenity_i = [elem.text for elem in soup.findAll('div', attrs={'class':'amenityCard'})]
    try:
        amenities.append(removeSpace(amenity_i))
    except:
        amenities.append(None)
    
    # specifics
    specific_i = [elem.text for elem in soup.findAll('li', attrs={'class':'specInfo'})]
    try:
        specifics.append(removeSpace(specific_i))
    except:
         specifics.append(None)
    
    # policy titles
    policy_i = [elem.text for elem in soup.findAll('h3', attrs={'class':'feePolicyTitle'})]
    try:
        policyTitle.append(removeSpace(policy_i))
    except:
        policyTitle.append(None)
   
    # policy specifics
    policies_i = [elem.text for elem in soup.findAll('div', attrs={'class':'feespolicies'})]
    try:
        policies.append(removeSpace(policies_i))
    except:
        policies.append(None)

driver.quit() # close driver

# create empty df to store housing info
df = pd.DataFrame()

df['Links'] = houseLinks # add link for each listing to df


# split address list into area and address
temp = [elem.split('–') for elem in removeSpace(address)]
df['Address'] = [elem[0] for elem in temp] # address of house
df['Area'] = [elem[1] for elem in temp] # area house is in


# functiongets values in certain location in each sublist
def sepList(list_, loc, numOnly=False):
    """
    Function picks values in certain location in each sublist and returns them in their own list.

    Parameters
    ----------
    list_ : list
        List with sublists to be seperated.
    loc : int
        Location of element of interest in each sublist.
    numOnly : TYPE, optional
        If you only want the numbers in each string to be in the returned list. The default is False.

    Returns
    -------
    list
        List of values in specified substring loc.

    """
    # get list of values in certain location of each sublist
    
    temp = [elem[loc] if len(elem)-1>=loc and elem[loc]!='' else None for elem in list_]
    
    # remove all non digits from list
    if numOnly == True:
        info = []
        # iterate through each element in list
        for elem in temp:
            # skip over Nonetype values, adding None to the new list
            if elem is None:
                info.append(None)
                continue # go to next loop iteration
            # iterate through each character in element, only keep the digits
            newElem = int(''.join(char for char in elem if char.isdigit()))
            info.append(newElem)
        return info
    
    else:
        return temp


# split rentInfo list into specific lists based on type of info
df['Rent'] = sepList(rentInfo, 0, True) # rent price
df['No. Bedrooms'] = sepList(rentInfo, 1, True) # num of bedrooms
df['Square Footage'] = sepList(rentInfo, 3, True) # square footage
# calc rent per person based on the no. of bedrooms
df['Rent Per Person'] = df['Rent'] / df['No. Bedrooms']
df['Rent Per Person'] = df['Rent Per Person'].round(2) # round this col to 2 decimal places


# for num of bathrooms, remove unneeded characters & make formatting consistent
numBathrm = [] # num of bathrooms
# iterate through each elem in list
for elem in rentInfo:
    # if the elem is not empty
    if len(elem)!=0:
        # remove all alpha values, left with the float num of bathrooms
        numBathrm.append(float(''.join(char for char in elem[2] if not char.isalpha())))
    # if the elem is empty, put None
    else:
        numBathrm.append(None)
df['No. Bathrooms'] = numBathrm


# convert availability vals to consistent datetime format
avail = []
for elem in availability:
    # if house is available now
    if elem == 'Available Now':
        avail.append(date.today()) # today's date
    # if availability date not given
    elif elem=='blank':
        avail.append(None)
    # if date is given
    else:
        # for dates given w/o year
        try:
            newElem = dt.strptime(elem, "%b. %d") # format elem into datetime
            avail.append(dt.replace(newElem, year=2021).date()) # remove time from each elem before appending
        # for dates given with year
        except:
            newElem = dt.strptime(elem, "%b. %d, %Y") # format elem into datetime
            avail.append(newElem.date())
df['Availability'] = avail # add to df

# export housing info to excel file
df.to_excel(r'C:\Users\cnpol\Documents\ISE 435\Project\Data\HousingInfo.xlsx',
            sheet_name='General Info')


# make formatting of specifics more consistent
# within each sublist, seperate any existing elems
specifics_ = []
for elem in specifics:
    elems = []
    for val in elem:
        # if a single elem has a comma, seperate it into a list of its vals
        if ',' in val:
            specs = val.split(',')
            [elems.append(spec) for spec in specs]
        else:
            elems.append(val)
    specifics_.append(elems) # new list with all elems of each sublist in its own val

# remove any headers from elem in each sublist
specifics_f = []    
for elem in specifics_:
    elems = []
    for val in elem:
        # if the value has a header 'Amenities', remove it
        if 'Amenities -' in val:
            newVal = val.replace('Amenities -', '')
        # if the value has a header 'Appliances', remove it
        elif 'Appliances -' in val:
            newVal = val.replace('Appliances -', '')
        elif 'Pets -' in val:
            newVal = val.replace('Pets -', '')
        else:
            newVal = val
        elems.append(newVal)
    specifics_f.append(removeSpace(elems)) # new list without any headers

    
# create set of all unique amenities, policies, specifics
specs = set() # set can only have unique values
for elem in amenities:
    for amenity in elem:
        specs.add(amenity) # add amenities
for elem in specifics_f:
    for specific in elem:
        specs.add(specific) # add specifics
for elem in policies:
    for policy in elem:
        specs.add(policy) # add policies

# export specs set to excel file
pd.DataFrame(specs).to_excel(r'C:\Users\cnpol\Documents\ISE 435\Project\Data\SpecificsSet.xlsx',
                             sheet_name='Specifics')

specs_df = pd.DataFrame(columns=specs) # create df with all specs as column headers
specs_df['Amenities'] = amenities # add col for amenities
specs_df['Policies'] = policies # add col for policies
specs_df['Specifics'] = specifics_f # add col for specifics
specs_df.replace(np.nan, 0, inplace=True) # replace all nan values with 0

# create binary df, each house has 0 if it doesn't have a spec, 1 if it does
# iterate throuhg each row num in df
for row in range(len(specs_df)):
    # if that row (house) has listed amenities...
    if len(amenities[row]) != 0:
        # for each listed amenity of that row (house)
        for amenity in amenities[row]:
            # put a 1 in the col corresponding to that amenity for that row (house)
            specs_df.loc[row, amenity] = 1
    # if that row (house) has listed specifics...
    if len(specifics_f[row]) != 0:
        for specific in specifics_f[row]:
            specs_df.loc[row, specific] = 1
    # if that row (house) has listed policies...
    if len(policies[row]) != 0:
        for policy in policies[row]:
            specs_df.loc[row, policy] = 1

# export specifics to excel file
specs_df.to_excel(r'C:\Users\cnpol\Documents\ISE 435\Project\Data\HousingSpecifics.xlsx',
                  sheet_name='Specifics')


















