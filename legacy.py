#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info, debug
from mininet.node import Host, RemoteController

QUAGGA_DIR = '/usr/lib/quagga'
# Must exist and be owned by quagga user (quagga:quagga by default on Ubuntu)
QUAGGA_RUN_DIR = '/var/run/quagga'
CONFIG_DIR = 'configslegacy'

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
	if self.name == 'r3':
            self.cmd('/usr/lib/quagga/ospfd -d -f configslegacy/ospfd3.conf -z /var/run/quagga/zebrar3.api -i /var/run/quagga/ospfdr3.pid')
        elif self.name =='r4':
            self.cmd('/usr/lib/quagga/ospfd -d -f configslegacy/ospfd4.conf -z /var/run/quagga/zebrar4.api -i /var/run/quagga/ospfdr4.pid')
        elif self.name =='r5':
            self.cmd('/usr/lib/quagga/ospfd -d -f configslegacy/ospfd5.conf -z /var/run/quagga/zebrar5.api -i /var/run/quagga/ospfdr5.pid')
	elif self.name == 'r6':
            self.cmd('/usr/lib/quagga/ospfd -d -f configslegacy/ospfd6.conf -z /var/run/quagga/zebrar6.api -i /var/run/quagga/ospfdr6.pid')
        elif self.name =='r7':
            self.cmd('/usr/lib/quagga/ospfd -d -f configslegacy/ospfd7.conf -z /var/run/quagga/zebrar7.api -i /var/run/quagga/ospfdr7.pid')
        elif self.name =='r8':
            self.cmd('/usr/lib/quagga/ospfd -d -f configslegacy/ospfd8.conf -z /var/run/quagga/zebrar8.api -i /var/run/quagga/ospfdr8.pid')
    def terminate(self):
        self.cmd("ps ax | egrep 'bgpd%s.pid|zebra%s.pid' | awk '{print $1}' | xargs kill" % (self.name, self.name))
	self.cmd("ps ax | egrep 'ospfd%s.pid|zebra%s.pid' | awk '{print $1}' | xargs kill" % (self.name, self.name))
	#for ospf we need to add another cmd 
        Host.terminate(self)


class LegacyTopo( Topo ):
    "legacy tutorial topology"

    def createInterface(self,number,mac,ips):
	"""Returns router """

	zebraConf = '%s/zebra.conf' % CONFIG_DIR
	intfs = {}
        name = 'r'+str(number)
	for i in range(len(ips)):
	    if i==0:
	        eth = { 'mac': mac, 'ipAddrs' : [ips[i]]}
	    else:
		eth = { 'ipAddrs' : [ips[i]]}
	    interface_name = name +'-eth'+str(i)
	    intfs[interface_name] = eth

	quaggaConf = '%s/quagga%s.conf' % (CONFIG_DIR,number)
	
	router = self.addHost(name, cls=Router, quaggaConfFile=quaggaConf, zebraConfFile=zebraConf, intfDict=intfs)
	return router
	
    
    def build( self ):
        r1 = self.createInterface(1,'00:00:00:00:01:01',["192.168.1.254/24","10.0.100.1/30"])
        host1 = self.addHost('h1' , cls=SdnIpHost, 
	                                ip='192.168.1.1/24' ,
	                                route='192.168.1.254')
        self.addLink(r1, host1)
        r2= self.createInterface(2,'00:00:00:00:02:01',['192.168.2.254/24','10.0.100.10/30'])
	            
	host2 = self.addHost('h2' , cls=SdnIpHost, 
	                                ip='192.168.2.1/24',
	                                route='192.168.2.254' )
        self.addLink(r2, host2)
	    
        r3 = self.createInterface(3,'00:00:00:00:03:01',["192.168.3.254/24","10.0.100.2/30","10.0.100.14/30"])
        host3 = self.addHost('h3' , cls=SdnIpHost, 
	                                ip='192.168.3.1/24',
	                                route='192.168.3.254' )
        self.addLink(r3,host3)
        self.addLink(r1,r3)
        r4 = self.createInterface(4,'00:00:00:00:04:01',["192.168.4.254/24","10.0.100.6/30","10.0.100.9/30"])
        host4 = self.addHost('h4' , cls=SdnIpHost, 
	                                ip='192.168.4.1/24',
	                                route='192.168.4.254' )
        self.addLink(r4,host4)
        
        r5= self.createInterface(5,'00:00:00:00:05:01',['192.168.5.254/24','10.0.100.5/30','10.0.100.13/30','10.0.100.17/30','10.0.100.21/30','10.0.100.25/30'])
	            
	host5 = self.addHost('h5' , cls=SdnIpHost, 
	                                ip='192.168.5.1/24',
	                                route='192.168.5.254' )
        self.addLink(r5, host5)
        self.addLink(r4,r5)
        self.addLink(r2,r4)
        self.addLink(r5,r3)
        r6= self.createInterface(6,'00:00:00:00:06:01',['192.168.6.254/24','10.0.100.26/30'])
	            
	host6 = self.addHost('h6' , cls=SdnIpHost, 
	                                ip='192.168.6.1/24',
	                                route='192.168.6.254' )
        self.addLink(r6, host6)

        r7= self.createInterface(7,'00:00:00:00:07:01',['192.168.7.254/24','10.0.100.22/30'])
	            
	host7 = self.addHost('h7' , cls=SdnIpHost, 
	                                ip='192.168.7.1/24',
	                                route='192.168.7.254' )
        self.addLink(r7, host7)

        r8= self.createInterface(8,'00:00:00:00:08:01',['192.168.8.254/24','10.0.100.18/30'])
	            
	host8 = self.addHost('h8' , cls=SdnIpHost, 
	                                ip='192.168.8.1/24',
	                                route='192.168.8.254' )
        self.addLink(r8, host8)
        self.addLink(r8, r5)
        self.addLink(r7, r5)
        self.addLink(r6, r5)


topos = { 'legacy' : LegacyTopo }

if __name__ == '__main__':
    setLogLevel('debug')
    topo = LegacyTopo()

    net = Mininet(topo=topo)

    net.start()

    CLI(net)

    net.stop()

    info("done\n")
