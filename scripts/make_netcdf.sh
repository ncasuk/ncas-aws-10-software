#!/bin/bash

#
# ./make_netcdf.sh YYYYmmdd
#

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

netcdf_path="/gws/nopw/j04/ncas_obs/iao/processing/ncas-aws-10/netcdf_files"
datapath="/gws/nopw/j04/ncas_obs/iao/raw_data/ncas-aws-10/incoming"
metadata_file=${SCRIPT_DIR}/../metadata.csv


datadate=$1  # YYYYmmdd

python ${SCRIPT_DIR}/../process_aws.py ${datapath}/${datadate}_vaisala.csv -m ${metadata_file} -o ${netcdf_path}
