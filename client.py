import socket
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
import logging

# Set up logging for the client
logging.basicConfig(filename='client_logs.txt', level=logging.INFO,
                    format="{asctime} - {levelname} - {message}",
                    style="{",
                    datefmt="%Y-%m-%d %H:%M",
                    filemode='w')


class Socket_Client:
    def __init__(self, m_widget):

        # Creating GUI
        self.m_widget = m_widget
        self.m_widget.title("Network Based Searching Window")

        self.label_filename = tk.Label(m_widget, text="Filename:")
        self.label_filename.pack(pady=5)

        self.entry_filename = tk.Entry(m_widget, width=50, fg='lightgray')  # Light gray text for placeholder
        self.entry_filename.insert(0, 'sample.txt')  # Insert default filename
        self.entry_filename.pack(pady=5)

        # Bind the focus event to clear placeholder text
        self.entry_filename.bind("<FocusIn>", self.clear_placeholder)
        self.entry_filename.bind("<FocusOut>", self.set_placeholder)

        self.label_pattern = tk.Label(m_widget, text="Search Word/Pattern:")
        self.label_pattern.pack(pady=5)

        self.entry_pattern = tk.Entry(m_widget, width=50)
        self.entry_pattern.pack(pady=5)

        self.button_search = tk.Button(m_widget, text="Search", command=self.perform_search)
        self.button_search.pack(pady=10)

        self.result_text = scrolledtext.ScrolledText(m_widget, width=60, height=20)
        self.result_text.pack(pady=5)

    def clear_placeholder(self, event):
        if self.entry_filename.get() == 'sample.txt':
            self.entry_filename.delete(0, tk.END)  # Clear the placeholder
            self.entry_filename.config(fg='black')  # Change text color to black

    def set_placeholder(self, event):
        if not self.entry_filename.get():
            self.entry_filename.insert(0, 'sample.txt')  # Reset placeholder text
            self.entry_filename.config(fg='lightgray')  # Set text color back to light gray

    def perform_search(self):
        # Get the user input
        filename = self.entry_filename.get() or 'sample.txt'  # Default filename if empty
        search_pattern = self.entry_pattern.get()

        if not search_pattern:
            messagebox.showwarning("Input Error", "Please enter a search word or pattern.")
            logging.warning("Search attempt without a pattern.")
            return

        request_data = {
            'filename': filename,
            'pattern': search_pattern
        }

        logging.info(f"Sending request: Filename: {filename}, Pattern: {search_pattern}")

        # Connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect(('127.0.0.1', 5000))  # Server IP and port
                client_socket.send(json.dumps(request_data).encode('utf-8'))

                response = client_socket.recv(4096).decode('utf-8')
                result = json.loads(response)

                self.display_results(result, filename)

            except ConnectionRefusedError:
                logging.error("Failed to connect to the server.")
                messagebox.showerror("Connection Error",
                                     "Failed to connect to the server. Please ensure it is running.")
            except json.JSONDecodeError:
                logging.error("Invalid JSON response received from the server.")
                messagebox.showerror("Response Error", "Received an invalid response from the server.")
            except Exception as e:
                logging.error(f"An unexpected error occurred: {e}")
                messagebox.showerror("Error", str(e))

    def display_results(self, result, filename):
        self.result_text.delete(1.0, tk.END)  # Clear previous results
        if 'error' in result:
            self.result_text.insert(tk.END, result['error'])  # Display error message if present
            logging.info(f"Error received: {result['error']}")
        else:
            if len(result) == 1:  # Means no matching pattern found
                message = f"No pattern found in '{filename}'\n"
                self.result_text.insert(tk.END, message)
                logging.info(message)
            else:
                for item in result[1:]:  # Skip the first item (the search pattern)
                    line_number, line_content = item
                    self.result_text.insert(tk.END, f"Line {line_number}: {line_content}\n")
                logging.info(f"Search result displayed for pattern: {result[0]}")


if __name__ == "__main__":
    root = tk.Tk()
    app = Socket_Client(root)
    root.mainloop()
