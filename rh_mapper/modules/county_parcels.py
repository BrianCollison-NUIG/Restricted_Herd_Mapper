import geopandas as gpd
import time

app_start = time.time()

def main():

    """ Section A
    
        Section A only needs to be run once to create a new shape file containing permanent pastures only
        It can be commented out after first execution
        
    """

    print('start... section A')

    # gdf = gpd.GeoDataFrame
    # gdf_output = gpd.GeoDataFrame
    # initial_data = []
    # # Master shape file
    # f = '/home/bcollison/Restricted_Herd_Mapper/data/shape_files/lpis/LPIS_2021_EXTRACT_MASTER_ING.shp'

    # gdf = gpd.read_file(f)
    # # Only retrieve permanent pastures
    # gdf = gdf.groupby(by='CRP_CROP_D')
    # gdf = gdf.get_group('Permanent Pasture')

    # # Read the first character of the land parcel id and append to a list variable
    # # After processing all parcels, add the list varibale to the GoeDataFrame
    # for _, parcel in gdf.iterrows():
    #     initial = parcel['LNU_PARCEL']
    #     initial = initial[0:1]
    #     initial_data.append(initial)

    # gdf_output = gdf.assign(County_Initial=initial_data)

    # # Create a new shape file for permanent pastures only also adding the new county initial column to the file
    # gdf_output.to_file('/home/bcollison/rh_mapper/data/shapes/parcels/County_PP_LPIS_2021_Extract.shp')

    """ Section B
    
        Section B is used to create new shape files on a per county basis.
        The county_initial column is used to seperate land parcels by county
        and save to a new shape file.
        
    """
    print('start... section B')

    gdf = gpd.GeoDataFrame
    f = '/home/bcollison/rh_mapper/data/shapes/parcels/County_PP_LPIS_2021_Extract.shp'

    gdf = gpd.read_file(f)
    gdf = gdf.groupby(by='County_Ini')
    gdf = gdf.get_group('N') # Parcels in County X

    gdf.to_file('/home/bcollison/rh_mapper/data/shapes/parcels/sub_county/Longford County.shp') # Change shp filename for different counties.

    print('Shows Over!')

if __name__ == '__main__':
    main()

print("\n" + 40*"#")
print(time.time() - app_start)
print(40*"#" + "\n")