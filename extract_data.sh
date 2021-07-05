#!/bin/bash

# extracts the data by averaging from the rtt_data file
# usage: extract_data.sh <h1_h2>

#!/bin/bash

RTT_FILE=rtt_data
get_data()
{
        count=$(grep "$1 $2 :" $RTT_FILE | wc -l)
        python3 -c "print((`cat $RTT_FILE | grep "$1 $2 :" | cut -d ' ' -f 12 | tr '\n' '+'`0)/$count)"
}

for i in 5 10 20 30 50 100
do
        get_data $1 $i
done
