import random
class PhysicalLayerDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.connection = None

    def connect(self, connection):
        self.connection = connection

    def send_data(self, data, destination_mac=None):
        if self.connection:
            self.connection.receive_data(data, destination_mac)

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
        chunks = [data[i:i + window_size] for i in range(0, len(data), window_size)]

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

# Example usage:
window_size = 3
data = "ABCDEFGHIJKLMNOPQUVWXYZ"
FlowControlProtocol.sliding_window(window_size, data)



# Test case 1: Two end devices with a dedicated connection
device1 = PhysicalLayerDevice("Device1")
device2 = PhysicalLayerDevice("Device2")
connection = Connection(device1, device2)
device1.send_data("Hello from Device 1")
device2.send_data("Hello from Device 2")

# Test case 2: Star topology with five end devices connected to a hub
hub = Hub()
devices = [PhysicalLayerDevice(f"Device{i}") for i in range(1, 6)]
for device in devices:
    hub.connect_device(device)
hub.broadcast("Hello from the hub")

# Test case: Create a switch with five end devices connected to it
switch = Switch("Switch1")
devices = [DataLinkLayerDevice(f"Device{i}") for i in range(1, 6)]
for i, device in enumerate(devices):
    device.set_mac_address(f"00:11:22:33:44:0{i}")
    switch.learn_mac_address(device.mac_address, i + 1)  # Assuming ports start from 1

# Enable data transmission between devices with flow control
for i, device in enumerate(devices):
    device.send_data(f"Hello from {device.device_id}", "00:11:22:33:44:05") # Broadcasting to device 5

# Report the total number of broadcast and collision domains
total_broadcast_domains = 1  # One broadcast domain per hub/switch
total_collision_domains = len(devices)  # One collision domain per device in a hub/switch
print("Total Broadcast Domains:", total_broadcast_domains)
print("Total Collision Domains:", total_collision_domains)

