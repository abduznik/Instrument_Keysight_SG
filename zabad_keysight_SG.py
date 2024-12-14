import tkinter as tk
from tkinter import messagebox
import pyvisa
import os
import sys
def resource(relative_path):
        base_path = getattr(
            sys,
            '_MEIPASS',
            os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
icon_path = resource("eitam911.ico")
class CustomIPDialog(tk.Toplevel):
    def __init__(self, master, initial_ip):
        super().__init__(master)
        self.title("Configure IP Address")
        self.geometry("400x200")
        self.configure(bg="#2c2c2c")

        self.result = None

        # Header Label
        tk.Label(
            self,
            text="Enter Signal Generator IP:",
            font=("Helvetica", 14),
            bg="#2c2c2c",
            fg="white"
        ).pack(pady=10)

        # Input Entry
        self.ip_entry = tk.Entry(
            self,
            font=("Helvetica", 14),
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            width=30
        )
        self.ip_entry.insert(0, initial_ip)
        self.ip_entry.pack(pady=10)

        # Buttons Frame
        button_frame = tk.Frame(self, bg="#2c2c2c")
        button_frame.pack(pady=10)

        # OK Button
        tk.Button(
            button_frame,
            text="OK",
            font=("Helvetica", 12),
            bg="#3e3e3e",
            fg="white",
            activebackground="#5e5e5e",
            activeforeground="white",
            relief="flat",
            command=self.on_ok
        ).pack(side=tk.LEFT, padx=5)

        # Cancel Button
        tk.Button(
            button_frame,
            text="Cancel",
            font=("Helvetica", 12),
            bg="#3e3e3e",
            fg="white",
            activebackground="#5e5e5e",
            activeforeground="white",
            relief="flat",
            command=self.on_cancel
        ).pack(side=tk.LEFT, padx=5)

    def on_ok(self):
        self.result = self.ip_entry.get().strip()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

class SignalGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap(icon_path)
        self.root.title("Signal Generator Controller")
        self.root.geometry("410x530")
        self.root.configure(bg="#2c2c2c")

        # Config file setup
        self.config_file = os.path.join(os.path.expanduser("~"), "signal_generator_config.txt")
        self.signal_generator_address = "TCPIP::192.168.0.10::INSTR"
        self.load_config()

        # State to track the input
        self.current_input = ""
        self.is_negative = False

        # Display
        self.display_var = tk.StringVar(value="0.00")
        self.display = tk.Entry(
            root,
            textvariable=self.display_var,
            font=("Helvetica", 24),
            justify="center",
            state="readonly",
            bg="#1e1e1e",
            fg="white",
            readonlybackground="#1e1e1e",
            relief="flat",
        )
        self.display.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="we")

        # Keypad Buttons
        buttons = [
            ("1", 1, 0),
            ("2", 1, 1),
            ("3", 1, 2),
            ("4", 2, 0),
            ("5", 2, 1),
            ("6", 2, 2),
            ("7", 3, 0),
            ("8", 3, 1),
            ("9", 3, 2),
            ("CLR", 4, 0),
            ("0", 4, 1),
            ("SEND", 4, 2),
        ]

        for (text, row, col) in buttons:
            tk.Button(
                root,
                text=text,
                font=("Helvetica", 18),
                bg="#3e3e3e",
                fg="white",
                activebackground="#5e5e5e",
                activeforeground="white",
                relief="flat",
                command=lambda t=text: self.on_button_click(t),
            ).grid(row=row, column=col, padx=5, pady=5, sticky="we")

        # Toggle +/- button
        self.toggle_button = tk.Button(
            root,
            text="-/+",
            font=("Helvetica", 18),
            bg="#3e3e3e",
            fg="white",
            activebackground="#5e5e5e",
            activeforeground="white",
            relief="flat",
            command=self.toggle_sign,
        )
        self.toggle_button.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="we")

        # Options button
        tk.Button(
            root,
            text="OPTIONS",
            font=("Helvetica", 18),
            bg="#3e3e3e",
            fg="white",
            activebackground="#5e5e5e",
            activeforeground="white",
            relief="flat",
            command=self.configure_ip,
        ).grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="we")

        # Footer label for instructions
        self.instruction_label = tk.Label(
            root,
            text="Enter up to 4 digits. Example: 12 → 0.12, 123 → 1.23, 1234 → 12.34",
            font=("Helvetica", 10),
            bg="#2c2c2c",
            fg="#a5a5a5",
        )
        self.instruction_label.grid(row=7, column=0, columnspan=3, pady=5)

        # Footer label for credits
        self.footer_label = tk.Label(
            root,
            text="Created by Yan Version 1.1",
            font=("Helvetica", 10),
            bg="#2c2c2c",
            fg="#a5a5a5",
        )
        self.footer_label.grid(row=8, column=0, columnspan=3, pady=5)

    def load_config(self):
        """Load IP from the config file or create the file if it doesn't exist."""
        if os.path.exists(self.config_file):
            # Read the IP address from the config file
            with open(self.config_file, "r") as f:
                ip = f.read().strip()
                self.signal_generator_address = f"TCPIP::{ip}::INSTR"
        else:
            # Create the config file with a default IP
            self.save_config("192.168.0.10")

    def save_config(self, ip):
        """Save the current IP to the config file."""
        try:
            with open(self.config_file, "w") as f:
                f.write(ip)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save IP: {e}")

    def on_button_click(self, button_text):
        if button_text == "CLR":
            self.current_input = ""
            self.display_var.set("0.00")
        elif button_text == "SEND":
            self.send_signal()
        else:
            # Update input based on the button pressed
            if len(self.current_input) < 4:  # Limit input to 4 digits
                self.current_input += button_text
            self.update_display()

    def update_display(self):
        """Update the display with formatted dBm value."""
        if not self.current_input:  # If input is empty, reset to 0.00
            formatted = "0.00"
        elif len(self.current_input) == 1:
            formatted = f"0.0{self.current_input}"  # Single digit
        elif len(self.current_input) == 2:
            formatted = f"0.{self.current_input}"  # Two digits
        elif len(self.current_input) == 3:
            formatted = f"{self.current_input[0]}.{self.current_input[1:]}"  # Three digits
        else:  # Four digits
            formatted = f"{self.current_input[:2]}.{self.current_input[2:]}"

        if self.is_negative:
            formatted = f"-{formatted}"

        self.display_var.set(formatted)

    def toggle_sign(self):
        """Toggle the sign of the current input."""
        self.is_negative = not self.is_negative
        self.update_display()

    def send_signal(self):
        try:
            dBm_value = float(self.display_var.get())  # Use formatted value
            if dBm_value > 12.0 or dBm_value < -12.0:
                messagebox.showerror("Error", "Value exceeds the range of -12 dBm to 12 dBm!")
                return

            rm = pyvisa.ResourceManager()
            self.visa_resource = rm.open_resource(self.signal_generator_address)
            self.visa_resource.write(f"POWER {dBm_value}")
            messagebox.showinfo("Success", f"Set signal generator to {dBm_value} dBm.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")
        finally:
            if hasattr(self, 'visa_resource'):
                self.visa_resource.close()

    def configure_ip(self):
        dialog = CustomIPDialog(self.root, self.signal_generator_address.split('::')[1])
        self.root.wait_window(dialog)
        if dialog.result:
            self.signal_generator_address = f"TCPIP::{dialog.result}::INSTR"
            self.save_config(dialog.result)
            messagebox.showinfo("Configuration", f"Updated IP to {dialog.result}.")
    
    
if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(icon_path)
    app = SignalGeneratorApp(root)
    root.mainloop()
