# Log Analysis Dashboard

A Flask-based web application for analyzing and visualizing log data patterns, designed to help identify anomalies and security incidents in system logs.

<img width="857" alt="image" src="https://github.com/user-attachments/assets/0178f256-6397-4718-ab90-19ac3b57d714" />


##  Features

- **Interactive Dashboard**: View key metrics and trends at a glance
- **Anomaly Detection**: Identify unusual patterns in log data
- **Advanced Search**: Filter logs by various parameters including timestamp, user, IP address, and action
- **Data Visualization**: Charts and graphs to represent log activity patterns
- **Responsive Design**: Works on desktop and mobile devices

##  Demo

This project is available as a live demo at [demo-link.com](https://demo-link.com) where you can interact with the dashboard using simulated log data.

> **Note**: The live demo uses simulated data and is intended for demonstration purposes only.

## Technologies Used

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib

##  Screenshots

### User Acitivity Dashboard
![image](https://github.com/user-attachments/assets/ff318566-7a13-4aca-9d96-d6d7b3f9295f)


### Action distribution Dashboard
![image](https://github.com/user-attachments/assets/e14f4d19-5298-40ec-b067-c38d7980708c)
![image](https://github.com/user-attachments/assets/099b00d1-86e1-4a3c-b268-1b3e224a1a19)


### Security dashboard
![image](https://github.com/user-attachments/assets/ed997bba-b65b-47e9-be8d-b138dce45b72)
![image](https://github.com/user-attachments/assets/356d6575-3dae-4904-8794-31013d81c5ee)

### Anomaly Detectiom
![image](https://github.com/user-attachments/assets/d42d2a6f-9679-463a-9c56-f82e495f9a35)
![image](https://github.com/user-attachments/assets/39a1e534-1a0e-4da2-9c7d-908d55a85171)
![image](https://github.com/user-attachments/assets/76293308-b4d8-48d0-bde2-31afe3f2c6ac)






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

## Usage Guide

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

