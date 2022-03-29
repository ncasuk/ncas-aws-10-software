"""
Functions for checking data against operational range of instrument and creating qc flag variables.

"""

import numpy as np


ranges = {'air_pressure': {'min': 500,
                           'max': 1100,
                           'units': 'hPa',
                           'qc_name': 'qc_flag_pressure'
                          },
          'air_temperature': {'min': 221.15,
                              'max': 333.15,
                              'units': 'K',
                              'qc_name': 'qc_flag_temperature'
                             },
          'relative_humidity': {'min': 0,
                                'max': 100,
                                'units': '%',
                                'qc_name': 'qc_flag_relative_humidity'
                               },
          'wind_speed': {'min': 0.01,  # actually the min is 0, but different flag for 0
                         'max': 60,   # check this
                         'units': 'm/s',
                         'qc_name': 'qc_flag_wind_speed'
                        },
          'wind_from_direction': {'min': 0,
                                  'max': 360,
                                  'units': 'degrees',
                                  'qc_name': 'qc_flag_wind_from_direction'
                                 },
          'rainfall_rate': {'min': 0,
                            'max': 200,
                            'units': 'mm/hr',
                            'qc_name': 'qc_flag_precipitation'
                           }
         }



def check_valid(data, ranges=ranges, verbose=0):
    """
    Performs basic quality control on weather station data based on manufacturer-stated measurement ranges.
    
    Args:
        data (dict): Dictionary of data to check against operational range, keys should be variable names in netCDF file.
        ranges (dict): Optional. Dictionary of min and max values, and qc flag name, for each variable. Default as defined in :py:func:`basic_qc`
        verbose (any): If truthy, prints variables in ``data`` for which no qc is available.
        
    Returns:
        dict: Dictionary of qc_flag data
        
    """
    qc_flags = {}
    for variable in data.keys():
        if variable in ranges.keys():
            if 'wind' not in variable:
                data_flatten = data[variable].flatten()
                qc = np.ones(len(data_flatten))
                for i, datum in enumerate(data_flatten):
                    if datum < ranges[variable]['min'] or datum > ranges[variable]['max']:
                        qc[i] = 2
                qc = qc.reshape(data[variable].shape)
                qc_flags[ranges[variable]['qc_name']] = qc
            elif variable == 'wind_speed':
                data_flatten = data[variable].flatten()
                qc = np.ones(len(data_flatten))
                for i, datum in enumerate(data_flatten):
                    if datum == 0:
                        qc[i] = 2
                    elif datum < ranges[variable]['min'] or datum > ranges[variable]['max']:
                        qc[i] = 3
                qc = qc.reshape(data[variable].shape)
                qc_flags[ranges[variable]['qc_name']] = qc
            elif variable == 'wind_from_direction':
                data_flatten = data[variable].flatten()
                speed_flatten = data['wind_speed'].flatten()
                qc = np.ones(len(data_flatten))
                for i, datum in enumerate(data_flatten):
                    if speed_flatten[i] == 0:
                        qc[i] = 2
                    elif datum < ranges[variable]['min'] or datum > ranges[variable]['max']:
                        qc[i] = 3
                qc = qc.reshape(data[variable].shape)
                qc_flags[ranges[variable]['qc_name']] = qc
            else:
                print(f'Oops, not sure how we got here, variable {variable}')
        elif verbose:
            print(f'No qc flag available for variable {variable}, continuing...')
    return qc_flags
            
