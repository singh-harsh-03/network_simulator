import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class PhysicalLayerDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.connection = None

    def connect(self, connection):
        self.connection = connection

    def send_data(self, data, destination_mac=None, window_size=3):
        if self.connection:
            FlowControlProtocol.sliding_window(window_size, data)
            checksum = ErrorControlProtocol.checksum(data)
            self.connection.send(data, destination_mac, checksum,sender_id=self.device_id)
    
    def receive_data(self, data, checksum, sender_id):
        """
        Receive data along with checksum and sender ID.
        :param data: The received data (string).
        :param checksum: The checksum received along with the data.
        :param sender_id: The ID of the sender device.
        """
        # Verify checksum
        if not ErrorControlProtocol.detect_errors(data, checksum):
            # Data is valid, process it
            print(f"Device {self.device_id} received data from {sender_id}: {data}")
        else:
            # Data contains errors
            print(f"Error: Data received by {self.device_id} from {sender_id} contains errors")


class Hub:
    def __init__(self):
        self.connected_devices = []

    def connect_device(self, device):
        self.connected_devices.append(device)

    def broadcast(self, data, sender_id):
        checksum = ErrorControlProtocol.checksum(data)
        for device in self.connected_devices:
            if device.device_id != sender_id:  # Exclude the sender from receiving the broadcast
                device.receive_data(data,checksum,sender_id)


class Connection:
    def __init__(self, device1, device2):
        self.device1 = device1
        self.device2 = device2
        device1.connect(self)
        device2.connect(self)

    def send(self, data, destination_mac=None, checksum=None,sender_id=None):
        if destination_mac == self.device1.device_id:
            self.device1.receive_data(data,checksum,sender_id)
        elif destination_mac == self.device2.device_id:
            self.device2.receive_data(data,checksum,sender_id)



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
        if isinstance(data, str):
            # Calculate checksum using ASCII values of characters in the string
            checksum_value = sum(ord(char) for char in data)
            return checksum_value
        else:
            raise TypeError("Checksum calculation requires a string input")


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



# Test case 1: Two end devices with a dedicated connection
device1 = PhysicalLayerDevice("Device1")
device2 = PhysicalLayerDevice("Device2")
connection = Connection(device1, device2)
device1.send_data("Hello from Device 1", destination_mac="Device2")
device2.send_data("Hello from Device 2", destination_mac="Device1")

#Create a star toplogy with five end devices connected to hub
hub=Hub()
end_devices = [EndDevice(f"Device{i}") for i in range(1,6)]

for device in end_devices:
    hub.connect_device(device)


# Enable communication within end devices via the hub's broadcast
data_to_broadcast = "Hello, everyone!"
sender_id = end_devices[0].device_id  # Assuming the first device is initiating the broadcast
hub.broadcast(data_to_broadcast, sender_id)

# Define the devices
devices = ["Device1", "Device2"]

# Create a plot for visual representation
plt.figure(figsize=(6, 4))

# Plot the devices
for i, device in enumerate(devices):
    plt.text(i, 0.5, device, ha='center', va='center', size=12, bbox=dict(facecolor='lightblue', alpha=0.5))

# Draw a line representing the dedicated connection
plt.plot([0, 1], [0.5, 0.5], color='black', linestyle='-', linewidth=2)

# Add labels and title
plt.title("Test Case 1: Two End Devices with Dedicated Connection")
plt.axis("off")
plt.show()


# Define the devices and hub
devices = ["Device1", "Device2", "Device3", "Device4", "Device5"]
hub = "Hub"

# Create a plot for visual representation
plt.figure(figsize=(8, 6))

# Plot the devices around the hub
num_devices = len(devices)
theta = 2 * np.pi / num_devices  # Calculate angle between devices
radius = 2

for i, device in enumerate(devices):
    x = radius * np.cos(i * theta)
    y = radius * np.sin(i * theta)
    plt.text(x, y, device, ha='center', va='center', size=12, bbox=dict(facecolor='lightblue', alpha=0.5))
    plt.plot([0, x], [0, y], color='black', linestyle='-', linewidth=1)  # Connect device to hub

# Plot the hub at the center
plt.text(0, 0, hub, ha='center', va='center', size=12, bbox=dict(facecolor='lightgreen', alpha=0.5))

plt.title("Star Topology: Hub with Five End Devices")
plt.axis("off")
plt.show()

# Example usage:
window_size = 3
data = "ABCDEFGHIJKLMNOPQUVWXYZ"
FlowControlProtocol.sliding_window(window_size, data)


switch = Switch("Switch1")
devices = []  # Initialize an empty list

for i in range(1, 6):  
    device = DataLinkLayerDevice(f"Device{i}")  # Create a DataLinkLayerDevice object with a unique ID
    devices.append(device)  # Add the device to the list

for i, device in enumerate(devices):
    device.set_mac_address(f"00:11:22:33:44:0{i+1}")
    switch.learn_mac_address(device.mac_address, i + 1)  
    switch.connect(device)


# Send data from Device1 to Device3 through the switch
device1.send_data("Hello from Device1", "00:11:22:33:44:03")
switch.forward("Hello from Device1", "00:11:22:33:44:03")


# Send data from Device2 to Device5 through the switch
device2.send_data("Hello from Device2", "00:11:22:33:44:05")
switch.forward("Hello from Device2", "00:11:22:33:44:05")


# Send data from Device3 to Device1 through the switch
device3 = devices[2]  # Get the third device from the list
device3.send_data("Hello from Device3", "00:11:22:33:44:01")
switch.forward("Hello from Device3","00:11:22:33:44:01")
device4 = devices[3]  
device5 = devices[4] 

# Send data from Device4 to Device2 through the switch
device4.send_data("Hello from Device4", "00:11:22:33:44:02")
switch.forward("Hello from Device4","00:11:22:33:44:02")

# Send data from Device5 to Device4 through the switch
device5.send_data("Hello from Device5", "00:11:22:33:44:04")
switch.forward("Hello from Device5","00:11:22:33:44:04")

switch.print_switch_table()


# Test case 2: Star topology with five end devices connected to each hub
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




# Enable data transmission between devices with flow control
for i, device in enumerate(devices):
    device.send_data(f"Hello from {device.device_id}", "00:11:22:33:44:05") # Broadcasting to device 5



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


 # Visualize the network topology
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, nodelist=["Hub1", "Hub2"], node_color='blue', node_size=3000)
nx.draw_networkx_nodes(G, pos, nodelist=["Switch"], node_color='red', node_size=4000 )
nx.draw_networkx_nodes(G, pos, nodelist=[device.device_id for device in end_devices1], node_color='skyblue', node_size=2000)
nx.draw_networkx_nodes(G, pos, nodelist=[device.device_id for device in end_devices2], node_color='skyblue', node_size=2000)
nx.draw_networkx_edges(G, pos, width=2)
nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')

plt.title("Network Topology - Hub with End Devices")
plt.show()

# Report the total number of broadcast and collision domains
total_broadcast_domains = 2  # Two broadcast domains (one per hub/switch)
total_collision_domains = len(end_devices1) + len(end_devices2)  # One collision domain per device in each hub/switch
print("Total Broadcast Domains:", total_broadcast_domains)
print("Total Collision Domains:", total_collision_domains)

