#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info, debug
from mininet.node import Host, RemoteController

QUAGGA_DIR = '/usr/lib/quagga'
# Must exist and be owned by quagga user (quagga:quagga by default on Ubuntu)
QUAGGA_RUN_DIR = '/var/run/quagga'
CONFIG_DIR = 'configs'

class SdnIpHost(Host):
    def __init__(self, name, ip, route, *args, **kwargs):
        Host.__init__(self, name, ip=ip, *args, **kwargs)

        self.route = route

    def config(self, **kwargs):
        Host.config(self, **kwargs)

        debug("configuring route %s" % self.route)

        self.cmd('ip route add default via %s' % self.route)

class Router(Host):
    def __init__(self, name, quaggaConfFile, zebraConfFile, intfDict, *args, **kwargs):
        Host.__init__(self, name, *args, **kwargs)

        self.quaggaConfFile = quaggaConfFile
        self.zebraConfFile = zebraConfFile
        self.intfDict = intfDict

    def config(self, **kwargs):
        Host.config(self, **kwargs)
        self.cmd('sysctl net.ipv4.ip_forward=1')

        for intf, attrs in self.intfDict.items():
            self.cmd('ip addr flush dev %s' % intf)
            if 'mac' in attrs:
                self.cmd('ip link set %s down' % intf)
                self.cmd('ip link set %s address %s' % (intf, attrs['mac']))
                self.cmd('ip link set %s up ' % intf)
            for addr in attrs['ipAddrs']:
                self.cmd('ip addr add %s dev %s' % (addr, intf))

        self.cmd('/usr/lib/quagga/zebra -d -f %s -z %s/zebra%s.api -i %s/zebra%s.pid' % (self.zebraConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
        self.cmd('/usr/lib/quagga/bgpd -d -f %s -z %s/zebra%s.api -i %s/bgpd%s.pid' % (self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))


    def terminate(self):
        self.cmd("ps ax | egrep 'bgpd%s.pid|zebra%s.pid' | awk '{print $1}' | xargs kill" % (self.name, self.name))

        Host.terminate(self)


class SdnIpTopo( Topo ):
    "SDN-IP tutorial topology"
    
    def build( self ):
        s1 = self.addSwitch('s1', dpid='00000000000000a1')
        s2 = self.addSwitch('s2', dpid='00000000000000a2')
        s3 = self.addSwitch('s3', dpid='00000000000000a3')
        s4 = self.addSwitch('s4', dpid='00000000000000a4')
        s5 = self.addSwitch('s5', dpid='00000000000000a5')
        s6 = self.addSwitch('s6', dpid='00000000000000a6')

        zebraConf = '%s/zebra.conf' % CONFIG_DIR

        # Switches we want to attach our routers to, in the correct order
        attachmentSwitches = [s1, s2]

        for i in range(1, 3):
            name = 'r%s' % i

            eth0 = { 'mac' : '00:00:00:00:0%s:01' % i,
                     'ipAddrs' : ['10.0.%s.1/24' % i] }
	    if i < 2:
            	eth1 = { 'ipAddrs' : ['10.100.100.254/24'] }
	    else:
	    	eth1 = { 'ipAddrs' : ['10.100.200.254/24'] }
            intfs = { '%s-eth0' % name : eth0,
                      '%s-eth1' % name : eth1 }

            quaggaConf = '%s/quagga%s.conf' % (CONFIG_DIR, i)

            router = self.addHost(name, cls=Router, quaggaConfFile=quaggaConf,
                                  zebraConfFile=zebraConf, intfDict=intfs)
            if i < 2:
            	host = self.addHost('h%s' % i, cls=SdnIpHost, 
                                	ip='10.100.100.2/24',
                                	route='10.100.100.254')
	    else:
 	   	host = self.addHost('h%s' % i, cls=SdnIpHost, 
                                ip='10.100.200.2/24',
                                route='10.100.200.254')
            
            self.addLink(router, attachmentSwitches[i-1])
            self.addLink(router, host)

        # Set up the internal BGP speaker
        bgpEth0 = { 'mac':'00:00:00:00:00:01', 
                    'ipAddrs' : ['10.0.1.101/24',
                                 '10.0.2.101/24',
                                 ] }
        bgpEth1 = { 'ipAddrs' : ['10.10.10.1/24'] }
        bgpIntfs = { 'bgp-eth0' : bgpEth0,
                     'bgp-eth1' : bgpEth1 }
        
        bgp = self.addHost( "bgp", cls=Router, 
                             quaggaConfFile = '%s/quagga-sdn.conf' % CONFIG_DIR, 
                             zebraConfFile = zebraConf, 
                             intfDict=bgpIntfs )
        
        self.addLink( bgp, s3 )

        # Connect BGP speaker to the root namespace so it can peer with ONOS
        root = self.addHost( 'root', inNamespace=False, ip='10.10.10.2/24' )
        self.addLink( root, bgp )


        # Wire up the switches in the topology
        self.addLink( s1, s2 )
        self.addLink( s1, s3 )
        self.addLink( s2, s4 )
        self.addLink( s3, s4 )
        self.addLink( s3, s5 )
        self.addLink( s4, s6 )
        self.addLink( s5, s6 )


        netWorkHostH1 = self.addHost('nh1',cls=SdnIpHost,ip='10.0.10.22/24',route='10.0.10.254')
        netWorkHostH2 = self.addHost('nh2',cls=SdnIpHost,ip='10.0.10.23/24',route='10.0.10.254')
        netWorkHostH3 = self.addHost('nh3',cls=SdnIpHost,ip='10.0.10.101/24',route='10.0.10.254')
        #netWorkHostH4 = self.addHost('nh4',cls=SdnIpHost,ip='10.0.10.42/24',route='10.0.10.254')

        self.addLink(netWorkHostH1,s3)
        self.addLink(netWorkHostH2,s4)
        self.addLink(netWorkHostH3,s5)
        #self.addLink(netWorkHostH4,s6)
        
        privateHostH1 = self.addHost('ph1',cls=SdnIpHost,ip='192.168.1.22/24',route='192.168.1.254')
        privateHostH2 = self.addHost('ph2',cls=SdnIpHost,ip='192.168.1.23/24',route='192.168.1.254')
        privateHostH3 = self.addHost('ph3',cls=SdnIpHost,ip='192.168.1.101/24',route='192.168.1.254')
        #privateHostH4 = self.addHost('ph4',cls=SdnIpHost,ip='192.168.1.42/24',route='192.168.1.254')

        self.addLink(privateHostH1,s1)
        self.addLink(privateHostH2,s2)
        self.addLink(privateHostH3,s3)
        #self.addLink(privateHostH4,s6)

	
        subnetHostH3 = self.addHost('h3',cls=SdnIpHost,ip='192.168.3.10/24',route='192.168.3.254')
        subnetHostH4 = self.addHost('h4',cls=SdnIpHost,ip='192.168.4.10/24',route='192.168.4.254')
	self.addLink(subnetHostH3,s4)
        self.addLink(subnetHostH4,s5)

topos = { 'sdnip' : SdnIpTopo }

if __name__ == '__main__':
    setLogLevel('debug')
    topo = SdnIpTopo()

    net = Mininet(topo=topo, controller=RemoteController)

    net.start()

    CLI(net)

    net.stop()

    info("done\n")
