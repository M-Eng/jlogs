"""
Templates for markdown journal entries
"""

def create_daily_hours_chart_image(time_data: dict, output_path: str) -> bool:
    """
    Create a static PNG image of daily work hours chart using matplotlib.
    
    Args:
        time_data: Dictionary mapping dates to work time strings
        output_path: Path to save the PNG file
        
    Returns:
        True if successful, False if matplotlib not available
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime
        import re
    except ImportError:
        return False
    
    # Prepare data for the chart
    dates = []
    hours = []
    
    # Get last 30 days of data
    all_dates = []
    for date_str, work_time in time_data.items():
        if work_time and work_time != "-":
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d")
                match = re.match(r'(\d+(?:\.\d+)?)h?', work_time)
                if match:
                    work_hours = float(match.group(1))
                    all_dates.append((entry_date, work_hours))
            except ValueError:
                continue
    
    if not all_dates:
        return False
    
    # Sort by date and take last 30 days
    all_dates.sort(key=lambda x: x[0])
    recent_dates = all_dates[-30:] if len(all_dates) > 30 else all_dates
    
    for entry_date, work_hours in recent_dates:
        dates.append(entry_date)
        hours.append(work_hours)
    
    if not dates:
        return False
    
    # Create the plot
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot the line chart
    ax.plot(dates, hours, color='#4CAF50', linewidth=3, marker='o', markersize=6, 
            markerfacecolor='#4CAF50', markeredgecolor='white', markeredgewidth=2)
    
    # Fill area under the curve
    ax.fill_between(dates, hours, alpha=0.3, color='#4CAF50')
    
    # Customize the chart
    ax.set_title('Daily Work Hours', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Work Hours', fontsize=12, fontweight='bold')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Format y-axis
    ax.set_ylim(0, max(hours) * 1.1 if hours else 10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}h'))
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add statistics text
    if hours:
        stats_text = f'Total: {sum(hours):.1f}h | Avg: {sum(hours)/len(hours):.1f}h | Best: {max(hours):.1f}h | Days: {len(hours)}'
        ax.text(0.5, 0.95, stats_text, transform=ax.transAxes, ha='center', va='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
                fontsize=10, fontweight='bold')
    
    # Improve layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    return True


def create_weekly_hours_chart_image(time_data: dict, output_path: str) -> bool:
    """
    Create a static PNG image of weekly work hours chart using matplotlib.
    
    Args:
        time_data: Dictionary mapping dates to work time strings
        output_path: Path to save the PNG file
        
    Returns:
        True if successful, False if matplotlib not available
    """
    try:
        import matplotlib.pyplot as plt
        from datetime import datetime
        import re
    except ImportError:
        return False
    
    weekly_data = get_weekly_work_time_data(time_data)
    
    if not weekly_data:
        return False
    
    # Prepare data for the chart
    weeks = []
    hours = []
    
    # Sort by week and take last 12 weeks
    sorted_weeks = sorted(weekly_data.keys())[-12:]
    
    for week_start in sorted_weeks:
        week_data = weekly_data[week_start]
        weeks.append(f"{week_start}")
        hours.append(week_data["total_hours"])
    
    if not weeks:
        return False
    
    # Create the plot
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create bar chart
    bars = ax.bar(weeks, hours, color='#FF6B35', alpha=0.8, edgecolor='#FF6B35', linewidth=2)
    
    # Customize bars
    for bar in bars:
        bar.set_edgecolor('#FF6B35')
        bar.set_linewidth(2)
    
    # Customize the chart
    ax.set_title('Weekly Work Hours', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Week Starting', fontsize=12, fontweight='bold')
    ax.set_ylabel('Work Hours', fontsize=12, fontweight='bold')
    
    # Format x-axis
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Format y-axis
    ax.set_ylim(0, max(hours) * 1.1 if hours else 40)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}h'))
    
    # Add grid
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, hour in zip(bars, hours):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(hours)*0.01,
                f'{hour:.1f}h', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Add statistics text
    if hours:
        stats_text = f'Total: {sum(hours):.1f}h | Avg: {sum(hours)/len(hours):.1f}h | Best: {max(hours):.1f}h | Weeks: {len(hours)}'
        ax.text(0.5, 0.95, stats_text, transform=ax.transAxes, ha='center', va='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
                fontsize=10, fontweight='bold')
    
    # Improve layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    return True

def get_daily_template(date_str: str) -> str:
    """
    Get the daily journal entry template with the given date.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        Formatted markdown template string
    """
    return f"""# 🗓️ {date_str}

