# -*- coding: utf-8 -*-
"""
Created on Mon May 23 14:53:04 2022

@author:        Brian Collison.
@student ID:    19240223.

@module name:   main.py.

"""

from Restricted_Herd_Map import Restricted_Herd_Map
import pandas as pd
import streamlit as st
import time
import datetime
import os


app_start = time.time()

def main(): 
    # Application entry here.  
    print('App Launched...')
    display_interface()      

def display_interface():
    # Method that creates the apllication user interface using streamlit.
    st.title('Restricted Herd Mapper')

    # Create a streamlit sidebar and add controls.
    with st.sidebar:
        st.image('/home/bcollison/rh_mapper/images/dafm.jpg') # Dept. of Agriculture logo.
        restricted_herd_data_file = st.file_uploader('Upload Restricted Herd Details', 'csv') # Allow user to upload csv filetypes only.

        # Display list of counties in a drop down list
        county_file = '/home/bcollison/rh_mapper/data/county_list/county_list.csv'
        df = pd.read_csv(county_file)        
        df = df.sort_values('NAME', ascending=True) # Sort the dataframe by county alphabetically.
        county = st.selectbox('Please select a location', df['NAME'], index=23) # Default value of dropdown list set to 'None'

        start_date = st.date_input('Breakdown Date', value=None)
        end_date =st.date_input('Breakdown End Date', value=None)

        action = st.button('Submit')
        download_map = st.checkbox('Save map?', value=False)


    if action:
        # The user has clicked the st.button.
        (valid, error_message) = validate_control_values(restricted_herd_data_file, county, start_date, end_date)

        if valid == 'true':
            # Create mapping object  
            rhm = Restricted_Herd_Map(restricted_herd_data_file, county, start_date, end_date)
            rhm.draw_map()
            if download_map:
                file_name = 'restricted_herd_map' + '_'  + str(datetime.datetime.now()) + '.html'
                file_dir = '/home/bcollison/rh_mapper/downloads/'
                file_path = os.path.join(file_dir, file_name)
                rhm.m.save(file_path)    # Save a copy of the map locally
                st.sidebar.text('Map saved as:')
                st.sidebar.text(file_path)
        else:
            st.sidebar.text(error_message)

    print('Shows Over!')


def validate_control_values(restricted_herd_data_file, county, start_date, end_date):
    # Validate sidebar control values inout by the user.

    valid = 'true' # String boolean variable
    error_message = ''

    if restricted_herd_data_file is None:   # check that the user selected a restricted herd data file.
        valid = 'false'
        error_message = 'Error: No file selected'
        return valid, error_message

    if county == 'None':   # check that the user selected a county from the dropdown list.
        valid = 'false'
        error_message = 'Error: No county selected'
        return valid, error_message

    if start_date > end_date:   # Check that the dates entered are valid
        valid = 'false'
        error_message = 'Error: Invalid date range entered'
        return valid, error_message
    
    # If all OK return true.
    return valid, error_message


if __name__ == "__main__":
    main() 

print("\n" + 40*"#")
print(time.time() - app_start)
print(40*"#" + "\n")