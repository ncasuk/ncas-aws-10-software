import datetime as dt
import numpy as np
from netCDF4 import Dataset
import csv

import read_aws
import basic_qc_aws
from ncas_amof_netcdf_template import create_netcdf, util, remove_empty_variables


   
    
def get_data(aws_file):
    df = read_aws.aws_to_csv(aws_file)
    dt_times = [dt.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S.%f") for i in df['Timestamp']]
    
    air_pressure = np.array([float(i) for i in df['Pa']])
    air_temperature = np.array([float(i) for i in df['Ta']])
    relative_humidity = np.array([float(i) for i in df['Ua']])
    wind_speed = np.array([float(i) for i in df['Sm']])
    wind_from_direction = np.array([float(i) for i in df['Dm']])
    thickness_of_rainfall_amount = np.array([float(i) for i in df['Rc']])
    rainfall_rate = np.array([float(i) for i in df['Ri']])
    hail_intensity = np.array([float(i) for i in df['Hc']])
    hail_rate = np.array([float(i) for i in df['Hi']])
    
    return dt_times, {'air_pressure':air_pressure, 'air_temperature':air_temperature, 'relative_humidity':relative_humidity, 'wind_speed':wind_speed, 'wind_from_direction':wind_from_direction, 'thickness_of_rainfall_amount':thickness_of_rainfall_amount, 'rainfall_rate':rainfall_rate, 'hail_intensity':hail_intensity, 'hail_rate':hail_rate}



def make_netcdf_surface_met(aws_file, metadata_file = None, ncfile_location = '.', verbose = False):
    if verbose: print('Getting data')
    dt_times, data = get_data(aws_file)
    qc_flags = basic_qc_aws.check_valid(data)
    unix_times, doy, years, months, days, hours, minutes, seconds, time_coverage_start_dt, time_coverage_end_dt, file_date = util.get_times(dt_times)
    
    if verbose: print('Making netCDF file')
    create_netcdf.main('ncas-aws-10', date = file_date, dimension_lengths = {'time':len(dt_times)}, loc = 'land', products = ['surface-met'], file_location=ncfile_location)
    ncfile = Dataset(f'{ncfile_location}/ncas-aws-10_iao_{file_date}_surface-met_v1.0.nc', 'a')
    
    if verbose: print('Adding variables')
    util.update_variable(ncfile, 'air_pressure', data['air_pressure'])
    util.update_variable(ncfile, 'air_temperature', data['air_temperature'])
    util.update_variable(ncfile, 'relative_humidity', data['relative_humidity'])
    util.update_variable(ncfile, 'wind_speed', data['wind_speed'])
    util.update_variable(ncfile, 'wind_from_direction', data['wind_from_direction'])
    util.update_variable(ncfile, 'thickness_of_rainfall_amount', data['thickness_of_rainfall_amount'])
    util.update_variable(ncfile, 'rainfall_rate', data['rainfall_rate'])
    util.update_variable(ncfile, 'hail_intensity', data['hail_intensity'])
    util.update_variable(ncfile, 'hail_rate', data['hail_rate'])
    
    util.update_variable(ncfile, 'time', unix_times)
    util.update_variable(ncfile, 'year', years)
    util.update_variable(ncfile, 'month', months)
    util.update_variable(ncfile, 'day', days)
    util.update_variable(ncfile, 'hour', hours)
    util.update_variable(ncfile, 'minute', minutes)
    util.update_variable(ncfile, 'second', seconds)
    util.update_variable(ncfile, 'day_of_year', doy)
    
    for key, value in qc_flags.items():
        util.update_variable(ncfile, key, value)
    
    if verbose: print('Adding global attributes')
    ncfile.setncattr('time_coverage_start', dt.datetime.fromtimestamp(time_coverage_start_dt, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S %Z"))
    ncfile.setncattr('time_coverage_end', dt.datetime.fromtimestamp(time_coverage_end_dt, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S %Z"))
    
    util.add_metadata_to_netcdf(ncfile, metadata_file)
                
    # if lat and lon given, no need to also give geospatial_bounds
    # this works great for point deployment (e.g. ceilometer)
    lat_masked = ncfile.variables['latitude'][0].mask
    lon_masked = ncfile.variables['longitude'][0].mask
    geospatial_attr_changed = "CHANGE" in ncfile.getncattr('geospatial_bounds')
    if geospatial_attr_changed and not lat_masked and not lon_masked:
        geobounds = f"{ncfile.variables['latitude'][0]}N, {ncfile.variables['longitude'][0]}E"
        ncfile.setncattr('geospatial_bounds', geobounds)
    
    ncfile.close()
    
    if verbose: print('Removing empty variables') 
    remove_empty_variables.main(f'{ncfile_location}/ncas-aws-10_iao_{file_date}_surface-met_v1.0.nc', verbose = verbose)
    
    if verbose: print('Complete')

    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description = 'Create AMOF-compliant netCDF file for ncas-aws-10 instrument.')
    parser.add_argument('input_file', type=str, help = 'Raw data from instrument.')
    parser.add_argument('-v','--verbose', action='store_true', help = 'Print out additional information.', dest = 'verbose')
    parser.add_argument('-m','--metadata', type = str, help = 'csv file with global attributes and additional metadata. Default is None', dest='metadata')
    parser.add_argument('-o','--ncfile-location', type=str, help = 'Path for where to save netCDF file. Default is .', default = '.', dest="ncfile_location")
    
    # Only option actually available is surface-met, however code kept here for ease in case of future change
    #parser.add_argument('-p','--products', nargs = '*', help = 'Products of ncas-aws-10 to make netCDF files for. Options are surface-met. One or many can be given (space separated), default is "surface-met".', default = ['surface-met'])
    
    args = parser.parse_args()
    
    make_netcdf_surface_met(args.input_file, metadata_file = args.metadata, ncfile_location = args.ncfile_location, verbose = args.verbose)
    
    # again, not needed now as only one product but kept here for future use
    
    #for prod in args.products:
    #    if prod == 'surface-met':
    #        make_netcdf_surface_met(args.input_csv, metadata_file = args.metadata, ncfile_location = args.ncfile_location)
    #    else:
    #        print(f'WARNING: {prod} is not recognised for this instrument, continuing with other prodcuts...')
