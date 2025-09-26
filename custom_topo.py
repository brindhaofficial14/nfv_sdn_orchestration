from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink

class NFVTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        fw = self.addHost('fw', ip='10.0.0.3')
        dpi = self.addHost('dpi', ip='10.0.0.4')
        nat = self.addHost('nat', ip='10.0.0.5')
        s1 = self.addSwitch('s1')
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(fw, s1)
        self.addLink(dpi, s1)
        self.addLink(nat, s1)

if __name__ == '__main__':
    net = Mininet(topo=NFVTopo(), controller=RemoteController, switch=OVSSwitch, link=TCLink)
    net.start()
    CLI(net)
    net.stop()
