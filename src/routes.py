import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from log_parser import load_logs, import_logs_from_csv  
from sqlalchemy import func
from models import LogEntry
from datetime import datetime, timedelta
import numpy as np
from flask import Blueprint, render_template, request, redirect, url_for


logs = Blueprint("logs", __name__)

@logs.route("/")
def index():
    log_data = load_logs()
    if log_data is not None:
        # Limit to first 10 rows
        limited_data = log_data.head(11)
        df_limited = pd.DataFrame(limited_data)
        df_limited_count = len(df_limited)
        
        total_rows = len(log_data)
        message = f'<div style="margin-bottom: 15px; font-style: italic; color: #6c757d;">Showing {df_limited_count} of {total_rows} rows. Use search to find all instances of logs by any row.</div>'
        
        # Combine the message with the HTML table
        html_content = message + limited_data.to_html()
        
        return render_template("index.html", logs=html_content)
    return "Error loading logs"


@logs.route('/import', methods=['POST'])
def import_logs():
    csv_file = request.files.get('csv_file')

    if csv_file:
        try:
            # Save the uploaded CSV file temporarily
            filepath = f"../data/{csv_file.filename}"
            csv_file.save(filepath)

            # Call the function to import logs from the CSV
            import_logs_from_csv(filepath)

            return redirect(url_for('logs.index'))  # Redirect back to the index or success page
        except Exception as e:
            return f"Error importing logs: {e}"
    return "No file uploaded"
    

