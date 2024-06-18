
import random
#implemetation of go back n protocol
class FlowControlProtocol:
    @staticmethod
    def sliding_window(window_size, data):     
        # Divide data into chunks based on window_size
        chunks = [data[i:i + window_size] for i in range(0, len(data), window_size)]
        base = 0
        next_seq_num = 0
        expected_ack = 0

        while base < len(chunks):
            # Send packets within the window
            while next_seq_num < min(base + window_size, len(chunks)):
                print(f"Sending packet {next_seq_num}: {chunks[next_seq_num]}")
                next_seq_num += 1

            # Receive acknowledgments within the window
            for _ in range(base, next_seq_num):
                acknowledgment_received = random.choice([True, False])  # Simulate ACK reception
                if acknowledgment_received:
                    print(f"Acknowledgment received for packet {_}: {chunks[_]}")
                    expected_ack = _ + 1
                else:
                    print(f"Acknowledgment not received for packet {_}: {chunks[_]}")
                    break

            # Slide the window based on the acknowledgment received
            if expected_ack == next_seq_num:
                base = expected_ack
            else:
                print(f"Timeout occurred, resending from packet {base}: {chunks[base]}")
                next_seq_num = base 

        print("All packets transmitted successfully")

