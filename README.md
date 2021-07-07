In this project,we  compare the network performance of the legacy network with SDN for IP routing in order to determine the feasibility of an SDN deployment for the Internet service provider (ISP) network. The simulation of the network is performed in the Mininet test-bed and the network traffic is generated using distributed Internet traffic generator. Round trip time, bandwidth, and packet transmission rate from both of these networks are first collected and then the comparison is done. We found that SDN-IP provides better bandwidth and latency compared to legacy routing. The experimental analysis of interoperability between SDN and legacy network shows that SDN implementation in production level carrier-grade ISP network is viable and progressive.

# Tools
* Mininet Simulation Environment ( 2.2.1 )
* ONOS 1.2.1 ( SDN Controller )
* Quagga Routing Suite ( 0.99.23 )
* Ubuntu 14.10 ( 64-bit )
* Hypervisor : VirtualBox ( 2 core, 4096 MB )
* DITG , PING , IPERF ( Data Collection )
* Matplotlib ( Visualization and Analysis )



# Running The Code

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
