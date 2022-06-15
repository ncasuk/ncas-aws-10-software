import pandas as pd
import csv


def aws_to_csv(infile):
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
            
    return pd.DataFrame(data)
    
    
if __name__ == "__main__":
    import sys
    aws_to_csv(sys.argv[1])