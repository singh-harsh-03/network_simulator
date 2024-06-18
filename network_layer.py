import heapq


class Router:
    def __init__(self, router_id):
        self.router_id = router_id
        self.interfaces = {}  # Dictionary to store interface information
        self.routing_table = {}  # Routing table to store network layer routing information
        self.neighbors = {}  # Dictionary to store neighboring routers and their interfaces
        self.routing_updates = []  # List to store received routing updates

    def add_interface(self, interface_name, ip_address, subnet_mask):
        """
        Add an interface to the router.
        """
        self.interfaces[interface_name] = {'ip_address': ip_address, 'subnet_mask': subnet_mask}

    def configure_routing_table(self, destination_network, next_hop, interface, subnet_mask):
        """
        Configure the routing table of the router.
        """
        self.routing_table[destination_network] = {
            'next_hop': next_hop,
            'interface': interface,
            'subnet_mask': subnet_mask
        }

    def forward_packet(self, packet):
        """
        Forward a packet based on the routing table using the longest mask matching.
        """
        destination_ip = packet['destination_ip']
        matching_routes = [
            (net, info) for net, info in self.routing_table.items()
            if self.ip_in_subnet(destination_ip, net, info['subnet_mask'])
        ]
        if matching_routes:
            longest_match = max(matching_routes, key=lambda x: self.mask_length(x[1]['subnet_mask']))
            next_hop = longest_match[1]['next_hop']
            outgoing_interface = longest_match[1]['interface']
            print(f"Forwarding packet to {destination_ip} via {next_hop} on interface {outgoing_interface}")
            # Here you can implement the actual packet forwarding mechanism
        else:
            print(f"No route found for destination {destination_ip}")

    def receive_packet(self, packet):
        """
        Receive a packet and process it.
        """
        destination_ip = packet['destination_ip']
        if any(self.ip_in_subnet(destination_ip, iface['ip_address'], iface['subnet_mask']) for iface in self.interfaces.values()):
            print(f"Packet for {destination_ip} received by router {self.router_id}")
            # Here you can implement processing of incoming packets
        else:
            print(f"Packet received by router {self.router_id} is not for any of its interfaces")

    def add_static_route(self, destination_network, next_hop, interface, subnet_mask):
        """
        Add a static route to the routing table of the router.
        """
        self.configure_routing_table(destination_network, next_hop, interface, subnet_mask)

    def ip_in_subnet(self, ip, network, subnet_mask):
        """
        Check if an IP address is in a given subnet.
        """
        ip_parts = ip.split('/')
        ip_address=ip_parts[0]
        subnet_length = ip_parts[1] if len(ip_parts) > 1 else '32'
        ip_bin = self.ip_to_bin(ip_address)
        network_bin = self.ip_to_bin(network)
        subnet_bin = '1' * int(subnet_length) + '0' * (32 - int(subnet_length))
        return ip_bin[:int(subnet_length)] == network_bin[:int(subnet_length)]

    def ip_to_bin(self, ip):
        """
        Convert an IP address to its binary representation.
        """
        return ''.join(f'{int(octet):08b}' for octet in ip.split('.'))

    def mask_length(self, subnet_mask):
        """
        Calculate the length of the subnet mask.
        """
        return sum(bin(int(octet)).count('1') for octet in subnet_mask.split('.'))

    def compute_shortest_path(self, graph, start):
        """
        Compute shortest paths using Dijkstra's algorithm.
        """
        queue = [(0, start, [])]
        seen = set()
        min_dist = {start: 0}
        while queue:
            (cost, v1, path) = heapq.heappop(queue)
            if v1 in seen:
                continue
            seen.add(v1)
            path = path + [v1]
            for v2, weight in graph.get(v1, {}).items():
                if v2 in seen:
                    continue
                prev = min_dist.get(v2, None)
                next = cost + weight
                if prev is None or next < prev:
                    min_dist[v2] = next
                    heapq.heappush(queue, (next, v2, path))
        return min_dist

class IPv4Address:
    def __init__(self, address, subnet_mask):
        self.address = address
        self.subnet_mask = subnet_mask

