import random
import networkx as nx
import matplotlib.pyplot as plt

class PhysicalLayerDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.connection = None

    def connect(self, connection):
        self.connection = connection

    def send_data(self, data, destination_mac=None):
        if self.connection:
            self.connection.receive_data(data, destination_mac)
        if isinstance(self.connection, Switch):
            self.connection.forward(data, destination_mac)

    def receive_data(self, data):
        print(f"Device {self.device_id} received data: {data}")


class Hub:
    def __init__(self):
        self.connected_devices = []

    def connect_device(self, device):
        self.connected_devices.append(device)

    def broadcast(self, data):
        for device in self.connected_devices:
            device.receive_data(data)


class Connection:
    def __init__(self, device1, device2):
        self.device1 = device1
        self.device2 = device2
        device1.connect(self)
        device2.connect(self)

    def receive_data(self, data, destination_mac=None):
        # Simulate transmission medium (e.g., wire)
        self.device1.receive_data(data)
        self.device2.receive_data(data)


class DataLinkLayerDevice(PhysicalLayerDevice):
    def __init__(self, device_id):
        super().__init__(device_id)
        self.mac_address = None

    def set_mac_address(self, mac_address):
        self.mac_address = mac_address


class Bridge(DataLinkLayerDevice):
    def __init__(self, device_id):
        super().__init__(device_id)
        self.table = {}

    def learn_mac_address(self, mac_address, port):
        self.table[mac_address] = port

    def forward(self, data, destination_mac):
        if destination_mac in self.table:
            port = self.table[destination_mac]
            print(f"Forwarding data to port {port}: {data}")
        else:
            print(f"MAC address {destination_mac} not found in the bridge table.")


class Switch(DataLinkLayerDevice):
    def __init__(self, device_id):
        super().__init__(device_id)
        self.table = {}

    def learn_mac_address(self, mac_address, port):
        self.table[mac_address] = port

    def forward(self, data, destination_mac):
        if destination_mac in self.table:
            port = self.table[destination_mac]
            print(f"Forwarding data to port {port}: {data}")
        else:
            print(f"MAC address {destination_mac} not found in the switch table.")

    def print_switch_table(self):
        print("Switch Table:")
        for mac_address, port in self.table.items():
            print(f"MAC Address: {mac_address}, Port: {port}")


class ErrorControlProtocol:
    @staticmethod
    def checksum(data):
        """
        Calculates the checksum of the data.
        :param data: The data for which the checksum will be calculated.
        :return: The checksum value.
        """
        # Simple sum-based checksum calculation
        return sum(data)

    @staticmethod
    def detect_errors(data, checksum):
        """
        Detects errors in the received data using a checksum.
        :param data: The received data.
        :param checksum: The checksum received along with the data.
        :return: True if errors are detected, False otherwise.
        """
        # Calculate the checksum of the received data
        calculated_checksum = ErrorControlProtocol.checksum(data)

        # Compare the calculated checksum with the received checksum
        if calculated_checksum == checksum:
            return False  # No errors detected
        else:
            return True  # Errors detected


class AccessControlProtocol:
    @staticmethod
    def control_access():
        # Placeholder for access control
        # For basic implementation, let's use CSMA/CD (Carrier Sense Multiple Access with Collision Detection)
        # In this simple version, we assume there's no collision detection, just a simple carrier sense mechanism

        idle_probability = 0.1  # Assuming 10% chance that the medium is idle
        if random.random() < idle_probability:
            return True  # Medium is idle, device can transmit
        else:
            return False


class FlowControlProtocol:
    @staticmethod
    def sliding_window(window_size, data):
        # Placeholder for sliding window flow control
        # For basic implementation, we'll simply send data in chunks of window_size

        # Divide data into chunks based on window_size
        chunks = []
        for i in range(0, len(data), window_size):
            chunk = data[i:i + window_size]
            chunks.append(chunk)


        # Simulate sending each chunk and waiting for acknowledgment
        for chunk in chunks:
            print("Sending chunk:", chunk)
            # Simulate waiting for acknowledgment
            acknowledgment_received = random.choice([True, False])  # Randomly simulate acknowledgment
            if acknowledgment_received:
                print("Acknowledgment received for chunk:", chunk)
            else:
                print("Acknowledgment not received for chunk:", chunk)
                # Resend the chunk if acknowledgment not received
                print("Resending chunk:", chunk)
                # Simulate waiting for acknowledgment again
                acknowledgment_received = random.choice([True, False])  # Randomly simulate acknowledgment after resend
                if acknowledgment_received:
                    print("Acknowledgment received for resent chunk:", chunk)
                else:
                    print("Failed to receive acknowledgment for resent chunk:", chunk)

class EndDevice(PhysicalLayerDevice):
    pass  # Inherits from PhysicalLayerDevice


