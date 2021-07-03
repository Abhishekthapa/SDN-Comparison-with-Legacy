#!/bin/bash

#Bash script to test ping between hosts
dest=$1
if [[ $# -ne 3 ]] 
then
   echo "Usage : vary_packet.sh <destination_IP> <folder_name> <file_name>"
   exit 2
fi
for i in $(seq 5 5 100)
do
  if [ ! -d ./legacy_data/ping/$2 ]
  then
	mkdir -p ./legacy_data/ping/$2
  fi
  
  mdevrtt=$(ping $dest -c $i | tee ./legacy_data/ping/$2/$3_$i | grep "mdev" | cut -d '/' -f 7 | cut -d " " -f 1)
  date=$(date)
  echo "$date $2 $i : $mdevrtt" >> rtt_data
  tail -n 1 rtt_data 

done
