"""
Functions to read data from automatic weather stations

"""

import pandas as pd
import numpy as np
import csv
import datetime as dt



def csv_to_dict(full_filename):
    """
    Reads nice csv created by :py:func:`aws_to_csv` and returns dict 
    of useful stuff for netcdf files.
    
    Args:
        full_filename (str): File path and name to csv created by :py:func:`aws_to_csv`
        
    Returns:
        dict: Variables and data for netCDF file.
        dict: Global attributes for netCDF file
        
    """
    df = pd.read_csv(full_filename)
    # in one ugly line, read in each timestamp, convert to datetime object, convert to unix time
    datetimes = [dt.datetime.strptime(df['Timestamp'][i], '%Y-%m-%dT%H:%M:%S.%f') for i in range(len(df['Timestamp']))]
    unix_time = np.array([datetimes[i].timestamp() for i in range(len(df['Timestamp']))])
    year = np.array([datetimes[i].year for i in range(len(df['Timestamp']))])
    month = np.array([datetimes[i].month for i in range(len(df['Timestamp']))])
    day = np.array([datetimes[i].day for i in range(len(df['Timestamp']))])
    hour = np.array([datetimes[i].hour for i in range(len(df['Timestamp']))])
    minute = np.array([datetimes[i].minute for i in range(len(df['Timestamp']))])
    second = np.array([datetimes[i].second for i in range(len(df['Timestamp']))])
    day_of_year = np.array([datetimes[i].timetuple().tm_yday for i in range(len(df['Timestamp']))])  # a.timetuple().tm_yday
    
    # data aren't recorded exactly equally spaced apart,
    # so we take mean
    # this doesn't work if there's missing data!!!!!
    tdeltas = []
    for i in range(len(df['Timestamp'])-1):
        tdeltas.append(datetimes[i+1] - datetimes[i])
    # take mean of middle values, avoids outliers...
    tdmean = np.mean(sorted(tdeltas[int(len(tdeltas)/4):int(3*len(tdeltas)/4)]))
    tdmean_round = round(tdmean.total_seconds(),4)
    
    all_data = {'air_pressure': np.array(df['Pa'].astype(np.float32)),
                'air_temperature': np.array(df['Ta'].astype(np.float32)),
                'relative_humidity': np.array(df['Ua'].astype(np.float32)),
                'wind_speed': np.array(df['Sm'].astype(np.float32)),
                'wind_from_direction': np.array(df['Dm'].astype(np.float32)),
                'thickness_of_rainfall_amount': np.array(df['Rc'].astype(np.float32)),
                'rainfall_rate': np.array(df['Ri'].astype(np.float32)),
                'hail_intensity': np.array(df['Hc'].astype(np.float32)),
                'hail_rate': np.array(df['Hi'].astype(np.float32)),
                'time': unix_time,
                'year': year,
                'month': month,
                'day': day,
                'hour': hour,
                'minute': minute,
                'second': second,
                'day_of_year': day_of_year
                
               }
    
    all_attrs = {'sampling_interval': f'{tdmean_round} seconds'
                }
    
    return all_data, all_attrs



def aws_to_csv(infile, outfile):
    """
    From Dan, aws-to-csv.py
    Reads data from automatic weather station and outputs to nice csv.
    Can be run at any time with live data.
    
    2022-03-04 - added in check for units
    2022-03-07 - added conversion to K for Air Temp
    
    Args:
        infile (str): File path and name of csv data written directly by weather station.
        outfile (str): File path and name of csv data to be written by this function.
        
    """
    fields = ['Timestamp','Dn','Dm','Dx','Sn','Sm','Sx','Ta','Tp','Ua','Pa','Rc','Rd','Ri','Hc','Hd','Hi','Rp','Hp','Th','Vh','Vs','Vr','Id']
    units = ['0','D','D','D','M','M','M','C','C','P','H','M','s','M','M','s','M','M','M','C','V','V','V','0']
    data = []
    
    with open(infile, 'r') as f:
        indata = csv.reader(f)
        for line in indata:
            out ={'Timestamp':line[0]}
            #discard line[1], it's just a start-of-data indicator
            for datum in line[2:]:
                details = datum.split('=')
                #values are suffixed with a single character unit
                #check unit is right
                if details[1][-1] == units[fields.index(details[0])]:
                    # correct units
                    pass
                elif details[0] in ['Timestamp', 'Id']:
                    # these are unitless
                    pass
                elif details[0] in ['Vh']:
                    # this is awkward, and I don't really care
                    pass
                else:
                    # one day put together some sort of conversion
                    print(f'Incorrect unit {details[1][-1]} for field {details[0]}')
                if details[0] == 'Ta':
                    # Convert to K
                    if details[1][-1] == 'C':
                        out[details[0]] = float(details[1][:-1]) + 273.15
                    elif details[1]-[-1] == 'F':
                        out[details[0]] = (float(details[1][:-1]) + 459.67) * (5/9)
                    else:
                        print(f'Very unexpected unit for Air Temp: {details[1][-1]}')
                else:
                    out[details[0]] = details[1][:-1]
                if details[0] == 'Id':
                    out[details[0]] = details[1]
            data.append(out)
    
               
        with open(outfile, 'w') as g:
            outdata = csv.DictWriter(g,fields)
            outdata.writeheader()
            outdata.writerows(data)