@logs.route("/plot")
def plot():
    log_data = load_logs()
    if log_data is not None:
        # Set a modern style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        user_activity = log_data.groupby("username")["action"].value_counts().unstack().fillna(0)

        # Create figure with a more reasonable size
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Custom color palette - using a standard colormap
        colors = plt.get_cmap('Blues')(np.linspace(0.4, 0.8, len(user_activity.columns)))
        
        user_activity.plot(kind="bar", stacked=True, ax=ax, color=colors)
        
        ax.set_title("User Activity Distribution", fontsize=14, fontweight='bold')
        ax.set_xlabel("Username", fontsize=12)
        ax.set_ylabel("Activity Count", fontsize=12)
        
        # Improve legend and add grid
        ax.legend(title="Action Type", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Format ticks
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.tight_layout()
        
        img = io.BytesIO()
        plt.savefig(img, format="png", dpi=100)  # Lower DPI for smaller file size
        img.seek(0)
        img_b64 = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Return HTML with page header, navbar, centered image and evaluation section
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>User Activity Dashboard</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                body {{
                    background-color: #f8f9fa;
                    color: #343a40;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    text-align: center;
                    color: #212529;
                    margin-bottom: 30px;
                    font-size: 2.5em;
                    font-weight: 700;
                    padding: 15px 0;
                    position: relative;
                    letter-spacing: 1px;
                    display: inline-block;
                    margin-left: auto;
                    margin-right: auto;
                }}
                h1::after {{
                    content: "";
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 100%;
                    height: 3px;
                    background: linear-gradient(to right, #3a506b, #4361ee);
                    border-radius: 2px;
                }}
                .header-container {{
                    text-align: center;
                    width: 100%;
                }}
                .nav-buttons {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-bottom: 30px;
                    justify-content: center;
                }}
                .nav-button {{
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: 600;
                    text-decoration: none;
                    text-align: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    flex: 1;
                    min-width: 180px;
                    max-width: 250px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: #3a506b;
                    color: white;
                }}
                .nav-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 6px 8px rgba(0,0,0,0.2);
                    background-color: #1c2541;
                }}
                .nav-button.primary {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #4361ee;
                }}
                .nav-button.success {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #38b000;
                }}
                .nav-button.warning {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #ff9e00;
                }}
                .nav-button.danger {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #ef476f;
                }}
                .nav-button.info {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #4cc9f0;
                }}
                .content-container {{
                    text-align: center;
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .image-container {{
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    padding: 10px;
                    background: white;
                    border-radius: 8px;
                }}
                .analysis-container {{
                    margin-top: 20px;
                    text-align: left;
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    font-size: 16px;
                }}
                .analysis-container h3 {{
                    color: #3a506b;
                    border-bottom: 1px solid #e9ecef;
                    padding-bottom: 10px;
                    font-size: 20px;
                }}
                .analysis-container p, .analysis-container li {{
                    margin-top: 10px;
                    line-height: 1.7;
                    font-size: 16px;
                }}
                .analysis-container strong {{
                    font-size: 17px;
                    font-weight: 600;
                }}
                .button-container {{
                    margin-top: 20px;
                    text-align: center;
                }}
                .action-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #3a506b;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-right: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header-container">
                    <h1>User Activity Dashboard</h1>
                </div>
                
                <!-- Navigation Buttons -->
                <div class="nav-buttons">
                    <a href="{url_for('logs.index')}" class="nav-button primary">Home</a>
                    <a href="{url_for('logs.plot')}" class="nav-button success">User Activity Plot</a>
                    <a href="{url_for('logs.dashboard')}" class="nav-button info">Dashboard</a>
                    <a href="{url_for('logs.security_dashboard')}" class="nav-button danger">Security Dashboard</a>
                    <a href="{url_for('logs.detect_anomalies')}" class="nav-button warning">Anomaly Detection</a>
                </div>
                
                <div class="content-container">
                    <div class="image-container">
                        <img src="data:image/png;base64,{img_b64}" alt="User Activity Plot" style="max-width:100%; height:auto;">
                    </div>
                    <div class="analysis-container">
                        <h3>Analysis</h3>
                        <p style="margin-top: 10px; line-height: 1.6;">
                            This visualization shows the distribution of different actions performed by each user. 
                            The stacked bars represent different action types, allowing you to compare user activity patterns.
                        </p>
                        <p style="margin-top: 10px; line-height: 1.6;">
                            <strong>Key Observations:</strong>
                        </p>
                        <ul style="margin-top: 5px; line-height: 1.6;">
                            <li>Compare the total activity levels between users</li>
                            <li>Identify which actions are most common for each user</li>
                            <li>Spot unusual patterns or outliers in user behavior</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
    return "Error loading logs"

@logs.route("/filter")
def filter_logs():
    log_data = load_logs()
    value = request.args.get("value")
    page = request.args.get("page", 1, type=int)  # Get the page number from query params, default to 1
    per_page = 11  # Number of results per page

    if log_data is not None and value:
        # Convert to string for comparison and filter rows where any column contains the search term
        filtered_data = log_data[
            log_data.apply(lambda row: row.astype(str).str.contains(value, case=False, na=False).any(), axis=1)
        ]
        
        # Get total count of filtered rows
        total_filtered = len(filtered_data)
        total_pages = (total_filtered + per_page - 1) // per_page  # Ceiling division
        
        # Calculate start and end indices for the current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_filtered)
        
        # Get the subset of data for the current page
        page_data = filtered_data.iloc[start_idx:end_idx]
        
        # Create pagination links
        pagination_html = create_pagination_links(page, total_pages, value)
        
        # Create message showing current range and total
        if total_filtered > 0:
            message = f'<div style="margin-bottom: 15px; font-style: italic; color: #6c757d;">Showing results {start_idx + 1}-{end_idx} of {total_filtered} matching rows for "{value}"</div>'
            html_content = message + page_data.to_html() + pagination_html
        else:
            message = f'<div style="margin-bottom: 15px; font-style: italic; color: #6c757d;">No results found for "{value}"</div>'
            html_content = message
            
        return render_template("index.html", logs=html_content)
    
    return render_template("index.html", logs="")
   
def create_pagination_links(current_page, total_pages, search_value):
    """Create HTML for pagination links"""
    if total_pages <= 1:
        return ""
    
    html = '<div style="margin-top: 20px; text-align: center;">'
    html += '<div style="display: inline-block; background-color: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">'
    
    # Previous button
    if current_page > 1:
        html += f'<a href="{url_for("logs.filter_logs", value=search_value, page=current_page-1)}" style="margin: 0 5px; padding: 5px 10px; text-decoration: none; color: #3a506b; border: 1px solid #dee2e6; border-radius: 4px;">Previous</a>'
    else:
        html += f'<span style="margin: 0 5px; padding: 5px 10px; color: #6c757d; border: 1px solid #dee2e6; border-radius: 4px;">Previous</span>'
    
    # Page numbers
    # Show up to 5 page numbers centered around the current page
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, start_page + 4)
    
    # Adjust start_page if we're near the end
    if end_page - start_page < 4:
        start_page = max(1, end_page - 4)
    
    for i in range(start_page, end_page + 1):
        if i == current_page:
            html += f'<span style="margin: 0 5px; padding: 5px 10px; background-color: #3a506b; color: white; border-radius: 4px;">{i}</span>'
        else:
            html += f'<a href="{url_for("logs.filter_logs", value=search_value, page=i)}" style="margin: 0 5px; padding: 5px 10px; text-decoration: none; color: #3a506b; border: 1px solid #dee2e6; border-radius: 4px;">{i}</a>'
    
    # Next button
    if current_page < total_pages:
        html += f'<a href="{url_for("logs.filter_logs", value=search_value, page=current_page+1)}" style="margin: 0 5px; padding: 5px 10px; text-decoration: none; color: #3a506b; border: 1px solid #dee2e6; border-radius: 4px;">Next</a>'
    else:
        html += f'<span style="margin: 0 5px; padding: 5px 10px; color: #6c757d; border: 1px solid #dee2e6; border-radius: 4px;">Next</span>'
    
    html += '</div>'
    html += '</div>'
    
    return html

@logs.route('/anomalies')
def detect_anomalies():
    log_data = load_logs()
    if log_data is None:
        return "Error loading logs"
    
    # Filter for failed login attempts
    failed_logins = log_data[log_data["action"] == "failed_login"]
    
    # Calculate time threshold (last 30 days)
    if not failed_logins.empty:
        max_date = failed_logins["timestamp"].max()
        time_threshold = max_date - timedelta(days=30)
        time_period = "30"
    else:
        # Default if no data
        time_threshold = datetime.now() - timedelta(days=30)
        time_period = "0"
    
    # Filter for recent failed attempts
    recent_failed = failed_logins[failed_logins["timestamp"] >= time_threshold]
    
    # Count failed attempts by user
    user_fail_count = recent_failed["username"].value_counts()
    
    # Identify suspicious users (more than 5 failed attempts)
    suspicious_users = user_fail_count[user_fail_count > 5].index.tolist()
    
    # Create user-count pairs for template
    user_fail_counts = [(user, count) for user, count in user_fail_count[user_fail_count > 5].items()]
    
    # Total failed attempts
    total_failed_attempts = len(recent_failed)
    
    # Create visualization
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 1. Failed logins over time
    if not recent_failed.empty:
        time_series = recent_failed.set_index("timestamp").resample('D')["action"].count()
        time_series.plot(kind="line", marker='o', color="#ff9e00", ax=ax1)
        ax1.set_title("Failed Login Attempts Over Time", fontsize=14, fontweight='bold')
        ax1.set_xlabel("Date", fontsize=12)
        ax1.set_ylabel("Number of Failed Attempts", fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
    else:
        ax1.text(0.5, 0.5, "No failed login data available", 
                 horizontalalignment='center', verticalalignment='center',
                 transform=ax1.transAxes, fontsize=14)
        ax1.set_title("Failed Login Attempts Over Time", fontsize=14, fontweight='bold')
    
    # 2. Top users with failed logins
    if len(user_fail_counts) > 0:
        users = [x[0] for x in user_fail_counts[:10]]  # Get top 10 users
        counts = [x[1] for x in user_fail_counts[:10]]
        
        bars = ax2.bar(users, counts, color="#ff9e00")
        ax2.set_title("Top Users with Failed Login Attempts", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Username", fontsize=12)
        ax2.set_ylabel("Number of Failed Attempts", fontsize=12)
        ax2.set_xticklabels(users, rotation=45, ha='right')
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=10)
    else:
        ax2.text(0.5, 0.5, "No suspicious users detected", 
                 horizontalalignment='center', verticalalignment='center',
                 transform=ax2.transAxes, fontsize=14)
        ax2.set_title("Top Users with Failed Login Attempts", fontsize=14, fontweight='bold')
    
    plt.tight_layout(pad=3.0)
    
    # Convert plot to base64 image
    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=100)
    img.seek(0)
    anomaly_img = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return render_template('anomalies.html', 
                          suspicious_users=suspicious_users,
                          user_fail_counts=user_fail_counts,
                          total_failed_attempts=total_failed_attempts,
                          time_period=time_period,
                          anomaly_img=anomaly_img)

@logs.route("/dashboard")
def dashboard():
    log_data = load_logs()
    if log_data is not None:
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Create a figure with multiple subplots - smaller size
        fig = plt.figure(figsize=(10, 8))
        
        # 1. User Activity Bar Chart
        ax1 = fig.add_subplot(221)
        user_activity = log_data.groupby("username")["action"].value_counts().unstack().fillna(0)
        user_activity.plot(kind="bar", stacked=True, ax=ax1)
        ax1.set_title("User Activity", fontsize=12)
        ax1.set_xlabel("Username", fontsize=10)
        ax1.set_ylabel("Count", fontsize=10)
        plt.xticks(rotation=45, ha='right', fontsize=8)
        ax1.legend(fontsize=8)
        
        # 2. Action Distribution Pie Chart
        ax2 = fig.add_subplot(222)
        action_counts = log_data["action"].value_counts()
        action_counts.plot(kind="pie", autopct='%1.1f%%', ax=ax2, fontsize=8)
        ax2.set_title("Action Distribution", fontsize=12)
        ax2.set_ylabel("")
        
        # 3. Time Series of Activities
        ax3 = fig.add_subplot(212)
        time_series = log_data.set_index("timestamp").resample('H')["action"].count()
        time_series.plot(kind="line", marker='o', ax=ax3)
        ax3.set_title("Activity Over Time", fontsize=12)
        ax3.set_xlabel("Timestamp", fontsize=10)
        ax3.set_ylabel("Number of Actions", fontsize=10)
        ax3.grid(True)
        ax3.tick_params(axis='both', which='major', labelsize=8)
        
        plt.tight_layout(pad=1.5)
        
        img = io.BytesIO()
        plt.savefig(img, format="png", dpi=100)
        img.seek(0)
        img_b64 = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Return HTML with page header, navbar, centered image and evaluation section
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Activity Dashboard</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                body {{
                    background-color: #f8f9fa;
                    color: #343a40;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    text-align: center;
                    color: #212529;
                    margin-bottom: 30px;
                    font-size: 2.5em;
                    font-weight: 700;
                    padding: 15px 0;
                    position: relative;
                    letter-spacing: 1px;
                    display: inline-block;
                    margin-left: auto;
                    margin-right: auto;
                }}
                h1::after {{
                    content: "";
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 100%;
                    height: 3px;
                    background: linear-gradient(to right, #3a506b, #4361ee);
                    border-radius: 2px;
                }}
                .header-container {{
                    text-align: center;
                    width: 100%;
                }}
                .nav-buttons {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-bottom: 30px;
                    justify-content: center;
                }}
                .nav-button {{
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: 600;
                    text-decoration: none;
                    text-align: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    flex: 1;
                    min-width: 180px;
                    max-width: 250px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: #3a506b;
                    color: white;
                }}
                .nav-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 6px 8px rgba(0,0,0,0.2);
                    background-color: #1c2541;
                }}
                .nav-button.primary {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #4361ee;
                }}
                .nav-button.success {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #38b000;
                }}
                .nav-button.warning {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #ff9e00;
                }}
                .nav-button.danger {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #ef476f;
                }}
                .nav-button.info {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #4cc9f0;
                }}
                .content-container {{
                    text-align: center;
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .image-container {{
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    padding: 10px;
                    background: white;
                    border-radius: 8px;
                }}
                .analysis-container {{
                    margin-top: 20px;
                    text-align: left;
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    font-size: 16px;
                }}
                .analysis-container h3 {{
                    color: #3a506b;
                    border-bottom: 1px solid #e9ecef;
                    padding-bottom: 10px;
                    font-size: 20px;
                }}
                .analysis-container p, .analysis-container li {{
                    margin-top: 10px;
                    line-height: 1.7;
                    font-size: 16px;
                }}
                .analysis-container strong {{
                    font-size: 17px;
                    font-weight: 600;
                }}
                .button-container {{
                    margin-top: 20px;
                    text-align: center;
                }}
                .action-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #3a506b;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-right: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header-container">
                    <h1>Activity Dashboard</h1>
                </div>
                
                <!-- Navigation Buttons -->
                <div class="nav-buttons">
                    <a href="{url_for('logs.index')}" class="nav-button primary">Home</a>
                    <a href="{url_for('logs.plot')}" class="nav-button success">User Activity Plot</a>
                    <a href="{url_for('logs.dashboard')}" class="nav-button info">Dashboard</a>
                    <a href="{url_for('logs.security_dashboard')}" class="nav-button danger">Security Dashboard</a>
                    <a href="{url_for('logs.detect_anomalies')}" class="nav-button warning">Anomaly Detection</a>
                </div>
                
                <div class="content-container">
                    <div class="image-container">
                        <img src="data:image/png;base64,{img_b64}" alt="Activity Dashboard" style="max-width:100%; height:auto;">
                    </div>
                    <div class="analysis-container">
                        <h3>Dashboard Analysis</h3>
                        <p style="margin-top: 10px; line-height: 1.6;">
                            This dashboard provides a comprehensive overview of system activity through three complementary visualizations:
                        </p>
                        <ul style="margin-top: 10px; line-height: 1.6; list-style-type: none; padding-left: 0;">
                            <li style="margin-bottom: 8px;"><strong>User Activity (Top Left):</strong> Shows the distribution of actions by user, helping identify the most active users.</li>
                            <li style="margin-bottom: 8px;"><strong>Action Distribution (Top Right):</strong> Displays the percentage breakdown of different action types across the system.</li>
                            <li style="margin-bottom: 8px;"><strong>Activity Timeline (Bottom):</strong> Tracks the volume of actions over time, revealing usage patterns and potential anomalies.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
    return "Error loading logs"

@logs.route("/security-dashboard")
def security_dashboard():
    log_data = load_logs()
    if log_data is not None:
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Filter for security events (failed logins)
        failed_logins = log_data[log_data["action"] == "failed_login"]
        
        # Smaller figure size
        fig = plt.figure(figsize=(10, 8))
        
        # 1. Failed Login Attempts by User
        ax1 = fig.add_subplot(221)
        user_fails = failed_logins["username"].value_counts().head(10)
        user_fails.plot(kind="bar", color="salmon", ax=ax1)
        ax1.set_title("Top 10 Users with Failed Logins", fontsize=12)
        ax1.set_xlabel("Username", fontsize=10)
        ax1.set_ylabel("Failed Attempts", fontsize=10)
        plt.xticks(rotation=45, ha='right', fontsize=8)
        
        # 2. Failed Logins by Time
        ax2 = fig.add_subplot(222)
        failed_logins.set_index("timestamp").resample('H')["action"].count().plot(kind="line", marker='o', color="crimson", ax=ax2)
        ax2.set_title("Failed Login Attempts Over Time", fontsize=12)
        ax2.set_xlabel("Timestamp", fontsize=10)
        ax2.set_ylabel("Failed Attempts", fontsize=10)
        ax2.tick_params(axis='both', which='major', labelsize=8)
        
        # 3. IP Address Distribution for Failed Logins - show fewer IPs
        ax3 = fig.add_subplot(212)
        ip_fails = failed_logins["ip_address"].value_counts().head(10)  # Reduced from 15 to 10
        ip_fails.plot(kind="barh", color="firebrick", ax=ax3)
        ax3.set_title("Top IP Addresses with Failed Logins", fontsize=12)
        ax3.set_xlabel("Number of Failed Attempts", fontsize=10)
        ax3.set_ylabel("IP Address", fontsize=10)
        ax3.tick_params(axis='both', which='major', labelsize=8)
        
        plt.tight_layout(pad=1.5)
        
        img = io.BytesIO()
        plt.savefig(img, format="png", dpi=100)
        img.seek(0)
        img_b64 = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Return HTML with page header, navbar, centered image and security evaluation
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Dashboard</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                body {{
                    background-color: #f8f9fa;
                    color: #343a40;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    text-align: center;
                    color: #212529;
                    margin-bottom: 30px;
                    font-size: 2.5em;
                    font-weight: 700;
                    padding: 15px 0;
                    position: relative;
                    letter-spacing: 1px;
                    display: inline-block;
                    margin-left: auto;
                    margin-right: auto;
                }}
                h1::after {{
                    content: "";
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 100%;
                    height: 3px;
                    background: linear-gradient(to right, #3a506b, #ef476f);
                    border-radius: 2px;
                }}
                .header-container {{
                    text-align: center;
                    width: 100%;
                }}
                .nav-buttons {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-bottom: 30px;
                    justify-content: center;
                }}
                .nav-button {{
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: 600;
                    text-decoration: none;
                    text-align: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    flex: 1;
                    min-width: 180px;
                    max-width: 250px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: #3a506b;
                    color: white;
                }}
                .nav-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 6px 8px rgba(0,0,0,0.2);
                    background-color: #1c2541;
                }}
                .nav-button.primary {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #4361ee;
                }}
                .nav-button.success {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #38b000;
                }}
                .nav-button.warning {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #ff9e00;
                }}
                .nav-button.danger {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #ef476f;
                }}
                .nav-button.info {{
                    background-color: #3a506b;
                    border-bottom: 3px solid #4cc9f0;
                }}
                .content-container {{
                    text-align: center;
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .image-container {{
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    padding: 10px;
                    background: white;
                    border-radius: 8px;
                }}
                .analysis-container {{
                    margin-top: 20px;
                    text-align: left;
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    font-size: 16px;
                }}
                .analysis-container h3 {{
                    color: #3a506b;
                    border-bottom: 1px solid #e9ecef;
                    padding-bottom: 10px;
                    font-size: 20px;
                }}
                .analysis-container p, .analysis-container li {{
                    margin-top: 10px;
                    line-height: 1.7;
                    font-size: 16px;
                }}
                .analysis-container strong {{
                    font-size: 17px;
                    font-weight: 600;
                }}
                .button-container {{
                    margin-top: 20px;
                    text-align: center;
                }}
                .action-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #3a506b;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-right: 10px;
                }}
                .danger-button {{
                    background-color: #ef476f;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header-container">
                    <h1>Security Dashboard</h1>
                </div>
                
                <!-- Navigation Buttons -->
                <div class="nav-buttons">
                    <a href="{url_for('logs.index')}" class="nav-button primary">Home</a>
                    <a href="{url_for('logs.plot')}" class="nav-button success">User Activity Plot</a>
                    <a href="{url_for('logs.dashboard')}" class="nav-button info">Dashboard</a>
                    <a href="{url_for('logs.security_dashboard')}" class="nav-button danger">Security Dashboard</a>
                    <a href="{url_for('logs.detect_anomalies')}" class="nav-button warning">Anomaly Detection</a>
                </div>
                
                <div class="content-container">
                    <div class="image-container">
                        <img src="data:image/png;base64,{img_b64}" alt="Security Dashboard" style="max-width:100%; height:auto;">
                    </div>
                    <div class="analysis-container">
                        <h3>Security Analysis</h3>
                        <p style="margin-top: 10px; line-height: 1.6;">
                            This security dashboard focuses on failed login attempts, which can indicate potential security threats:
                        </p>
                        <ul style="margin-top: 10px; line-height: 1.6; list-style-type: none; padding-left: 0;">
                            <li style="margin-bottom: 8px;"><strong>User-Based Failures (Top Left):</strong> Identifies users with the most failed login attempts, potentially indicating targeted accounts.</li>
                            <li style="margin-bottom: 8px;"><strong>Temporal Patterns (Top Right):</strong> Shows when failed logins occur, helping identify coordinated attack attempts.</li>
                            <li style="margin-bottom: 8px;"><strong>Source IP Analysis (Bottom):</strong> Reveals the IP addresses with the most failed attempts, helping identify potential attackers.</li>
                        </ul>
                        <p style="margin-top: 15px; line-height: 1.6;">
                            <strong>Recommended Actions:</strong> Investigate users and IPs with unusually high failed login counts. Consider implementing additional security measures for frequently targeted accounts.
                        </p>
                    </div>
                    <div class="button-container">
                        <a href="{url_for('logs.index')}" class="action-button">Back to Dashboard</a>
                        <a href="{url_for('logs.detect_anomalies')}" class="action-button danger-button">View Anomalies</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
    return "Error loading logs"

