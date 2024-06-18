import http.client
import ftplib
from FlowCtrl import FlowControlProtocol

class TCPSimulator:
    def __init__(self):
        self.port_map = {}
        self.well_known_ports = set(range(0, 1024))
        self.ephemeral_ports = set(range(1024, 49152))
        self.processes = {}

    # Transport Layer: Port Management
    def assign_port(self, process_id):
        if process_id not in self.processes:
            if self.well_known_ports:
                port = self.well_known_ports.pop()
            elif self.ephemeral_ports:
                port = self.ephemeral_ports.pop()
            else:
                raise RuntimeError("No available ports")
            self.port_map[process_id] = port
            self.processes[process_id] = {
                "port": port,
                "data_buffer": [],
                "ack_buffer": []
            }
            return port
        else:
            return self.port_map[process_id]

    # Transport Layer: Sending Data
    def send_data(self, process_id, data):
        if process_id not in self.processes:
            raise RuntimeError("Process not registered")
        FlowControlProtocol.sliding_window(5, data)
        # For simplicity, we'll just assume data is delivered successfully
        self.processes[process_id]["data_buffer"].append(data)

    # Application Layer: Telnet Service
    def http_client_service(self, host, port, path):
        try:
            conn = http.client.HTTPConnection(host, port)
            conn.request("GET", path)
            response = conn.getresponse()
            data = response.read().decode('utf-8')
            conn.close()
            return data
        except Exception as e:
            return str(e)


    # Application Layer: FTP Service
    def ftp_service(self, host, username, password, command, filepath=None):
        try:
            ftp = ftplib.FTP(host)
            ftp.login(username, password)
            response = ""
            if command == "list":
                response = ftp.retrlines('LIST')
            elif command == "download" and filepath:
                with open(filepath, 'wb') as f:
                    ftp.retrbinary(f'RETR {filepath}', f.write)
                response = f"Downloaded {filepath}"
            elif command == "upload" and filepath:
                with open(filepath, 'rb') as f:
                    ftp.storbinary(f'STOR {filepath}', f)
                response = f"Uploaded {filepath}"
            ftp.quit()
            return response
        except Exception as e:
            return str(e)


    # Testing the protocol stack
    def test_protocol_stack(self):
        # Demonstrate working of the entire protocol stack
        process_id_1 = "process_1"
        process_id_2 = "process_2"

        port_1 = self.assign_port(process_id_1)
        port_2 = self.assign_port(process_id_2)

        print(f"Assigned port {port_1} to {process_id_1}")
        print(f"Assigned port {port_2} to {process_id_2}")

        data = "Hello, this is a test message for the Transport Layer protocol."
        print("Sending data from process_1 to process_2...")
        self.send_data(process_id_1, data)

        host = "jsonplaceholder.typicode.com"
        port = 80
        path = "/todos/1"

        print(f"Sending HTTP GET request to {host}:{port}{path}...")
        response = self.http_client_service(host, port, path)
        print(f"Received HTTP response:\n{response}")


        # FTP service test
        print("Testing FTP service...")
        ftp_host = "ftp.dlptest.com"
        ftp_username = "dlpuser"
        ftp_password = "rNrKYTX9g7z3RgJRmxWuGHbeu"
        ftp_response = self.ftp_service(ftp_host, ftp_username, ftp_password, "list")
        print(f"FTP service response: {ftp_response}")

        # file_data = "Sample file data for transfer."
        # print("Testing file transfer service...")
        # file_transfer_response = self.file_transfer_service(process_id_1, file_data)
        # print(f"File transfer service response: {file_transfer_response}")


def main():
    tcp_simulator = TCPSimulator()
    tcp_simulator.test_protocol_stack()

if __name__ == "__main__":
    main()