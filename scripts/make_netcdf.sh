#!/bin/bash

#
# ./make_netcdf.sh YYYYmmdd
#

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

netcdf_path="/gws/nopw/j04/ncas_obs/iao/processing/ncas-aws-10/netcdf_files"
datapath="/gws/nopw/j04/ncas_obs/iao/raw_data/ncas-aws-10/incoming"
logfilepath="/home/users/earjham/logs/na10logs"
metadata_file=${SCRIPT_DIR}/../metadata.csv


datadate=$1  # YYYYmmdd

python ${SCRIPT_DIR}/../process_aws.py ${datapath}/${datadate}_vaisala.csv -m ${metadata_file} -o ${netcdf_path}

if [ -f ${netcdf_path}/ncas-aws-10_iao_${year}${month}${day}_surface-met_*.nc ]
then 
  aws_file_exists=True
else
  aws_file_exists=False
fi

cat << EOF | sed -e 's/#.*//; s/  *$//' > ${logfilepath}/${year}${month}${day}.txt
Date: $(date -u)
AWS file created: ${aws_file_exists}
EOF