## ⏰ Time Tracking

- **Start time**: 
- **End time**: 
- **Extra hours**: 

## ✅ What I accomplished

## 🤔 What didn't go well / blockers

## 📚 What I learned

## 🚀 What to improve
"""

def get_aggregated_table_template(title: str, entries: list) -> str:
    """
    Get the aggregated table template with entries.
    
    Args:
        title: The section title (e.g., "What I accomplished")
        entries: List of (date, entry, comment) tuples
        
    Returns:
        Formatted markdown table string
    """
    if not entries:
        return f"""# {title}

| Date       | Entry                                  | Comment   |
|------------|----------------------------------------|-----------|
"""
    
    table_lines = [f"# {title}", "", "| Date       | Entry                                  | Comment   |", "|------------|----------------------------------------|-----------|"]
    
    prev_date = None
    for date, entry, comment in entries:
        date_display = date if date != prev_date else ""
        comment_display = comment if comment else ""
        table_lines.append(f"| {date_display:10} | {entry:38} | {comment_display:9} |")
        prev_date = date
    
    return "\n".join(table_lines) + "\n"


def calculate_current_week_work_time(time_data: dict) -> str:
    """
    Calculate work time for the current week (Monday to Sunday).
    
    Args:
        time_data: Dictionary mapping dates to work time strings
        
    Returns:
        Current week work time as formatted string
    """
    import re
    from datetime import datetime, timedelta
    
    today = datetime.now().date()  # Get date only, no time component
    # Find the start of this week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    total_hours = 0.0
    valid_entries = 0
    
    for date_str, work_time in time_data.items():
        if work_time and work_time != "-":
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()  # Get date only
                if start_of_week <= entry_date <= end_of_week:
                    # Parse work time string (e.g., "8h", "7.5h")
                    match = re.match(r'(\d+(?:\.\d+)?)h?', work_time)
                    if match:
                        hours = float(match.group(1))
                        total_hours += hours
                        valid_entries += 1
            except ValueError:
                continue
    
    if valid_entries == 0:
        return "-"
    
    # Format total hours
    week_range = f"{start_of_week.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}"
    if total_hours == int(total_hours):
        return f"{int(total_hours)}h ({valid_entries} days, {week_range})"
    else:
        return f"{total_hours:.1f}h ({valid_entries} days, {week_range})"


def get_weekly_work_time_data(time_data: dict) -> dict:
    """
    Get work time data organized by weeks.
    
    Args:
        time_data: Dictionary mapping dates to work time strings
        
    Returns:
        Dictionary mapping week start dates to work time data
    """
    import re
    from datetime import datetime, timedelta
    
    weekly_data = {}
    
    for date_str, work_time in time_data.items():
        if work_time and work_time != "-":
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Find the start of the week (Monday)
                start_of_week = entry_date - timedelta(days=entry_date.weekday())
                week_key = start_of_week.strftime("%Y-%m-%d")
                
                if week_key not in weekly_data:
                    weekly_data[week_key] = {"total_hours": 0.0, "entries": 0, "days": []}
                
                # Parse work time string (e.g., "8h", "7.5h")
                match = re.match(r'(\d+(?:\.\d+)?)h?', work_time)
                if match:
                    hours = float(match.group(1))
                    weekly_data[week_key]["total_hours"] += hours
                    weekly_data[week_key]["entries"] += 1
                    weekly_data[week_key]["days"].append((date_str, hours))
                    
            except ValueError:
                continue
    
    return weekly_data


def create_daily_hours_chart_html(time_data: dict) -> str:
    """
    Create an HTML file with a Chart.js visualization of daily work hours.
    
    Args:
        time_data: Dictionary mapping dates to work time strings
        
    Returns:
        HTML content string
    """
    import re
    from datetime import datetime, timedelta
    
    # Prepare data for the chart
    dates = []
    hours = []
    
    # Get last 30 days of data
    all_dates = []
    for date_str, work_time in time_data.items():
        if work_time and work_time != "-":
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d")
                match = re.match(r'(\d+(?:\.\d+)?)h?', work_time)
                if match:
                    work_hours = float(match.group(1))
                    all_dates.append((entry_date, work_hours))
            except ValueError:
                continue
    
    # Sort by date and take last 30 days
    all_dates.sort(key=lambda x: x[0])
    recent_dates = all_dates[-30:] if len(all_dates) > 30 else all_dates
    
    for entry_date, work_hours in recent_dates:
        dates.append(entry_date.strftime("%Y-%m-%d"))
        hours.append(work_hours)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Work Hours Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .chart-container {{
            padding: 40px;
            position: relative;
            height: 500px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 0 40px 40px 40px;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            border-left: 4px solid #4CAF50;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #4CAF50;
            margin: 0;
        }}
        .stat-label {{
            font-size: 1.1em;
            color: #666;
            margin: 5px 0 0 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Work Hours</h1>
            <p>Visual tracking of your daily work time over the last 30 entries</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <p class="stat-number">{len(hours)}</p>
                <p class="stat-label">Days Tracked</p>
            </div>
            <div class="stat-card">
                <p class="stat-number">{sum(hours):.1f}h</p>
                <p class="stat-label">Total Hours</p>
            </div>
            <div class="stat-card">
                <p class="stat-number">{(sum(hours) / len(hours) if hours else 0):.1f}h</p>
                <p class="stat-label">Average per Day</p>
            </div>
            <div class="stat-card">
                <p class="stat-number">{max(hours) if hours else 0:.1f}h</p>
                <p class="stat-label">Best Day</p>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="dailyChart"></canvas>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('dailyChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {dates},
                datasets: [{{
                    label: 'Work Hours',
                    data: {hours},
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#4CAF50',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#4CAF50',
                        borderWidth: 1,
                        callbacks: {{
                            label: function(context) {{
                                return context.parsed.y + ' hours worked';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: Math.max(...{hours}) + 1,
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value + 'h';
                            }}
                        }}
                    }},
                    x: {{
                        grid: {{
                            display: false
                        }},
                        ticks: {{
                            maxTicksLimit: 10
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    return html_content


def create_weekly_hours_chart_html(time_data: dict) -> str:
    """
    Create an HTML file with a Chart.js visualization of weekly work hours.
    
    Args:
        time_data: Dictionary mapping dates to work time strings
        
    Returns:
        HTML content string
    """
    weekly_data = get_weekly_work_time_data(time_data)
    
    # Prepare data for the chart
    weeks = []
    hours = []
    
    # Sort by week and take last 12 weeks
    sorted_weeks = sorted(weekly_data.keys())[-12:]
    
    for week_start in sorted_weeks:
        week_data = weekly_data[week_start]
        weeks.append(f"Week of {week_start}")
        hours.append(week_data["total_hours"])
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Work Hours Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .chart-container {{
            padding: 40px;
            position: relative;
            height: 500px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 0 40px 40px 40px;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            border-left: 4px solid #FF6B35;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #FF6B35;
            margin: 0;
        }}
        .stat-label {{
            font-size: 1.1em;
            color: #666;
            margin: 5px 0 0 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Weekly Work Hours</h1>
            <p>Weekly aggregated work time over the last 12 weeks</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <p class="stat-number">{len(hours)}</p>
                <p class="stat-label">Weeks Tracked</p>
            </div>
            <div class="stat-card">
                <p class="stat-number">{sum(hours):.1f}h</p>
                <p class="stat-label">Total Hours</p>
            </div>
            <div class="stat-card">
                <p class="stat-number">{(sum(hours) / len(hours) if hours else 0):.1f}h</p>
                <p class="stat-label">Average per Week</p>
            </div>
            <div class="stat-card">
                <p class="stat-number">{max(hours) if hours else 0:.1f}h</p>
                <p class="stat-label">Best Week</p>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="weeklyChart"></canvas>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('weeklyChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {weeks},
                datasets: [{{
                    label: 'Weekly Hours',
                    data: {hours},
                    backgroundColor: 'rgba(255, 107, 53, 0.8)',
                    borderColor: '#FF6B35',
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#FF6B35',
                        borderWidth: 1,
                        callbacks: {{
                            label: function(context) {{
                                return context.parsed.y + ' hours worked';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: Math.max(...{hours}) + 5,
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value + 'h';
                            }}
                        }}
                    }},
                    x: {{
                        grid: {{
                            display: false
                        }},
                        ticks: {{
                            maxRotation: 45
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    return html_content


def get_readme_template(aggregated_data: dict) -> str:
    """
    Get the main README template with aggregated data and links.
    
    Args:
        aggregated_data: Dictionary mapping section names to lists of (date, entry, comment) tuples
        
    Returns:
        Formatted README markdown string
    """
    # Count total entries
    total_entries = sum(len(entries) for entries in aggregated_data.values() if isinstance(entries, list))
    
    # Get all unique dates (sorted in reverse order - most recent first)
    all_dates = set()
    for section_name, entries in aggregated_data.items():
        if isinstance(entries, list):  # Skip time_tracking dict
            for date, _, _ in entries:
                all_dates.add(date)
    sorted_dates = sorted(all_dates, reverse=True)
    
    # Calculate current streak
    current_streak = calculate_current_streak(sorted_dates)
    
    # Calculate total work time and current week work time
    time_data = aggregated_data.get("time_tracking", {})
    total_work_time = calculate_total_work_time(time_data)
    current_week_work_time = calculate_current_week_work_time(time_data)
    
    # Create the README content
    readme_content = f"""# 📝 Journal

