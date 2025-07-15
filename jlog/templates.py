"""
Templates for markdown journal entries
"""

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
    
    # Calculate total work time
    time_data = aggregated_data.get("time_tracking", {})
    total_work_time = calculate_total_work_time(time_data)
    
    # Create the README content
    readme_content = f"""# 📝 Journal

Welcome to my personal journal! This repository contains my daily learning and reflection entries.

## 📊 Overview

- **Total entries**: {total_entries}
- **Days logged**: {len(sorted_dates)}
- **Latest entry**: {sorted_dates[0] if sorted_dates else 'No entries yet'}
- **Current streak**: {current_streak} days 🔥
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