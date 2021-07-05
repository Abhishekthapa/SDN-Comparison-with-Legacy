# How To Run

#setup and step by step procedure:
1. Install a SDN IP VM from ONOS's website.
2. Run VM and reset the application.
3. Open terminal and go to the folder containing topology file.
4. Run the topology.
5. Open ONOS and run the ONOS applications: config, proxyarp ,sdn ip and sdn ip reactive routing
6. PING the hosts in the terminal where the topology was run.
7.  Use DITG and iperf application to gather further data.

For Legacy setup, just run legacy.py file and do ping DITG and iperf operation.
In the datasets folder, 'legacy_data' and 'sdn_data' folders contain output of PING and 
'sdn_dataset.csv' file contains output of DITG obtained from our experiment.