Welcome to my personal journal! This repository contains my daily learning and reflection entries.

## 📊 Overview

- **Total entries**: {total_entries}
- **Days logged**: {len(sorted_dates)}
- **Latest entry**: {sorted_dates[0] if sorted_dates else 'No entries yet'}
- **Current streak**: {current_streak} days 🔥
- **Current week work time**: {current_week_work_time}
- **Total work time**: {total_work_time}

## 🗂️ Quick Links

### Aggregated Summaries
- [✅ What I accomplished](aggregated/accomplished.md)
- [🤔 What didn't go well / blockers](aggregated/blockers.md)
- [📚 What I learned](aggregated/learned.md)
- [🚀 What to improve](aggregated/improve.md)

### Latest Entries
"""
    
    # Add latest entries table with reverse chronological order and streak info
    if sorted_dates:
        readme_content += """
| Date       | Entry | Work Time | Streak |
|------------|-------|-----------|--------|
"""
        
        # Generate table rows with breaks inserted
        table_rows = generate_table_rows_with_breaks(sorted_dates, aggregated_data)
        
        # Add all table rows
        for row in table_rows:
            readme_content += row + "\n"
    
    # Add visualization section with static images for GitHub viewing
    readme_content += """
### 📈 Work Time Visualizations

#### 📊 Daily Work Hours
![Daily Work Hours](visualizations/daily_hours.png)

#### 📈 Weekly Work Hours  
![Weekly Work Hours](visualizations/weekly_hours.png)

#### 🔗 Interactive Charts
For interactive charts with hover details and animations:
- [📊 **Interactive Daily Chart**](visualizations/daily_hours.html) - Click for interactive version
- [📈 **Interactive Weekly Chart**](visualizations/weekly_hours.html) - Click for interactive version

*Note: Interactive HTML charts work best when viewing locally or via GitHub Pages*

"""
    
    readme_content += """
## 🚀 Usage

This journal is managed using the `jlog` CLI tool:

- `jlog init` - Initialize a new journal
- `jlog today` - Create today's entry
- `jlog aggregate` - Update aggregated summaries
- `jlog push` - Aggregate and push to git

---

*Generated automatically by jlog*
"""
    
    return readme_content


def calculate_current_streak(sorted_dates: list) -> int:
    """
    Calculate the current streak from the most recent date.
    
    Args:
        sorted_dates: List of date strings in reverse chronological order (most recent first)
        
    Returns:
        Current streak length in days
    """
    from datetime import datetime, timedelta
    
    if not sorted_dates:
        return 0
    
    streak = 1
    
    for i in range(1, len(sorted_dates)):
        current_date = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
        previous_date = datetime.strptime(sorted_dates[i-1], "%Y-%m-%d")
        expected_date = previous_date - timedelta(days=1)
        
        if current_date == expected_date:
            # Consecutive day - continue streak
            streak += 1
        else:
            # Break in streak - stop counting
            break
    
    return streak


def calculate_total_work_time(time_data: dict) -> str:
    """
    Calculate total work time from time tracking data.
    
    Args:
        time_data: Dictionary mapping dates to work time strings
        
    Returns:
        Total work time as formatted string
    """
    import re
    
    total_hours = 0.0
    valid_entries = 0
    
    for date, work_time in time_data.items():
        if work_time and work_time != "-":
            # Parse work time string (e.g., "8h", "7.5h")
            match = re.match(r'(\d+(?:\.\d+)?)h?', work_time)
            if match:
                hours = float(match.group(1))
                total_hours += hours
                valid_entries += 1
    
    if valid_entries == 0:
        return "-"
    
    # Format total hours
    if total_hours == int(total_hours):
        return f"{int(total_hours)}h ({valid_entries} days)"
    else:
        return f"{total_hours:.1f}h ({valid_entries} days)"


def generate_table_rows_with_breaks(sorted_dates: list, aggregated_data: dict) -> list:
    """
    Generate table rows with break indicators inserted.
    
    Args:
        sorted_dates: List of date strings in reverse chronological order (most recent first)
        aggregated_data: Dictionary containing time tracking data
        
    Returns:
        List of table row strings
    """
    from datetime import datetime, timedelta
    
    if not sorted_dates:
        return []
    
    table_rows = []
    
    # Extract time data from aggregated_data if available
    time_data = aggregated_data.get("time_tracking", {})
    
    # Pre-calculate all streak groups and their lengths
    streak_groups = []
    current_group = []
    
    for i in range(len(sorted_dates)):
        current_date = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
        
        if i == 0:
            # First date (most recent)
            current_group = [sorted_dates[i]]
        else:
            previous_date = datetime.strptime(sorted_dates[i-1], "%Y-%m-%d")
            expected_date = previous_date - timedelta(days=1)
            
            if current_date == expected_date:
                # Consecutive day - add to current group
                current_group.append(sorted_dates[i])
            else:
                # Break in streak - save current group and start new one
                if current_group:
                    streak_groups.append(current_group)
                current_group = [sorted_dates[i]]
    
    # Add the last group
    if current_group:
        streak_groups.append(current_group)
    
    # Now generate table rows with correct streak values
    for group_idx, group in enumerate(streak_groups):
        group_length = len(group)
        
        for i, date in enumerate(group):
            current_date = datetime.strptime(date, "%Y-%m-%d")
            
            # Get work time for this date
            work_time = time_data.get(date, "-")
            
            # Calculate streak value: oldest gets 1, most recent gets group_length
            streak_value = group_length - i
            
            entry_link = f"[{date}](entries/{date}.md)"
            streak_text = f"🔥 {streak_value}"
            table_rows.append(f"| {date} | {entry_link} | {work_time} | {streak_text} |")
            
            # Insert break indicator after this group (except for the last group)
            if i == len(group) - 1 and group_idx < len(streak_groups) - 1:
                # Calculate break length to next group
                next_group_date = datetime.strptime(streak_groups[group_idx + 1][0], "%Y-%m-%d")
                break_length = (current_date - next_group_date).days - 1
                if break_length > 0:
                    table_rows.append(f"| | | | ⏸️ **Break: {break_length} days** |")
    
    return table_rows


def format_section_for_table(entries: list) -> str:
    """
    Format section entries for display in a table cell.
    
    Args:
        entries: List of (entry, comment) tuples
        
    Returns:
        Formatted string for table cell
    """
    if not entries:
        return "-"
    
    # Show up to 2 entries, truncate if longer
    formatted_entries = []
    for i, (entry, comment) in enumerate(entries[:2]):
        if len(entry) > 25:
            entry = entry[:22] + "..."
        if comment:
            entry = f"{entry} [{comment}]"
        formatted_entries.append(entry)
    
    if len(entries) > 2:
        formatted_entries.append(f"... +{len(entries) - 2} more")
    
    return "<br>".join(formatted_entries) 