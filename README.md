# ncas-aws-10-software

Code for creating AMOF-compliant netCDF files for ncas-aws-10 instrument.


## Requirements
* python 3.7 or above
* modules:
  * numpy
  * pandas
  * datetime
  * netCDF4
  * [ncas-amof-netcdf-template]


## Installation

Clone the git repo
```
git clone https://github.com/ncasuk/ncas-aws-10-software.git
```

Install required modules using `pip install -r requirements.txt` or `conda install --file requirements.txt`


## Usage

```
python process_aws.py /path/to/datafile.csv -m metadata.csv
```
where `metadata.csv` includes additional metadata for the netCDF file.

Additional flags that can be given for each python script:
* `-o` or `--ncfile-location` - where to write the netCDF files to. If not given, default is `'.'`
* `-v` or `--verbose` - print additional information as the script runs

A description of all the available options can be obtained using the `-h` flag, for example
```
python process_aws.py -h
```

### BASH scripts

Three [scripts] are provided for easy use:
* `make_netcdf.sh` - makes netCDF file for a given date: `./make_netcdf.sh YYYYmmdd`
* `make_today_netcdf.sh` - makes netCDF file for today's data: `./make_today_netcdf.sh`
* `make_yesterday_netcdf.sh` - makes netCDF file for yesterday's data: `./make_yesterday_netcdf.sh`

Within `make_netcdf.sh`, the following may need adjusting:
* `netcdf_path="/gws/..."`: replace file path with where to write netCDF files.
* `datapath="/gws/..."`: replace file path with path to data.
* `metadata_file="${SCRIPT_DIR}/../metadata.csv`: replace if using different metadata file.
* `logfilepath=/home...`: replace with path of where to write logs

[scripts]: scripts
[ncas-amof-netcdf-template]: https://ncas-amof-netcdf-template.readthedocs.io/en/stable

## Further Information
* `read_aws.py` contains the code that actually reads the raw data. This is called from within `process_aws.py`
* `basic_qc_aws.py` returns qc values based on the instrument's designed operating range. This is called from within `process_aws.py`

