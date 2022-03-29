"""
Create AMOF compliant netCDF file for ncas-aws-10 from vaisala weather station output.

"""

#######################################################
# This section is needed for relative imports to work
import sys
from pathlib import Path

if __name__ == '__main__' and __package__ is None:
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[2]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # Already removed
        pass

    import ncas_aws_10.core
    __package__ = 'ncas_aws_10.core'
#######################################################

from netCDF4 import Dataset
import numpy as np
import datetime as dt

from ..util import create_netcdf as create_netcdf
from ..util import add_datasets as add_datasets
from ..util import helpful_functions as hf
from . import read_aws_data as read_aws
from . import basic_qc as qc


#################################
# Set a few things here for now #
#################################

# which amof version?
amof_version = "2.0"

# raw data file location
raw_data_loc = '/gws/nopw/j04/ncas_obs/iao/raw_data/ncas-aws-10/incoming'

# These are all attributes so far
platform = 'iao'
platform_type = 'stationary_platform'  # One of: stationary_platform, moving_platform
comment = 'None'
featureType = 'timeSeries'
processing_level = 0  # for now

instrument_manufacturer = 'Vaisala'
instrument_model = 'WXT536'
instrument_serial_number = 'N404071 PTU: P5040241'

# these are not available from the weather station
# use float32s, -90 - +90 for lat, -180 - +180 for lon
latitude = np.float32(52.3141)
longitude = np.float32(-1.5426423)


# stuff for create_netcdf.main_v2
netcdf_file_location = '/home/users/earjham/bin/writing_netcdf/test_nc_files'
instrument_name = 'ncas-aws-10'
pi_scientist = 'barbara.brooks@ncas.ac.uk'
creator_scientist = 'barbara.brooks@ncas.ac.uk'
dimensions_product = 'surface-met'
variables_product = 'surface-met'
attrs_product = 'surface-met'
common_loc = 'land'
options = 'someheight'
product_version = '1.0'


# somewhere to store the file created by read_aws.aws_to_csv
tmp_dir = '/work/scratch-pw/earjham/iceland_test'


