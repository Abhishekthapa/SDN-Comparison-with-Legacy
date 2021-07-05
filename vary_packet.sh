#!/bin/bash

#Bash script to test ping between hosts
#dest=$1
#if [[ $# -ne 4 ]] 
#then
#   echo "Usage : vary_packet.sh <destination_IP> <folder_name> <file_name> <sdn/legacy>"
#   echo "****************************"
#   echo "Destination_ip is the Ip to ping"
#   echo "folder_name convention is to use two hosts being pinged , h1_h2 , where h1 is source, h2 is destination"
#   echo "file_name is the file_name to be saved under"
#   echo "sdn/legacy to differentiate"
#   exit 2
#fi

h2="10.100.200.2"
h1="10.100.100.2"
h3="192.168.3.10"
h4="192.168.4.10"

file_name="default"

ips=("10.100.200.2" "10.100.100.2" "192.168.3.10" "192.168.4.10")

my_ip=$(ifconfig | grep "Bcast" | cut -f ':' -f 2 | cut -d ' ' -f 1)
my_host=$(ifconfig | head -n 1 | cut -d '-' -f 1)

network_type="sdn"
for j in {1..5}
do
for ip in ${ips[@]}
do
	if [[ $ip != my_ip ]] 
		then	
			if [[ $ip == $h1 ]]
			then	
				file_name="${my_host}_h1"
			elif [[ $ip == $h2 ]]
			then
				file_name="${my_host}_h2"
			elif [[ $ip == $h3 ]]
			then
				file_name="${my_host}_h3"
			elif [[ $ip == $h4 ]]
			then
				file_name="${my_host}_h4"

			fi
		 
			for i in $(seq 5 5 100)
			do
				mkdir -p ./${network_type}_data/ping/$file_name
			  	mdevrtt=$(ping $ip -c $i | tee ./${network_type}_data/ping/$file_name/${file_name}_${i}_${j} | grep "mdev" | cut -d '/' -f 7 | cut -d " " -f 1)
			  date=$(date)
			  echo "$date $network_type $file_name $i : $mdevrtt" >> rtt_data
			  tail -n 1 rtt_data 

			done
	fi
done
done
