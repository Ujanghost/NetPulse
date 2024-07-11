# NetPulse

NetPulse is a comprehensive network monitoring tool that provides real-time insights into your network's performance. It collects data on network speed, packet loss, latency, and other metrics, displaying the results in a user-friendly graphical interface. Additionally, it offers features for generating detailed reports and listing connected devices.

## Features

- **Real-time Network Monitoring**: Displays current network speed, packet loss, and latency.
- **Graphical Data Representation**: Visualizes network performance metrics over time.
- **Background Data Collection**: Allows for continuous data collection without user intervention.
- **Report Generation**: Creates daily, weekly, and monthly reports in PDF format.
- **Connected Devices Listing**: Lists all devices connected to the network.
- **Indicators**: Visual indicators for network health, internet connectivity, and data collection status.

## Installation

To run NetPulse, you need to have Python installed on your machine along with the required libraries. Install the necessary dependencies using pip:

```sh
pip install tkinter customtkinter matplotlib psutil pillow requests
```

## Usage

Run the `NetworkMonitorApp` by executing:

```sh
python netpulse.py
```

The application will launch a window displaying real-time network metrics and various control buttons for managing network tests and generating reports.

## Screenshot

![NetPulse Screenshot](ss.png)

## Future Improvements

- **Enhanced Data Analysis**: Add more detailed data analysis features, such as identifying trends and anomalies.
- **Customizable Alerts**: Implement alerts for significant changes in network performance.
- **Remote Monitoring**: Enable remote monitoring capabilities to observe network performance from different locations.
- **Mobile App**: Develop a mobile application for monitoring network performance on-the-go.
- **Integration with Other Tools**: Allow integration with other network management and monitoring tools for a more comprehensive solution.

## License

This project is licensed under the MIT License.

---

Feel free to contribute to the project by submitting issues and pull requests on [GitHub](https://github.com/yourusername/netpulse). For more information, visit the project repository.

