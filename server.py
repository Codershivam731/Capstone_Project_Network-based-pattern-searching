# Importing Modules required for Programs
import socket
import threading
import json
import logging
import sys
from search import Search

# Setting Log Configuration into a text file
logging.basicConfig(filename='server_logs.txt',
                    format="{asctime} - {levelname} - {message}",
                    level=logging.INFO,
                    style='{',
                    datefmt="%Y-%m-%d %H:%M",
                    filemode='w')


class Loopback_Server:

    def __init__(self, host = '127.0.0.1', port=5000):
        """
        Configuring Server side connection
        :param host: Assign IP for server
        :param port: Assign the port you want to connect
        """

        self.up_flag = True
        self.host = host
        self.port = port
        self.ser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ser_socket.bind((self.host, self.port))
        self.ser_socket.listen(5)
        logging.info(f"Server started listening on {self.host} : {self.port}")
        print(f"Server started listening on {self.host} : {self.port}")
        print("+--" * 25)
        print("Press 'q' to close the server")

        # Thread keep running on background and wait for user input to close
        self.q_thread = threading.Thread(target=self.shutdown, daemon=True)
        self.q_thread.start()

    def connecting_client(self, c_socket, c_addr, th_name):
        """
        Establishing connection with client on a network
        :param c_socket: socket object associated with client
        :param c_addr:  address
        :param th_name: Thread name handling specific connection
        :return:
        """
        logging.info(f"Connected to {c_addr} --- Thread Exe - {th_name} ")
        try:
            c_req = c_socket.recv(1024).decode('utf-8')
            logging.info(f"Request received {c_req} --- Thread Exe - {th_name} ")

            # Deserialize s (a str, bytes or bytearray instance containing a JSON document) to a Python object.
            c_data = json.loads(c_req)
            c_filename = c_data.get('filename') or 'sample.txt'
            c_pattern = c_data.get('pattern')

            logging.info(f"Started searching {c_pattern} into {c_filename}  --- Thread Exe - {th_name} ")

            try:
                file_search = Search(c_filename)
                requested_lines = file_search.getlines(c_pattern)
                server_response = json.dumps(requested_lines)
                logging.info(f"Sending json response {server_response}")

            except FileNotFoundError as err:
                server_response = json.dumps({"ERROR": str(err)})
                logging.info("File not found on the server.")

            c_socket.send(server_response.encode('utf-8'))

        except Exception as err:
            logging.info(f"Unexpected Error {err}. Please Check generated server_logs.txt --- Thread Exe - {th_name}")

        finally:
            c_socket.close()
            logging.info(f"connection closed (X) .... --- Thread Exe - {th_name}")

    def starting_server(self):
        """
        Server started accepting connection.
        :return:
        """
        logging.info(f" Server running on {self.host} : {self.port}")

        while self.up_flag:
            try:
                c_socket, c_addr = self.ser_socket.accept()
                th_name = threading.current_thread().name
                logging.info(f" Accepted Connection ^-^ from {c_addr}")

                multiple_clients = threading.Thread(
                    target=self.connecting_client,
                    args=(c_socket, c_addr, th_name),
                    name=f"Thread - {threading.active_count()}"
                )

                multiple_clients.start()
            except OSError:
                break

    def shutdown(self):
        """
        Wait for 'q' :key press to shut down the server
        """
        while True:
            if input().lower() == 'q':
                logging.info("Exit Request ***___***")
                self.up_flag = False
                self.ser_socket.close()
                print("\n*** Shutting Down the Server... Thank you for using it! ***")
                sys.exit(0)


if __name__ == "__main__":
    server = Loopback_Server()
    server.starting_server()
