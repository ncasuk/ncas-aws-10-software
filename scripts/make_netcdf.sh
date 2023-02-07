#!/bin/bash

#
# ./make_netcdf.sh YYYYmmdd
#

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

gws_path=/gws/pw/j07/ncas_obs_vol1

netcdf_path=${gws_path}/iao/processing/ncas-aws-10/netcdf_files
datapath=${gws_path}/iao/raw_data/ncas-aws-10/incoming
logfilepath=${gws_path}/iao/logs/ncas-aws-10

metadata_file=${SCRIPT_DIR}/../metadata.csv

datadate=$1  # YYYYmmdd
conda_env=${2:-netcdf}

conda activate ${conda_env}

python ${SCRIPT_DIR}/../process_aws.py ${datapath}/${datadate}_vaisala.csv -m ${metadata_file} -o ${netcdf_path} -v

if [ -f ${netcdf_path}/ncas-aws-10_iao_${datadate}_surface-met_*.nc ]
then 
  aws_file_exists=True
else
  aws_file_exists=False
fi

cat << EOF | sed -e 's/#.*//; s/  *$//' > ${logfilepath}/${datadate}.txt
Date: $(date -u)
AWS file created: ${aws_file_exists}
EOF
