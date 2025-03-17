# Log Analysis Dashboard

A Flask-based web application for analyzing and visualizing log data patterns, designed to help identify anomalies and security incidents in system logs.

![Dashboard Preview](screenshots/dashboard_preview.png)

## 🌟 Features

- **Interactive Dashboard**: View key metrics and trends at a glance
- **Anomaly Detection**: Identify unusual patterns in log data
- **Advanced Search**: Filter logs by various parameters including timestamp, user, IP address, and action
- **Data Visualization**: Charts and graphs to represent log activity patterns
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Demo

This project is available as a live demo at [demo-link.com](https://demo-link.com) where you can interact with the dashboard using simulated log data.

> **Note**: The live demo uses simulated data and is intended for demonstration purposes only.

## 📋 Technologies Used

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib

## 📸 Screenshots

### Main Dashboard
![Main Dashboard](screenshots/main_dashboard.png)

### Anomaly Detection
![Anomaly Detection](screenshots/anomaly_detection.png)

### Search Functionality
![Search Functionality](screenshots/search_functionality.png)

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.7+
- pip

### Installation Steps

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/log-analysis-dashboard.git
   cd log-analysis-dashboard
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database with sample data
   ```bash
   python init_db.py
   ```

5. Run the application
   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://127.0.0.1:5000`

## 📊 Data Simulation

This project uses simulated log data to demonstrate functionality. The simulated data includes:

- User login/logout events
- File access operations
- System configuration changes
- Simulated security incidents
- Various IP addresses and user agents

The data is designed to showcase patterns that would be typical in a production environment, including:
- Daily usage patterns (working hours vs. off-hours)
- Weekend vs. weekday differences
- Occasional anomalies that might indicate security concerns

## 🔍 Usage Guide

### Dashboard Navigation
- The main dashboard displays an overview of log activity
- Use the date range selector to filter data by time period
- Hover over charts to see detailed information

### Searching Logs
1. Navigate to the Search page
2. Enter search criteria (e.g., username, IP address, action type)
3. Click "Search" to filter results
4. Use pagination to navigate through results

### Anomaly Detection
1. Go to the Anomalies page
2. View highlighted unusual patterns
3. Click on specific anomalies to see detailed information

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

Your Name - [your.email@example.com](mailto:your.email@example.com)

Project Link: [https://github.com/yourusername/log-analysis-dashboard](https://github.com/yourusername/log-analysis-dashboard)

---

⭐️ If you found this project helpful, please give it a star on GitHub! ⭐️ 