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

        return render_template('plot.html', img_b64=img_b64)
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
        # Make sure timestamp is a datetime type
        if not pd.api.types.is_datetime64_any_dtype(recent_failed["timestamp"]):
            recent_failed["timestamp"] = pd.to_datetime(recent_failed["timestamp"])
        
        # Print the timestamp data for debugging
        print("Timestamp data types:", recent_failed["timestamp"].dtype)
        print("Sample timestamps:", recent_failed["timestamp"].head())
        
        # Extract hour from timestamp for hourly grouping - more explicit format
        recent_failed['hour'] = recent_failed['timestamp'].dt.floor('H').dt.strftime('%Y-%m-%d %H:00')
        
        # Print the grouped data for debugging
        print("Unique hours:", recent_failed['hour'].unique())
        print("Hour counts:", recent_failed['hour'].value_counts().sort_index())
        
        # Group by hour and count
        hourly_counts = recent_failed.groupby('hour').size().reset_index(name='count')
        print("Hourly counts:", hourly_counts)
        
        # Plot the time series
        ax1.plot(range(len(hourly_counts)), hourly_counts['count'], marker='o', color="#ff9e00", linestyle='-')
        
        # Add data labels to each point
        for i, count in enumerate(hourly_counts['count']):
            ax1.annotate(f'{count}', (i, count), textcoords="offset points", 
                        xytext=(0,10), ha='center')
        
        ax1.set_title(f"Failed Login Attempts Over Time (Total: {total_failed_attempts})", 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel("Hour", fontsize=12)
        ax1.set_ylabel("Number of Failed Attempts", fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Format x-axis labels
        ax1.set_xticks(range(len(hourly_counts)))
        ax1.set_xticklabels(hourly_counts['hour'], rotation=45, ha='right', fontsize=8)
        
        # Ensure all data points are visible
        ax1.set_xlim(-0.5, len(hourly_counts) - 0.5)
        
        # Add some padding to y-axis to make room for data labels
        y_max = hourly_counts['count'].max() if not hourly_counts.empty else 1
        ax1.set_ylim(0, y_max * 1.15)
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

        return render_template('dashboard.html', img_b64=img_b64)
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

        return render_template('security-dashboard.html', img_b64=img_b64)
    return "Error loading logs"