class Network:
    def __init__(self, network_address, subnet_mask):
        self.network_address = network_address
        self.subnet_mask = subnet_mask
        self.devices = []

    def assign_ip_address(self, device):
        """
        Assign an IPv4 address to a device within the network.
        """
        # Increment the host part of the network address for each device
        host_address = len(self.devices) + 1  # Increment for each new device
        ip_address = f"{self.network_address}.{host_address}"
        device.ip_address = ip_address
        device.network = self
        self.devices.append(device)

    def broadcast_arp_response(self, target_ip, target_mac, sender_ip):
        """
        Broadcast an ARP response to all devices in the network.
        """
        for device in self.devices:
            if device.ip_address == target_ip:
                # Simulate receiving the ARP response
                device.receive_arp_response(sender_ip, target_mac)
                

import random

class Device:
    def __init__(self, name):
        self.name = name
        self.ip_address = None
        self.mac_address = None
        self.network = None

    def send_arp_request(self, ip_address):
        """
        Simulate sending an ARP request to resolve the MAC address for the given IP address.
        """
        if self.network:
            # Send ARP request to all devices in the network
            for device in self.network.devices:
                if device.ip_address == ip_address:
                    # Simulate receiving an ARP request
                    device.receive_arp_request(self.ip_address)

    def receive_arp_request(self, sender_ip):
        """
        Simulate receiving an ARP request and send a response.
        """
        if self.network:
            # Simulate sending an ARP response
            self.network.broadcast_arp_response(self.ip_address, self.mac_address, sender_ip)

    def receive_arp_response(self, ip_address, mac_address):
        """
        Receive an ARP response containing the MAC address.
        """
        print(f"{self.name} received ARP response: IP - {ip_address}, MAC - {mac_address}")
        self.mac_address = mac_address
        

# Example usage:
# Create a router instance
router1 = Router("Router1")

# Add interfaces to the router
router1.add_interface("eth0", "192.168.1.1", "255.255.255.0")  # Add interface eth0 with IP address 192.168.1.1 and subnet mask 255.255.255.0
router1.add_interface("eth1", "10.0.0.1", "255.255.255.0")     # Add interface eth1 with IP address 10.0.0.1 and subnet mask 255.255.255.0

# Configure the routing table for the router
#static routing
router1.configure_routing_table("192.168.2.0", "192.168.1.2", "eth0", "255.255.255.0")  # Configure routing for network 192.168.2.0 to use next hop 192.168.1.2 via interface eth0
router1.configure_routing_table("10.1.0.0", "10.0.0.2", "eth1", "255.255.0.0")       # Configure routing for network 10.1.0.0 to use next hop 10.0.0.2 via interface eth1

# Simulate forwarding a packet to destination IP 192.168.2.10
packet = {'destination_ip': "192.168.2.10"}
router1.forward_packet(packet)  # Router forwards the packet to the appropriate next hop based on the routing table

# Simulate receiving a packet destined for IP 192.168.1.1
received_packet = {'destination_ip': "192.168.1.1"}  # Packet received on eth0 interface
router1.receive_packet(received_packet)  # Router processes the received packet

# Example usage:
# Create devices
device1 = Device("Device1")  # Create device named Device1
device2 = Device("Device2")  # Create device named Device2

# Create a network with a subnet
network = Network("192.168.1.0", "255.255.255.0")  # Create a network with network address 192.168.1.0 and subnet mask 255.255.255.0

# Assign IP addresses to devices within the network
network.assign_ip_address(device1)  # Assign an IP address to Device1 within the network
network.assign_ip_address(device2)  # Assign an IP address to Device2 within the network

# Print assigned IP addresses and subnet mask for devices
print(f"{device1.name} IP Address: {device1.ip_address} / Subnet Mask: {network.subnet_mask}")
print(f"{device2.name} IP Address: {device2.ip_address} / Subnet Mask: {network.subnet_mask}")

# Simulate ARP request from Device1 to resolve the MAC address of Device2
print(f"{device1.name} is sending an ARP request to resolve the MAC address of {device2.name}...")
device1.send_arp_request(device2.ip_address)  # Device1 sends an ARP request to resolve the MAC address of Device2

# Simulate ARP response from Device2 to Device1
print(f"{device2.name} is sending an ARP response to {device1.name}...")
device2.receive_arp_response(device1.ip_address, "00:11:22:33:44:55")  # Device2 responds to the ARP request from Device1 with its MAC address

# Print MAC addresses of devices after ARP resolution
print(f"{device1.name} MAC Address: {device1.mac_address}")
print(f"{device2.name} MAC Address: {device2.mac_address}")