def main(date, raw_data_loc=raw_data_loc, tmp_dir=tmp_dir, platform=platform, 
         platform_type=platform_type, comment=comment, 
         featureType=featureType, processing_level=processing_level, 
         instrument_manufacturer=instrument_manufacturer, 
         instrument_model=instrument_model, 
         instrument_serial_number=instrument_serial_number, 
         latitude=latitude, longitude=longitude, 
         netcdf_file_location=netcdf_file_location, instrument_name=instrument_name, 
         pi_scientist=pi_scientist, creator_scientist=creator_scientist,
         dimensions_product=dimensions_product, variables_product=variables_product, 
         attrs_product=attrs_product, location=platform, common_loc=common_loc, 
         options=options, product_version=product_version, amof_version=amof_version):
    """
    Creates AMOF compliant netCDF file with the data from a daily csv file created by :py:func:`read_aws_data.csv_to_dict`
    
    Args:
        date (str): Date string in format YYYYmmdd
        raw_data_loc (str): Location of raw data
        tmp_dir (str): Place to store file created by :py:func:`read_aws_data.aws_to_csv`
        platform (str): Name of the platform on which the instrument was deployed. Global attribute for netCDF file.
        platform_type (str): Type of platform on which the instrument was deployed. Global attribute for netCDF file.
        comment (str): Any other text that might be useful. Use "None" if no comment needed. Global attribute for netCDF file.
        featureType (str): Feature Type of measurements (set for each instrument type). Global attribute for netCDF file.
        processing_level (int): Data product level. Possible values: 0: native, 1: basic QC, 2: high-level QC, 3: product derived from levels 1 and 2 data. Global attribute for netCDF file.
        instrument_manufacturer (str): Manufacturer of instrument and key sub components. Global attribute for netCDF file.
        instrument_model (str): Model number of instrument and key sub components. Global attribute for netCDF file.
        instrument_serial_number (str): Serial number of instrument and key sub components. Global attribute for netCDF file.
        latitude (float): Latitude of instrument location. Dimension and global attribute (geospatial_bounds) for netCDF file.
        longitude (float): Longitude of instrument location. Dimension and global attribute (geospatial_bounds) for netCDF file.
        netcdf_file_location (str): Location where to save netCDF file to. Supplied to :py:func:`create_netcdf.main_v2`.
        instrument_name (str): Name of instrument, should be in https://github.com/ncasuk/AMF_CVs/blob/v2.0.0/AMF_CVs/AMF_ncas_instrument.json. Supplied to :py:func:`create_netcdf.main_v2`.
        pi_scientist (str or dict): Either the email of the project principal investigator (should be in https://github.com/ncasuk/AMF_CVs/blob/v2.0.0/AMF_CVs), or a dictionary with keys name, primary_email, and orcid. Supplied to :py:func:`create_netcdf.main_v2`.
        creator_scientist (str or dict): Either the email of the creator (should be in https://github.com/ncasuk/AMF_CVs/blob/v2.0.0/AMF_CVs), or a dictionary with keys name, primary_email, and orcid. Supplied to :py:func:`create_netcdf.main_v2`.
        dimensions_product (str): Name of product for product-specific dimensions. Should be in https://github.com/ncasuk/AMF_CVs/blob/v2.0.0/AMF_CVs/AMF_product.json. Supplied to :py:func:`create_netcdf.main_v2`.
        variables_product (str): Name of product for product-specific variables. Should be in https://github.com/ncasuk/AMF_CVs/blob/v2.0.0/AMF_CVs/AMF_product.json. Supplied to :py:func:`create_netcdf.main_v2`.
        attrs_product (str): Name of product for product-specific general attributes. Should be in https://github.com/ncasuk/AMF_CVs/blob/v2.0.0/AMF_CVs/AMF_product.json. Supplied to :py:func:`create_netcdf.main_v2`.
        location (str): Where is the instrument (wao, cao, cdao, e.t.c.). Supplied to :py:func:`create_netcdf.main_v2`.
        common_loc (str): Location of instrument for common dimensions, variables and attributes. One of 'land', 'sea', 'air', 'trajectory'. Supplied to :py:func:`create_netcdf.main_v2`.
        options (str): Comma separated string of options for name of netCDF file. Supplied to :py:func:`create_netcdf.main_v2`.
        product_version (str): Product version of data in netCDF file. Supplied to :py:func:`create_netcdf.main_v2`.
        amof_version (str): Version of AMOF convention
        
    """
         
    datafile = f'{raw_data_loc}/{date}_vaisala.csv'
    
    # read in file just to be able to count how many lines, and therefore how many times
    with open(datafile, 'r') as f:
        for count, line in enumerate(f):
            pass
    total_times = count + 1
    
    # create the netcdf
    # the options used in here need to be moved somewhere more accessible
    if amof_version == "2.0":
        filename = create_netcdf.main_v2(netcdf_file_location, instrument_name, pi_scientist, creator_scientist, variables_product, platform, common_loc, date, total_times, product_version, alt_length = 0, options=options, dimensions_product=dimensions_product, attrs_product=attrs_product)
    elif amof_version == "1.1":
        filename = create_netcdf.main_v1_1(netcdf_file_location, instrument_name, pi_scientist, creator_scientist, variables_product, platform, common_loc, date, total_times, product_version, index_length = 0, options=options, dimensions_product=dimensions_product, attrs_product=attrs_product)
    
    # open the netcdf to append the data to
    ncfile = Dataset(filename, 'a')
    
    # read in the data from the weather station
    read_aws.aws_to_csv(datafile, f'{tmp_dir}/{date}.csv')
    data, attrs = read_aws.csv_to_dict(f'{tmp_dir}/{date}.csv')
    
    # Basic QC, just checking against manufacturer-stated operating range
    qc_flags = qc.check_valid(data)
    
    # add data to netcdf
    for data_name in data.keys():
        add_datasets.add_dataset(ncfile, data_name, data, 0)
        
    # add qc flag data to netcdf
    for data_name in qc_flags.keys():
        add_datasets.add_dataset(ncfile, data_name, qc_flags, 0)
    
    # write attributes to netcdf
    for attr in attrs.keys():
        if ncfile.getncattr(attr) == '':
            ncfile.setncattr(attr, attrs[attr])
        elif ncfile.getncattr(attr) != attrs[attr]:
            print(f'Global attribute {attr} changes with time, i={i}')
                
        
    # add in lat and lon vars, and geospatial_bounds attr
    ncfile['latitude'][:] = latitude
    ncfile['longitude'][:] = longitude
    ncfile.geospatial_bounds = f'{latitude}N, {longitude}E'
        
        
    # where possible, should start to fill in the empty attributes
    # I'll leave that for another day      
    ncfile.processing_level = processing_level
    ncfile.featureType = featureType
    ncfile.platform = platform
    ncfile.platform_type = platform_type
    ncfile.comment = comment
    ncfile.instrument_manufacturer = instrument_manufacturer
    ncfile.instrument_model = instrument_model
    ncfile.instrument_serial_number = instrument_serial_number
    ncfile.product_version = f'v{product_version}'
    
    # I think this should be in the json files, but it's not, so for now...
    ncfile.institution = 'National Centre for Atmospheric Science (NCAS)'
    
    
    # Can now add in values to time_coverage_start and time_coverage_end global attrs
    #2016-07-06T00:00:00
    first_time = ncfile['time'][0]  # should be unix time
    first_time = dt.datetime.fromtimestamp(int(first_time))
    ncfile.time_coverage_start = first_time.strftime('%Y-%m-%dT%H:%M:%S')
    last_time = ncfile['time'][-1]  # should be unix time
    last_time = dt.datetime.fromtimestamp(int(last_time))
    ncfile.time_coverage_end = last_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    
    
    # Check for still empty attributes
    for attr in ncfile.ncattrs():
        if ncfile.getncattr(attr) == '':
            print(f'Empty attribute: {attr}')
        
    ncfile.close()
    
    # Create a new file without the empty, product-specific variables,
    # then rename the new file to remove the old file
    hf.remove_empty_whole(filename, f'{filename[:-3]}-removed.nc', 'surface-met')
    
    
    
if __name__ == "__main__":
    date = sys.argv[1]  # YYYYmmdd
    if len(sys.argv) == 2:  # remember, sys.argv[0] is the python file name
        main(date)
    else:
        tmp_dir = sys.argv[2]  # otherwise, '/work/scratch-pw/earjham/iceland_test'
        main(date, tmp_dir = tmp_dir) 
