# -*- coding: utf-8 -*-
"""
Created on Sun May 29 13:15:33 2022

@author:        Brian Collison.
@student ID:    19240223.

@module name:   Restricted_Herd_Map.py

"""

import pandas as pd
import geopandas as gpd
import folium
import datetime as dt
from datetime import datetime
import streamlit.components.v1 as components


class Restricted_Herd_Map:

    # ===============================
    # Class Attributes
    # ===============================

    # Parcel color coding, using hex colour codes:
    no_risk_style  = {'fillColor': '#008000', 'color': '#008000'}       # Green.
    high_risk_style  = {'fillColor': '#FF0000', 'color': '#FF0000'}     # Red.
    medium_risk_style  = {'fillColor': '#ffbf00', 'color': '#ffbf00'}   # Amber.
    low_risk_style  = {'fillColor': '#ffff00', 'color': '#ffff00'}      # Yellow.

    # Restricted herd file
    restricted_herd_csv_file = ''

    # Shape file paths
    parcel_shape_file_path = '/home/bcollison/rh_mapper/data/shapes/parcels/sub_county/'
    parcel_shape_file = ''
    county_shape_file = '/home/bcollison/rh_mapper/data/shapes/county/counties.shp'

    df_restricted_herds = pd.DataFrame()
    gdf_parcels = gpd.GeoDataFrame()
    gdf_counties = gpd.GeoDataFrame()
    gdf_restricted_parcels = gpd.GeoDataFrame()
    gdf_non_restricted_parcels = gpd.GeoDataFrame()

    # Map size coordinates 
    map_height = 700
    map_width = 850
    map_start_position = []

    filter_by_date = 'false'
    
    # ===============================
    # Class Instance Methods
    # ===============================   

    def __init__(self, restricted_herd_data_file, county, start_date, end_date):
        # Populate Instance attributes
        #          

        # Check if filtering herds by date, if both dates do not equal todays date, then set to true
        if start_date == dt.date.today() and end_date == dt.date.today():
            self.filter_by_date = 'false'
        else:
            self.filter_by_date = 'true'

        self.restricted_herd_csv_file =  restricted_herd_data_file
        self.county = county
        self.start_date = start_date
        self.end_date = end_date

        self.read_county_shapefile()
        self.parcel_shape_file = self.parcel_shape_file_path + self.county + '.shp'

        # Create map folium map object.
        self.m = folium.Map(location=self.map_start_position, tiles='OpenStreetMap', zoom_start=11, control_scale=True)
        #OpenStreetMap

    def draw_map(self):
        # Method to generate the map.
        self.read_rhd_file()            # Get restricted herd ids and dates
        self.read_parcel_shape_file()   # Retrieve land parcel geometries
        self.process_parcel_data()      # Flag any parcels used by restricted herds
        self.gen_county_layer()         # Add county boundaries to a mapping layer
        self.gen_parcel_layer()         # Add each parcel to a layer
        self.gen_restricted_herd_layer() # Create a marker and popup for each restricted herd

        folium.LayerControl().add_to(self.m)
        fig = folium.Figure().add_child(self.m)
        components.html(fig.render(), height=self.map_height, width=self.map_width) # Display the map.


    def read_county_shapefile(self):
        # Read county data from shapefile and set map start position coordinates
        #
        gdf = gpd.GeoDataFrame # local variable.

        self.gdf_counties = gpd.read_file(self.county_shape_file)
        self.gdf_counties = self.gdf_counties[['COUNTY', 'COUNTYNAME', 'geometry']]
        self.gdf_counties = self.gdf_counties.to_crs(epsg = 4326)

        gdf = self.gdf_counties.loc[lambda gdf: gdf['COUNTYNAME'] == self.county]
        coordinates = gdf['geometry'].centroid        
        X = coordinates.x
        Y = coordinates.y

        self.map_start_position = [Y, X]


    def read_rhd_file(self):
        # Read csv file containing restricted herd details
        #
        df = pd.DataFrame # local variable
        try:       
            df = pd.read_csv(self.restricted_herd_csv_file)
            self.df_restricted_herds = df
        except:
            pass


    def read_parcel_shape_file(self):
        # Method to read land parcel data from shape file.
        #  
        gdf = gpd.GeoDataFrame # Local variable

        try:
            gdf = gpd.read_file(self.parcel_shape_file)             #, rows=10000)

            # Strip out columns that are not required.
            gdf = gdf[['HERD', 'HOLDING_ID', 'LNU_PARCEL', 'geometry']]
            # Append an additional column 'restricted' with a default value of 'n' to the GeoDataFrame.
            gdf['RESTRICTED'] = 'n'
            # Append additional columns to the GeoDataFrame.
            gdf['Breakdown Date'] = ''
            gdf['Breakdown End Date'] = ''
            gdf['No of Amls'] = ''
            gdf['Days Rst'] = ''
            gdf['No of Herd tests since breakdown'] = ''
            gdf['No of Reactors in Current Breakdown'] = ''
            gdf['Next Test Date'] = ''
            gdf['No of Parcels'] = ''
            gdf = gdf.to_crs(epsg = 4326)
            self.gdf_parcels = gdf
        except:
            pass # Trap shape file not found error


    def process_parcel_data(self):
        # Flag parcels that are used by restricted herds.
        # Add restriction start and end date to the GeoDataFrame
        #
        gdf = gpd.GeoDataFrame # Local variable

        # Check that gdf_parcels contains data.
        if self.gdf_parcels.empty != True:
            # Check if we have any retstricted herds
            if self.df_restricted_herds.empty != True:
                # Find parcels may be used by retricted herds.
                for x in range(len(self.df_restricted_herds['RESTRICTED_HERD_ID'])):
                    herd_id = self.df_restricted_herds['RESTRICTED_HERD_ID'].iloc[x]
                    gdf = self.gdf_parcels.groupby('HERD')

                    try:
                        gdf = gdf.get_group(herd_id)
                        for y in range(len(gdf.index)):
                            i = (gdf.index[y])
                            self.gdf_parcels.iat[i, 4] = 'y'
                            
                            if not str(self.df_restricted_herds['Breakdown Date'].iloc[x]) == 'nan':    # Check that we have a breakdown start date.
                                self.gdf_parcels.iat[i, 5] = datetime.date(datetime.strptime(self.df_restricted_herds['Breakdown Date'].iloc[x],"%d/%m/%Y"))
                            if not str(self.df_restricted_herds['Breakdown End Date'].iloc[x]) == 'nan':     # Check that we have a breakdown end date.
                                self.gdf_parcels.iat[i, 6] = datetime.date(datetime.strptime(self.df_restricted_herds['Breakdown End Date'].iloc[x],"%d/%m/%Y"))
                            self.gdf_parcels.iat[i, 7] = self.df_restricted_herds['No of Amls'].iloc[x]
                            self.gdf_parcels.iat[i, 8] = self.df_restricted_herds['Days Rst'].iloc[x]
                            self.gdf_parcels.iat[i, 9] = self.df_restricted_herds['No of Herd tests since breakdown'].iloc[x]
                            self.gdf_parcels.iat[i, 10] = self.df_restricted_herds['No of Reactors in Current Breakdown'].iloc[x]
                            if not str(self.df_restricted_herds['Next Test Date'].iloc[x]) == 'nan':    # Check that we have a next test date.
                                self.gdf_parcels.iat[i, 11] = datetime.date(datetime.strptime(self.df_restricted_herds['Next Test Date'].iloc[x],"%d/%m/%Y"))
                            self.gdf_parcels.iat[i, 12] = len(gdf.index) # No of parcels used by the restricted herd.
                    except:
                        pass # Herd not found, trap error and continue with next retstricted herd.
 
        # Seperate restricted/ non restricted parcels for improved access
        if self.gdf_parcels.empty != True:
            gdf = self.gdf_parcels.groupby('RESTRICTED')

            try:
                self.gdf_restricted_parcels = gdf.get_group('y')
            except:
                pass # Data does not contain any herds that are restricted.

            try:
                self.gdf_non_restricted_parcels = gdf.get_group('n')
            except:
                pass # No herds in data thta are not under restriction.


    def gen_county_layer(self):
        # Create a folium fg and add each county.
        fg = folium.FeatureGroup('County')

        # Add each county to the feature group.
        for _, county in self.gdf_counties.iterrows():
            county_shape = gpd.GeoSeries(county['geometry'])
            county_shape  = county_shape.to_json()
            county_shape = folium.GeoJson(data=county_shape,
                                        style_function=lambda x: {'fillColor': '#ffffff'},)  # White fill colour
            county_shape.add_to(fg)
            
        fg.add_to(self.m)
    

    def gen_parcel_layer(self): 
        # Create a folium fg and add all parcels.
        #
        # Local variables
        gdf = gpd.GeoDataFrame 

        # Draw non restricted parcels
        # Use green colour shade for parcels with non restricted herds
        fg = folium.FeatureGroup('Non-Restricted Herd Parcels')
        for _, parcel in self.gdf_non_restricted_parcels.iterrows():                            
            parcel_shape = gpd.GeoSeries(parcel['geometry'])
            parcel_shape = parcel_shape.to_json()
            parcel_shape = folium.GeoJson(data=parcel_shape,
                    style_function=lambda x: self.no_risk_style)
            folium.Popup('Herd:' + parcel['HERD'] + ' ' + 'Parcel:' + parcel['LNU_PARCEL']).add_to(parcel_shape)
            parcel_shape.add_to(fg)

        fg.add_to(self.m)


        # Restricted parcels
        if len(self.gdf_restricted_parcels.index) > 0: # Check that there are restricted herds to display
            gdf = self.gdf_restricted_parcels.sort_values(by='HERD') # Sort geodataframe by herd id
            fg = folium.FeatureGroup('Restricted Herd Parcels')

            if self.filter_by_date == 'true':

                for _, parcel in gdf.iterrows():
                    num_reactors = parcel['No of Reactors in Current Breakdown']
                    restricted_colour_style = self.get_parcel_colour_style(num_reactors)
                    parcel_shape = gpd.GeoSeries(parcel['geometry'])
                    parcel_shape = parcel_shape.to_json()

                    if parcel['Breakdown Date'] != '' and parcel['Breakdown End Date'] != '':
                        if parcel['Breakdown Date'] >= self.start_date and parcel['Breakdown End Date'] <= self.end_date:
                            parcel_shape = folium.GeoJson(data=parcel_shape,
                                style_function=lambda x, restricted_colour_style=restricted_colour_style: restricted_colour_style)
                        else:
                            parcel_shape = folium.GeoJson(data=parcel_shape,
                                style_function=lambda x: self.no_risk_style) 
                        # Parcel popup to display the Herd and Parcel ID when polygon clicked
                        folium.Popup('Herd:' + parcel['HERD'] + ' ' + 'Parcel:' + parcel['LNU_PARCEL']).add_to(parcel_shape)
                        parcel_shape.add_to(fg)   
                    
                fg.add_to(self.m)
            else:

                for _, parcel in gdf.iterrows():
                    num_reactors = parcel['No of Reactors in Current Breakdown']
                    restricted_colour_style = self.get_parcel_colour_style(num_reactors)
                    parcel_shape = gpd.GeoSeries(parcel['geometry'])
                    parcel_shape = parcel_shape.to_json()

                    parcel_shape = folium.GeoJson(data=parcel_shape, 
                        style_function=lambda x, restricted_colour_style=restricted_colour_style: restricted_colour_style)
                    # Parcel popup to display the Herd and Parcel ID when polygon clicked
                    folium.Popup('Herd:' + parcel['HERD'] + ' ' + 'Parcel:' + parcel['LNU_PARCEL']).add_to(parcel_shape)
                    parcel_shape.add_to(fg)

                fg.add_to(self.m)


    def gen_restricted_herd_layer(self):
        # Create a layer to hold restricted herd folium markers.
        #
        fg = folium.FeatureGroup('Markers')     
        gdf = gpd.GeoDataFrame # Local variable.
        # Only create one marker per herd. 
        gdf = self.gdf_restricted_parcels.drop_duplicates(subset = 'HERD')

        for _, restricted_parcel in gdf.iterrows():
            # Check if we are filtering herds by retriction dates.
            if self.filter_by_date == 'true':
                if restricted_parcel['Breakdown Date'] != '' and restricted_parcel['Breakdown End Date'] != '':
                    if restricted_parcel['Breakdown Date'] >= self.start_date and restricted_parcel['Breakdown End Date'] <= self.end_date:
                        html = self.create_popup(restricted_parcel)
                        popup = folium.Popup(folium.Html(html, script=True), max_width=500)
                        point = restricted_parcel['geometry'].centroid
                        folium.Marker(location=[point.bounds[1], point.bounds[0]], popup=popup, icon=folium.Icon(icon = 'glyphicon glyphicon-info-sign')).add_to(fg)
                            
            else:
                html = self.create_popup(restricted_parcel)
                popup = folium.Popup(folium.Html(html, script=True), max_width=500)
                point = restricted_parcel['geometry'].centroid
                folium.Marker(location=[point.bounds[1], point.bounds[0]], popup=popup, icon=folium.Icon(icon = 'glyphicon glyphicon-info-sign')).add_to(fg)
        
        fg.add_to(self.m)

    
    def get_parcel_colour_style(self, num_of_reactors):
        # Assign a parcel colour coding style based on the number of reactors in the current TB breakdown.
        #
        if num_of_reactors < 2:
            style = self.low_risk_style
        elif num_of_reactors == 2:
            style = self.medium_risk_style
        else:
            # 3 or more reactors
            style = self.high_risk_style

        return style


    def create_popup(self, restricted_parcel_row):
        # Method that creates a popup for folium marker on the map
        #
        # Local variables.
        parcels = [] 
        str_parcels = ''
        gdf = gpd.GeoDataFrame 

        herd_id = restricted_parcel_row['HERD']
        if type(restricted_parcel_row['Breakdown Date']) is dt.date:
            st_date = restricted_parcel_row['Breakdown Date'].strftime('%d/%m/%Y')
        else:
            st_date = ''
        if type(restricted_parcel_row['Breakdown End Date']) is dt.date:
            end_date = restricted_parcel_row['Breakdown End Date'].strftime('%d/%m/%Y')
        else:
            end_date = ''
        num_animals = restricted_parcel_row['No of Amls']
        num_days_restr = restricted_parcel_row['Days Rst']
        num_tests = restricted_parcel_row['No of Herd tests since breakdown']
        num_react = restricted_parcel_row['No of Reactors in Current Breakdown']
        if type(restricted_parcel_row['Next Test Date']) is dt.date:
            next_test = restricted_parcel_row['Next Test Date'].strftime('%d/%m/%Y')
        else:
            next_test = ''
        num_parcels = restricted_parcel_row['No of Parcels'] 

        # Get the parcels for the current Herd ID.
        gdf = self.gdf_restricted_parcels.groupby('HERD')
        gdf = gdf.get_group(herd_id)

        # Create string of the parcel id's to add to the popup
        parcels = gdf['LNU_PARCEL']
        for x in parcels:
            str_parcels = str_parcels + str(x) + ', '

        # Remove trailing comma after last parcel was added to the string
        str_parcels = str_parcels[:-2]

        html = """<!DOCTYPE html>
            <html>
            <head>
            <h4 style="margin-bottom:10"; width="200px">{}</h4>""".format('Restricted Herd Details') + """
            </head>
            <table style="height: 100px; width: 500px;">
            <body>
            <tr>
                <td style="width: 500px;">Herd ID:</td>
                <td style="width: 125px;">{}</td>""".format(herd_id) + """
            </tr>
            <tr>
                <td style="width: 500px;">Breakdown Date:</td>
                <td style="width: 125px;">{}</td>""".format(st_date) + """ 
            </tr>
            <tr>
                <td style="width: 500px;">Breakdown End Date:</td>
                <td style="width: 125px;">{}</td>""".format(end_date) + """
            </tr>
            <tr>
                <td style="width: 500px;">No. of Animals:</td>
                <td style="width: 125px;">{}</td>""".format(num_animals) + """
            </tr>
            <tr>
                <td style="width: 500px;">Days Restricted:</td>
                <td style="width: 125px;">{}</td>""".format(num_days_restr) + """
            </tr>
            <tr>
                <td style="width: 500px;">No. of Herd tests since breakdown:</td>
                <td style="width: 125px;">{}</td>""".format(num_tests) + """
            </tr>
            <tr>
                <td style="width: 500px;">No. of Reactors in Current Breakdown:</td>
                <td style="width: 125px;">{}</td>""".format(num_react) + """
            </tr>
            <tr>
                <td style="width: 500px;">Next Test Date:</td>
                <td style="width: 125px;">{}</td>""".format(next_test) + """
            </tr>
            <tr>
                <td style="width: 500px;">No. of Parcels:</td>
                <td style="width: 125px;">{}</td>""".format(num_parcels) + """
            </tr>
            <tr>
                <td style="width: 500px;">Parcel ID's:</td>
                <td style="width: 500px;"></td>
            </tr>
            <tr>
                <td style="width: 500px;"></td>
                <td style="width: 500px;">{}</td>""".format(str_parcels) + """
            </tr>

            </body>
            </table>
            </html>
            """

        return html

    #===============================================
    # Class Getters/ Setters
    #===============================================
        
    # restricted_herd_csv_file
    @property
    def restricted_herd_csv_file(self):
        return self._restricted_herd_csv_file
    
    @restricted_herd_csv_file.setter
    def restricted_herd_csv_file(self, csv):
        self._restricted_herd_csv_file = csv

    # parcel_shape_file
    @property
    def parcel_shape_file(self):
        return self._parcel_shape_file
    
    @parcel_shape_file.setter
    def parcel_shape_file(self, sfile):
        self._parcel_shape_file = sfile

    # m
    @property
    def m(self):
        return self._m
    
    @m.setter
    def m(self, map):
        self._m = map

    # county
    @property
    def county(self):
        return self._county
    
    @county.setter
    def county(self, c):
        self._county = c

    # start_date
    @property
    def start_date(self):
        return self._start_date
    
    @start_date.setter
    def start_date(self, sdate):
        self._start_date = sdate

    # end_date
    @property
    def end_date(self):
        return self._end_date
    
    @end_date.setter
    def end_date(self, edate):
        self._end_date = edate



    
        
        
        