import tkinter as tk
import customtkinter as ctk
from datetime import datetime, timedelta
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import matplotlib.dates as mdates
import psutil
import socket
import os
import time
import requests
import subprocess
import threading

class NetworkMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Network Monitor")
        self.geometry("1200x800")
        self.configure(fg_color="#2C3E50")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, fg_color="#34495E", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        self.network_speed_label = ctk.CTkLabel(self.header_frame, text="Current Network Speed: N/A", font=("Roboto", 18, "bold"), text_color="#ECF0F1")
        self.network_speed_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.start_test_button = ctk.CTkButton(self.header_frame, text="Start Network Test", command=self.confirm_start_test, fg_color="#27AE60", hover_color="#2ECC71")
        self.start_test_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.stop_test_button = ctk.CTkButton(self.header_frame, text="Stop Network Test", command=self.stop_network_test, fg_color="#E74C3C", hover_color="#C0392B", state="disabled")
        self.stop_test_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.bg_collect_button = ctk.CTkButton(self.header_frame, text="Background Collection", command=self.toggle_background_collection, fg_color="#9B59B6", hover_color="#8E44AD")
        self.bg_collect_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.data_collection_indicator = ctk.CTkLabel(self.header_frame, text="⬤", font=("Roboto", 18), text_color="#7F8C8D")
        self.data_collection_indicator.pack(side=tk.RIGHT, padx=10, pady=10)

        self.network_health_indicator = ctk.CTkLabel(self.header_frame, text="⬤", font=("Roboto", 18), text_color="#F1C40F")
        self.network_health_indicator.pack(side=tk.RIGHT, padx=10, pady=10)

        self.internet_indicator = ctk.CTkLabel(self.header_frame, text="⬤", font=("Roboto", 18), text_color="#7F8C8D")
        self.internet_indicator.pack(side=tk.RIGHT, padx=10, pady=10)

        self.main_frame = ctk.CTkFrame(self, fg_color="#34495E", corner_radius=10)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.debug_console = ctk.CTkTextbox(self.main_frame, width=1160, height=100, font=("Roboto", 12))
        self.debug_console.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        self.fig, self.axs = plt.subplots(3, 1, figsize=(10, 6))
        self.fig.patch.set_facecolor('#34495E')
        for ax in self.axs:
            ax.set_facecolor('#2C3E50')
            ax.tick_params(colors='#ECF0F1')
            ax.spines['bottom'].set_color('#ECF0F1')
            ax.spines['top'].set_color('#ECF0F1')
            ax.spines['left'].set_color('#ECF0F1')
            ax.spines['right'].set_color('#ECF0F1')
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        self.footer_frame = ctk.CTkFrame(self, fg_color="#34495E", corner_radius=0)
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))

        self.report_button = ctk.CTkButton(self.footer_frame, text="Download Daily Report", command=lambda: self.generate_report("daily"), fg_color="#3498DB", hover_color="#2980B9")
        self.report_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.weekly_report_button = ctk.CTkButton(self.footer_frame, text="Download Weekly Report", command=lambda: self.generate_report("weekly"), fg_color="#3498DB", hover_color="#2980B9")
        self.weekly_report_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.monthly_report_button = ctk.CTkButton(self.footer_frame, text="Download Monthly Report", command=lambda: self.generate_report("monthly"), fg_color="#3498DB", hover_color="#2980B9")
        self.monthly_report_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.list_devices_button = ctk.CTkButton(self.footer_frame, text="List Connected Devices", command=self.list_connected_devices, fg_color="#3498DB", hover_color="#2980B9")
        self.list_devices_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.stop_button = ctk.CTkButton(self.footer_frame, text="Exit", fg_color="#E74C3C", hover_color="#C0392B", command=self.all_stop)
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.network_data = []
        self.start_time = datetime.now()
        self.is_monitoring = False
        self.is_background_collecting = False
        self.csv_file = 'network_metrics.csv'
        self.downtime_start = None
        self.total_downtime = timedelta()

        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Packet Loss", "Latency (ms)", "Network Speed (Mbps)", "Is Down"])

        self.passive_monitoring()
        self.update_indicators()

    def confirm_start_test(self):
        confirm = ctk.CTkInputDialog(text="Starting the network test may affect your network performance. Are you sure you want to continue? (yes/no)", title="Caution")
        response = confirm.get_input()
        if response and response.lower() == 'yes':
            self.start_network_test()
        else:
            self.debug_console.insert("end", "Network test cancelled.\n")
            self.debug_console.see("end")

    def start_network_test(self):
        self.is_monitoring = True
        self.debug_console.insert("end", "Network test started.\n")
        self.debug_console.see("end")
        self.start_test_button.configure(state="disabled")
        self.stop_test_button.configure(state="normal")

    def stop_network_test(self):
        self.is_monitoring = False
        self.debug_console.insert("end", "Network test stopped.\n")
        self.debug_console.see("end")
        self.start_test_button.configure(state="normal")
        self.stop_test_button.configure(state="disabled")

    def toggle_background_collection(self):
        self.is_background_collecting = not self.is_background_collecting
        if self.is_background_collecting:
            self.bg_collect_button.configure(text="Stop Background Collection")
            self.debug_console.insert("end", "Background data collection started.\n")
        else:
            self.bg_collect_button.configure(text="Background Collection")
            self.debug_console.insert("end", "Background data collection stopped.\n")
        self.debug_console.see("end")

    def passive_monitoring(self):
        self.log_network_metrics()
        if self.is_monitoring or self.is_background_collecting:
            self.update_graphs()
        self.after(5000, self.passive_monitoring)

    def get_network_metrics(self):
        net_io = psutil.net_io_counters()
        bytes_sent, bytes_recv = net_io.bytes_sent, net_io.bytes_recv
        time.sleep(1)
        net_io = psutil.net_io_counters()
        new_bytes_sent, new_bytes_recv = net_io.bytes_sent, net_io.bytes_recv

        upload_speed = (new_bytes_sent - bytes_sent) / 125000
        download_speed = (new_bytes_recv - bytes_recv) / 125000

        try:
            latency = socket.getaddrinfo('google.com', 80)[0][4][0]
            start_time = time.time()
            socket.create_connection((latency, 80), timeout=5)
            latency = (time.time() - start_time) * 1000
        except socket.error:
            latency = None

        packet_loss = net_io.dropin + net_io.dropout

        return packet_loss, latency, download_speed, upload_speed

    def update_graphs(self):
        timestamps = [entry[0] for entry in self.network_data]
        packet_losses = [entry[1] for entry in self.network_data]
        latencies = [entry[2] for entry in self.network_data]
        download_speeds = [entry[3] for entry in self.network_data]
        upload_speeds = [entry[4] for entry in self.network_data]

        self.axs[0].clear()
        self.axs[0].plot(timestamps, packet_losses, color='#E74C3C')
        self.axs[0].set_ylabel('Packet Loss')
        self.axs[0].set_title('Packet Loss Over Time')

        self.axs[1].clear()
        self.axs[1].plot(timestamps, latencies, color='#3498DB')
        self.axs[1].set_ylabel('Latency (ms)')
        self.axs[1].set_title('Latency Over Time')

        self.axs[2].clear()
        self.axs[2].plot(timestamps, download_speeds, label='Download Speed (Mbps)', color='#2ECC71')
        self.axs[2].plot(timestamps, upload_speeds, label='Upload Speed (Mbps)', color='#F39C12')
        self.axs[2].set_ylabel('Speed (Mbps)')
        self.axs[2].set_title('Network Speed Over Time')
        self.axs[2].legend()

        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()

    def log_network_metrics(self):
        packet_loss, latency, download_speed, upload_speed = self.get_network_metrics()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        is_down = packet_loss > 0 or latency is None
        if is_down and not self.downtime_start:
            self.downtime_start = datetime.now()
        elif not is_down and self.downtime_start:
            downtime = datetime.now() - self.downtime_start
            self.total_downtime += downtime
            self.downtime_start = None

        self.network_data.append((timestamp, packet_loss, latency, download_speed, upload_speed, is_down))
        self.network_data = self.network_data[-60:]

        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, packet_loss, latency, download_speed, upload_speed, is_down])

        self.network_speed_label.configure(text=f"Current Network Speed: {download_speed:.2f} Mbps / {upload_speed:.2f} Mbps")

    def update_indicators(self):
        self.update_network_health_indicator()
        self.update_internet_indicator()
        self.update_data_collection_indicator()
        self.after(1000, self.update_indicators)

    def update_network_health_indicator(self):
        if self.network_data:
            _, packet_loss, latency, _, _, is_down = self.network_data[-1]
            if is_down:
                self.network_health_indicator.configure(text_color="#E74C3C")
            elif packet_loss > 0 or latency > 200:
                self.network_health_indicator.configure(text_color="#F39C12")
            else:
                self.network_health_indicator.configure(text_color="#2ECC71")
        else:
            self.network_health_indicator.configure(text_color="#7F8C8D")

    def update_internet_indicator(self):
        try:
            requests.get("https://www.google.com", timeout=5)
            self.internet_indicator.configure(text_color="#2ECC71")
        except requests.ConnectionError:
            self.internet_indicator.configure(text_color="#E74C3C")

    def update_data_collection_indicator(self):
        if self.is_background_collecting:
            self.data_collection_indicator.configure(text_color="#2ECC71")
        else:
            self.data_collection_indicator.configure(text_color="#7F8C8D")

    def generate_report(self, report_type):
        end_date = datetime.now()
        if report_type == "daily":
            start_date = end_date - timedelta(days=1)
            filename = f"daily_report_{end_date.strftime('%Y%m%d')}.pdf"
        elif report_type == "weekly":
            start_date = end_date - timedelta(weeks=1)
            filename = f"weekly_report_{end_date.strftime('%Y%m%d')}.pdf"
        elif report_type == "monthly":
            start_date = end_date - timedelta(days=30)
            filename = f"monthly_report_{end_date.strftime('%Y%m%d')}.pdf"

        filtered_data = [row for row in self.network_data if start_date <= datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") <= end_date]

        with PdfPages(filename) as pdf:
            # First Page: Graphs
            plt.figure(figsize=(10, 6))
            timestamps = [datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S") for data in filtered_data]
            packet_losses = [data[1] for data in filtered_data]
            latencies = [data[2] if data[2] is not None else 0 for data in filtered_data]
            speeds = [data[3] for data in filtered_data]

            plt.subplot(3, 1, 1)
            plt.plot(timestamps, packet_losses, label='Packet Loss', color='#E74C3C')
            plt.xlabel('Timestamp')
            plt.ylabel('Packet Loss')
            plt.legend()

            plt.subplot(3, 1, 2)
            plt.plot(timestamps, latencies, label='Latency (ms)', color='#F39C12')
            plt.xlabel('Timestamp')
            plt.ylabel('Latency (ms)')
            plt.legend()

            plt.subplot(3, 1, 3)
            plt.plot(timestamps, speeds, label='Network Speed (Mbps)', color='#2ECC71')
            plt.xlabel('Timestamp')
            plt.ylabel('Network Speed (Mbps)')
            plt.legend()

            plt.tight_layout()
            pdf.savefig()  # Save the current figure
            plt.close()  # Close the current figure

            # Second Page: Summary
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.95, f"{report_type.capitalize()} Network Performance Report", horizontalalignment='center', verticalalignment='center', fontsize=18)
            plt.text(0.5, 0.85, f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", horizontalalignment='center', verticalalignment='center', fontsize=12)
            plt.text(0.5, 0.75, f"Average Download Speed: {sum(speeds) / len(speeds):.2f} Mbps", horizontalalignment='center', verticalalignment='center', fontsize=12)
            plt.text(0.5, 0.65, f"Average Latency: {sum(latencies) / len(latencies):.2f} ms", horizontalalignment='center', verticalalignment='center', fontsize=12)
            plt.text(0.5, 0.55, f"Total Downtime: {self.total_downtime}", horizontalalignment='center', verticalalignment='center', fontsize=12)
            
            isp_info = self.get_isp_info()
            plt.text(0.5, 0.45, f"ISP: {isp_info['isp']}", horizontalalignment='center', verticalalignment='center', fontsize=12)
            plt.text(0.5, 0.35, f"IP: {isp_info['ip']}", horizontalalignment='center', verticalalignment='center', fontsize=12)
            
            computer_info = self.get_computer_network_info()
            plt.text(0.5, 0.25, f"Computer Network Info:", horizontalalignment='center', verticalalignment='center', fontsize=12)
            plt.text(0.5, 0.20, f"MAC Address: {computer_info['mac']}", horizontalalignment='center', verticalalignment='center', fontsize=10)
            plt.text(0.5, 0.15, f"IP Address: {computer_info['ip']}", horizontalalignment='center', verticalalignment='center', fontsize=10)
            plt.text(0.5, 0.10, f"Default Gateway: {computer_info['gateway']}", horizontalalignment='center', verticalalignment='center', fontsize=10)
            
            plt.text(0.5, 0.05, f"This report provides a comprehensive analysis of the network performance over the {report_type} period.", horizontalalignment='center', verticalalignment='center', fontsize=10)
            plt.axis('off')
            pdf.savefig()  # Save the current figure
            plt.close()  # Close the current figure

        self.debug_console.insert("end", f"{report_type.capitalize()} report generated successfully: {filename}\n")
        self.debug_console.see("end")


    def list_connected_devices(self):
        try:
            output = subprocess.check_output(['arp', '-a'])
            devices = output.decode().split('\n')
            self.debug_console.insert("end", "Connected Devices:\n")
            for device in devices:
                self.debug_console.insert("end", f"{device}\n")
            self.debug_console.see("end")
        except subprocess.CalledProcessError as e:
            self.debug_console.insert("end", f"Failed to list connected devices: {e}\n")
            self.debug_console.see("end")

    def all_stop(self):
        self.stop_network_test()
        self.is_background_collecting = False
        self.update_data_collection_indicator()
        self.destroy()

if __name__ == "__main__":
    app = NetworkMonitorApp()
    app.mainloop()
