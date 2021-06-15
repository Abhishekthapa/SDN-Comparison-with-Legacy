#!/bin/bash

#Bash script to test ping between hosts
dest=$1
if [[ $# -ne 3 ]] 
then
   echo "Usage : h1_ping.sh <destination_IP> <folder_name> <file_name>"
   exit 2
fi
for i in 5 10 20 30 50 100
do
  if [ ! -d ./legacy_data/ping/$2 ]
  then
	mkdir ./legacy_data/ping/$2
  fi
  ping $dest -c $i | tee ./legacy_data/ping/$2/$3_$i
done