# Configure static routes on the router for the network
router1.add_static_route("192.168.2.0", "192.168.1.2", "eth0", "255.255.255.0")  # Add a static route for network 192.168.2.0 via eth0
router1.add_static_route("10.1.0.0", "10.0.0.2", "eth1", "255.255.0.0")       # Add a static route for network 10.1.0.0 via eth1




def main():
    # Step 1: Create Routers
    router1 = Router("Router1")
    router2 = Router("Router2")
    router3 = Router("Router3")

    # Step 2: Add Interfaces to the Routers
    router1.add_interface("eth0", "192.168.1.1", "255.255.255.0")
    router1.add_interface("eth1", "10.0.0.1", "255.255.255.0")

    router2.add_interface("eth0", "192.168.2.1", "255.255.255.0")
    router2.add_interface("eth1", "192.168.1.2", "255.255.255.0")

    router3.add_interface("eth0", "10.0.0.2", "255.255.255.0")
    router3.add_interface("eth1", "10.1.0.1", "255.255.255.0")

    # Step 3: Configure Routing Tables
    router1.configure_routing_table("192.168.2.0", "192.168.1.2", "eth0", "255.255.255.0")
    router1.configure_routing_table("10.1.0.0", "10.0.0.2", "eth1", "255.255.0.0")

    router2.configure_routing_table("192.168.1.0", "192.168.1.1", "eth1", "255.255.255.0")
    router2.configure_routing_table("10.1.0.0", "10.0.0.2", "eth1", "255.255.0.0")

    router3.configure_routing_table("192.168.1.0", "10.0.0.1", "eth0", "255.255.255.0")
    router3.configure_routing_table("192.168.2.0", "10.0.0.1", "eth0", "255.255.255.0")


    # Step 4: Create Networks and Assign Devices
    network1 = Network("192.168.1.0", "255.255.255.0")
    network2 = Network("192.168.2.0", "255.255.255.0")
    network3 = Network("10.1.0.0", "255.255.255.0")

    device1 = Device("Device1")
    device2 = Device("Device2")
    device3 = Device("Device3")
    device4 = Device("Device4")
    device5 = Device("Device5")

    network1.assign_ip_address(device1)  # Assign IP to Device1
    network1.assign_ip_address(device2)  # Assign IP to Device2
    network2.assign_ip_address(device3)  # Assign IP to Device3
    network2.assign_ip_address(device4)  # Assign IP to Device4
    network3.assign_ip_address(device5)  # Assign IP to Device5

    # Step 5: Simulate ARP Requests/Responses within networks
    print(f"{device1.name} is sending an ARP request to resolve the MAC address of {device2.name}...")
    device1.send_arp_request(device2.ip_address)

    print(f"{device2.name} is sending an ARP response to {device1.name}...")
    device2.receive_arp_response(device1.ip_address, "00:11:22:33:44:55")

    print(f"{device3.name} is sending an ARP request to resolve the MAC address of {device4.name}...")
    device3.send_arp_request(device4.ip_address)

    print(f"{device4.name} is sending an ARP response to {device3.name}...")
    device4.receive_arp_response(device3.ip_address, "66:77:88:99:AA:BB")

    print(f"{device5.name} is sending an ARP request to resolve the MAC address of {router3.interfaces['eth1']['ip_address']}...")
    device5.send_arp_request(router3.interfaces['eth1']['ip_address'])

    print(f"{router3.router_id} is sending an ARP response to {device5.name}...")
    device5.receive_arp_response(router3.interfaces['eth1']['ip_address'], "CC:DD:EE:FF:00:11")

    # Step 6: Simulate Packet Forwarding across networks
    packet_from_device1_to_device3 = {'destination_ip': device3.ip_address}
    print(f"{device1.name} sends a packet to {device3.name}...")
    router1.forward_packet(packet_from_device1_to_device3)

    packet_from_device3_to_device5 = {'destination_ip': device5.ip_address}
    print(f"{device3.name} sends a packet to {device5.name}...")
    router2.forward_packet(packet_from_device3_to_device5)

    # Print final MAC addresses of devices
    print(f"{device1.name} MAC Address: {device1.mac_address}")
    print(f"{device2.name} MAC Address: {device2.mac_address}")
    print(f"{device3.name} MAC Address: {device3.mac_address}")
    print(f"{device4.name} MAC Address: {device4.mac_address}")
    print(f"{device5.name} MAC Address: {device5.mac_address}")

if __name__ == "__main__":
    main()