# Example usage:
window_size = 3
data = "ABCDEFGHIJKLMNOPQUVWX"
FlowControlProtocol.sliding_window(window_size, data)



# Test case 1: Two end devices with a dedicated connection
device1 = PhysicalLayerDevice("Device1")
device2 = PhysicalLayerDevice("Device2")
connection = Connection(device1, device2)
device1.send_data("Hello from Device 1")
device2.send_data("Hello from Device 2")

# Test case 2: Star topology with five end devices connected to a hub
hub1 = Hub()
hub2 = Hub()

end_devices1 = [EndDevice(f"Device{i}") for i in range(1, 6)]
end_devices2 = [EndDevice(f"Device{i}") for i in range(6, 11)]

for device in end_devices1:
    hub1.connect_device(device)

for device in end_devices2:
    hub2.connect_device(device)

interconnect_switch = Switch("Switch")

for device in end_devices1:
    interconnect_switch.connect(device)

for device in end_devices2:
    interconnect_switch.connect(device)
    
# Enable communication between end devices across the network
# Broadcasting from devices in hub1 to devices in hub2 via the switch
for device in end_devices1:
    device.send_data("Hello from Hub1", destination_mac="Broadcast")

# Broadcasting from devices in hub2 to devices in hub1 via the switch
for device in end_devices2:
    device.send_data("Hello from Hub2", destination_mac="Broadcast")

# Report the total number of broadcast and collision domains
total_broadcast_domains = 2  # Two broadcast domains (one per hub/switch)
total_collision_domains = len(end_devices1) + len(end_devices2)  # One collision domain per device in each hub/switch
print("Total Broadcast Domains:", total_broadcast_domains)
print("Total Collision Domains:", total_collision_domains)


# Create the network topology graph
G = nx.Graph()

# # Add nodes for hub and end devices
G.add_node("Hub1")
G.add_node("Hub2")
for device in end_devices1:
    G.add_node(device.device_id)

for device in end_devices2:
    G.add_node(device.device_id)

# Add edges for connections
for device in end_devices1:
    G.add_edge("Hub1", device.device_id)

for device in end_devices2:
    G.add_edge("Hub2", device.device_id)

# Add edges for interconnection via the switch
G.add_edge("Switch", "Hub1")
G.add_edge("Switch", "Hub2")

# # Visualize the network topology
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, nodelist=["Hub1", "Hub2"], node_color='blue', node_size=3000)
nx.draw_networkx_nodes(G, pos, nodelist=["Switch"], node_color='red', node_size=4000 )
nx.draw_networkx_nodes(G, pos, nodelist=[device.device_id for device in end_devices1], node_color='skyblue', node_size=2000)
nx.draw_networkx_nodes(G, pos, nodelist=[device.device_id for device in end_devices2], node_color='skyblue', node_size=2000)
nx.draw_networkx_edges(G, pos, width=2)
nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')

plt.title("Network Topology - Hub with End Devices")
plt.show()

# Test case: Create a switch with five end devices connected to it
switch = Switch("Switch1")
devices = []  # Initialize an empty list

for i in range(1, 6):  
    device = DataLinkLayerDevice(f"Device{i}")  # Create a DataLinkLayerDevice object with a unique ID
    devices.append(device)  # Add the device to the list

for i, device in enumerate(devices):
    device.set_mac_address(f"00:11:22:33:44:0{i+1}")
    switch.learn_mac_address(device.mac_address, i + 1)  
    switch.connect(device)


# Test case: Send data from Device1 to Device3 through the switch
device1.send_data("Hello from Device1", "00:11:22:33:44:03")
switch.forward("Hello from Device1", "00:11:22:33:44:03")


# Test case: Send data from Device2 to Device5 through the switch
device2.send_data("Hello from Device2", "00:11:22:33:44:05")
switch.forward("Hello from Device2", "00:11:22:33:44:05")


# Test case: Send data from Device3 to Device1 through the switch
device3 = devices[2]  # Get the third device from the list
device3.send_data("Hello from Device3", "00:11:22:33:44:01")
switch.forward("Hello from Device3","00:11:22:33:44:01")
device4 = devices[3]  # Get the fourth device from the list
device5 = devices[4] 
# Test case: Send data from Device4 to Device2 through the switch
device4.send_data("Hello from Device4", "00:11:22:33:44:02")
switch.forward("Hello from Device4","00:11:22:33:44:02")

# Test case: Send data from Device5 to Device4 through the switch
device5.send_data("Hello from Device5", "00:11:22:33:44:04")
switch.forward("Hello from Device5","00:11:22:33:44:04")

switch.print_switch_table()


# Enable data transmission between devices with flow control
for i, device in enumerate(devices):
    device.send_data(f"Hello from {device.device_id}", "00:11:22:33:44:05") # Broadcasting to device 5

