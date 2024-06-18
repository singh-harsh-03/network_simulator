import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
import network_layer
import Transport_application
from FlowCtrl import FlowControlProtocol

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
            self.connection.send(data, destination_mac, checksum,receiver_id=self.device_id)
    
    def receive_data(self, data, checksum, receiver_id):
        """
        Receive data along with checksum and sender ID.
        :param data: The received data (string).
        :param checksum: The checksum received along with the data.
        :param receiver_id: The ID of the sender device.
        """
        # Verify checksum
        if not ErrorControlProtocol.detect_errors(data, checksum):
            # Data is valid, process it
            print(f"Device {self.device_id} received data from {receiver_id}: {data}")
        else:
            # Data contains errors
            print(f"Error: Data received by {self.device_id} from {receiver_id} contains errors")


class Hub:
    def __init__(self):
        self.connected_devices = []

    def connect_device(self, device):
        self.connected_devices.append(device)

    def broadcast(self, data, receiver_id):
        checksum = ErrorControlProtocol.checksum(data)
        for device in self.connected_devices:
            if device.device_id != receiver_id: 
                device.receive_data(data,checksum,receiver_id)


class Connection:
    def __init__(self, device1, device2):
        self.device1 = device1
        self.device2 = device2
        device1.connect(self)
        device2.connect(self)

    def send(self, data, destination_mac=None, checksum=None,receiver_id=None):
        if AccessControlProtocol.control_access():
            if destination_mac == self.device1.device_id:
                self.device1.receive_data(data,checksum,receiver_id)
            elif destination_mac == self.device2.device_id:
                self.device2.receive_data(data,checksum,receiver_id)



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

        elif destination_mac == "Broadcast":
            print(f"Broadcasting data to all ports: {data}")
            # Forward data to all connected devices (except the source)
            for mac_addr, port in self.table.items():
                if mac_addr != self.mac_address:  # Exclude the source device
                    print(f"Forwarding to port {port}: {data}")
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
        if isinstance(data, str):
            # Calculate checksum using ASCII values of characters in the string
            checksum_value = sum(ord(char) for char in data)
            return checksum_value
        else:
            print(f"requires a String type")

    @staticmethod
    def binary_checksum(data_blocks, n_bits):
        """
        Calculates the checksum of the data using binary addition.
        :param data_blocks: List of data blocks (each block represented as an integer).
        :param n_bits: Number of bits in each data block.
        :return: The checksum value.
        """
        # Calculate the sum of all data blocks
        sum_data = sum(data_blocks)

        # Add carry to the sum, if any
        while sum_data >> n_bits:
            sum_data = (sum_data & ((1 << n_bits) - 1)) + (sum_data >> n_bits)

        # Perform one's complement
        checksum = ~sum_data & ((1 << n_bits) - 1)

        return checksum



    @staticmethod
    def detect_errors(data, checksum):
        # Calculate the checksum of the received data
        calculated_checksum = ErrorControlProtocol.checksum(data)

        # Compare the calculated checksum with the received checksum
        if calculated_checksum == checksum:
            return False  # No errors detected
        else:
            return True
    
    @staticmethod
    def detect_errors_binary(data_blocks, checksum, n_bits):
        """
        Detects errors in the received data by comparing the checksum.
        :param data_blocks: List of received data blocks (each block represented as an integer).
        :param checksum: The checksum received along with the data.
        :param n_bits: Number of bits in each data block.
        :return: True if errors are detected, False otherwise.
        """
        # Calculate the sum of all data blocks and checksum
        sum_data = sum(data_blocks) + checksum

        # Add carry to the sum, if any
        while sum_data >> n_bits:
            sum_data = (sum_data & ((1 << n_bits) - 1)) + (sum_data >> n_bits)

        # Perform one's complement
        computed_checksum = ~sum_data & ((1 << n_bits) - 1)

        # Check if the result is all 1s
        if computed_checksum == 0:
            return False  # No errors detected
        else:
            return True



class AccessControlProtocol:
    @staticmethod
    def control_access():
        # For basic implementation,used CSMA/CD.
        idle_probability = 0.1  # Probability of the medium being idle
        max_backoff_attempts = 10  # Maximum number of backoff attempts

        backoff_attempts = 0
        
        while backoff_attempts < max_backoff_attempts:
            if random.random() < idle_probability:
                return True  # Medium is idle, device can transmit
            else:
                # Medium is busy, wait for a random backoff period
                backoff_time = random.uniform(0, 1)  # Random backoff time between 0 and 1 seconds
                print(f"Medium is busy, waiting for {backoff_time:.2f} seconds...")
                time.sleep(backoff_time)  # Simulate waiting for the backoff time
                backoff_attempts += 1

        print("Exceeded maximum backoff attempts. Channel still busy.")
        return False



class EndDevice(PhysicalLayerDevice):
    def __init__(self, device_id):
        super().__init__(device_id)
        self.mac_address = None

    def set_mac_address(self, mac_address):
        self.mac_address = mac_address



# Test case 1: Two end devices with a dedicated connection
device1 = PhysicalLayerDevice("Device1")
device2 = PhysicalLayerDevice("Device2")
connection = Connection(device1, device2)
device1.send_data("Hello from Device 1", destination_mac="Device2")
device2.send_data("Hello from Device 2", destination_mac="Device1")

#Test case 2: a star toplogy with five end devices connected to hub
hub=Hub()
end_devices = [EndDevice(f"Device{i}") for i in range(1,6)]

for device in end_devices:
    hub.connect_device(device)


# Enable communication within end devices via the hub's broadcast
data_to_broadcast = "Hello, everyone!"
receiver_id = end_devices[0].device_id  # Assuming the first device is initiating the broadcast
hub.broadcast(data_to_broadcast, receiver_id)

# Define the devices
devices = ["Device1", "Device2"]

# Create a plot for visual representation
plt.figure(figsize=(6, 4))

# Plot the devices
for i, device in enumerate(devices):
    plt.text(i, 0.5, device, ha='center', va='center', size=12, bbox=dict(facecolor='lightblue', alpha=0.5))

# Draw a line representing the dedicated connection
plt.plot([0, 1], [0.5, 0.5], color='black', linestyle='-', linewidth=2)
plt.title("Test Case 1: Two End Devices with Dedicated Connection")
plt.axis("off")
plt.show()


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
data = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
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

device1=devices[0]    
device2=devices[1]


device1.send_data("Hello from Device 1", "00:11:22:33:44:03")
switch.forward("Hello from Device 1", "00:11:22:33:44:03")
# Send data from Device2 to Device5 through the switch
device2.send_data("Hello from Device2", "00:11:22:33:44:05")
switch.forward("Hello from Device2", "00:11:22:33:44:05")
# Send data from Device3 to Device1 through the switch
device3 = devices[2]  
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


data_blocks = [0b1101, 0b1010, 0b0110]  # Example data blocks (each represented as binary integers)
n_bits = 4  # Number of bits in each data block
checksum = ErrorControlProtocol.binary_checksum(data_blocks, n_bits)

received_data_blocks = [0b1101, 0b1010, 0b0110]  # Example received data blocks
received_checksum = 0b1111  # Received checksum (example)
n_bits = 4  # Number of bits in each data block
if ErrorControlProtocol.detect_errors_binary(received_data_blocks, received_checksum, n_bits):
    print("Errors detected in the received data.")
else:
    print("No errors detected in the received data.")


# Test case 2: Star topology with five end devices connected to each hub
hub1 = Hub()
hub2 = Hub()

end_devices1 = [EndDevice(f"Device{i}") for i in range(1, 6)]
end_devices2 = [EndDevice(f"Device{i}") for i in range(6, 11)]

for device in end_devices1:
    hub1.connect_device(device)

for device in end_devices2:
    hub2.connect_device(device)

def connect_hubs_to_switch(hub1, hub2, switch):
    switch.connect(hub1)
    switch.connect(hub2)


# Create and setup the switch
interconnect_switch = Switch("Switch")
connect_hubs_to_switch(hub1, hub2, interconnect_switch)

# Function to assign MAC addresses and make the switch learn them
def setup_devices_and_learn_mac(devices, switch, start_index=1, learn=True):
    for i, device in enumerate(devices):
        mac_address = f"00:11:22:33:44:{start_index + i:02d}"
        device.set_mac_address(mac_address)
        if learn:
            switch.learn_mac_address(mac_address, start_index + i)


# Simulate sending a message from Device1 to all devices
sender_id = "Device4"
receiver_id = "Device1"
message = "Hello, everyone, I am Device 4!"

print(f"Sending message from {sender_id}: {message}")


if sender_id in [device.device_id for device in end_devices1] and receiver_id in [device.device_id for device in end_devices1]:
    hub1.broadcast(message, sender_id)

elif sender_id in [device.device_id for device in end_devices2] and receiver_id in [device.device_id for device in end_devices2]:
    hub2.broadcast(message, sender_id)

else:
    hub1.broadcast(message,sender_id)
    hub2.broadcast(message,sender_id)

sender_hub = None
receiver_hub = None

for device in end_devices1:
    if device.device_id == sender_id:
        sender_hub = hub1
    if device.device_id == receiver_id:
        receiver_hub = hub1

for device in end_devices2:
    if device.device_id == sender_id:
        sender_hub = hub2
    if device.device_id == receiver_id:
        receiver_hub = hub2

if sender_hub == receiver_hub:
    print("Sender and receiver are in the same hub. Switch learns MAC addresses only for devices in hub1.")
    setup_devices_and_learn_mac(end_devices1, interconnect_switch, start_index=1, learn=True)
else:
    print("Sender and receiver are in different hubs. Switch learns MAC addresses for all devices.")
    setup_devices_and_learn_mac(end_devices1, interconnect_switch, start_index=1, learn=True)
    setup_devices_and_learn_mac(end_devices2, interconnect_switch, start_index=6, learn=True)

interconnect_switch.print_switch_table()


# Create the network topology graph
G = nx.Graph()

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

total_broadcast_domains = 2  # Two broadcast domains (one per hub/switch)
total_collision_domains = len(end_devices1) + len(end_devices2)  # One collision domain per device in each hub/switch
print("Total Broadcast Domains:", total_broadcast_domains)
print("Total Collision Domains:", total_collision_domains)

network_layer.main()
Transport_application.main()