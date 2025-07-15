"""
Markdown parsing utilities for journal entries
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def parse_time_tracking(content: str) -> Dict[str, Optional[str]]:
    """
    Parse time tracking information from markdown content.
    
    Args:
        content: Markdown content as string
        
    Returns:
        Dictionary with start_time, end_time, and worked_hours
    """
    time_data = {
        "start_time": None,
        "end_time": None,
        "extra_hours": None
    }
    
    # Find time tracking section
    time_section_match = re.search(r"##\s*⏰\s*Time Tracking(.*?)(?=##|$)", content, re.DOTALL | re.IGNORECASE)
    if not time_section_match:
        return time_data
    
    time_section = time_section_match.group(1)
    
    # Parse start time
    start_match = re.search(r"Start time\*?\*?:\s*([^\n\r]+)", time_section, re.IGNORECASE)
    if start_match:
        start_time = start_match.group(1).strip()
        if start_time and start_time != "":
            time_data["start_time"] = start_time
    
    # Parse end time
    end_match = re.search(r"End time\*?\*?:\s*([^\n\r]+)", time_section, re.IGNORECASE)
    if end_match:
        end_time = end_match.group(1).strip()
        if end_time and end_time != "":
            time_data["end_time"] = end_time
    
    # Parse extra hours
    extra_match = re.search(r"Extra hours\*?\*?:\s*([^\n\r]+)", time_section, re.IGNORECASE)
    if extra_match:
        extra_hours = extra_match.group(1).strip()
        if extra_hours and extra_hours != "":
            time_data["extra_hours"] = extra_hours
    
    return time_data


def calculate_work_time(start_time: str, end_time: str, extra_hours: Optional[str] = None) -> str:
    """
    Calculate work time based on start/end times plus extra hours.
    Formula: finish - start - 1 + extra_hours
    
    Args:
        start_time: Start time string (e.g., "09:00", "9:00 AM")
        end_time: End time string (e.g., "17:00", "5:00 PM")
        extra_hours: Optional extra hours string (e.g., "2h", "1.5")
        
    Returns:
        Formatted work time string
    """
    # If start or end time is missing, return dash
    if not start_time or not end_time:
        return "-"
    
    try:
        # Parse time formats (support both 24h and 12h formats)
        start_dt = parse_time_string(start_time)
        end_dt = parse_time_string(end_time)
        
        if start_dt is None or end_dt is None:
            return "-"
        
        # Calculate duration
        if end_dt < start_dt:
            # Handle case where end time is next day
            end_dt += timedelta(days=1)
        
        duration = end_dt - start_dt
        base_hours = duration.total_seconds() / 3600
        
        # Apply formula: finish - start - 1 + extra_hours
        work_hours = max(0, base_hours - 1)
        
        # Add extra hours if provided
        if extra_hours:
            extra_hours_clean = extra_hours.strip()
            if extra_hours_clean:
                # Parse extra hours (e.g., "2h", "1.5", "0.5h")
                import re
                match = re.match(r'(\d+(?:\.\d+)?)h?', extra_hours_clean)
                if match:
                    extra_value = float(match.group(1))
                    work_hours += extra_value
        
        # Format as hours with one decimal place if needed
        if work_hours == int(work_hours):
            return f"{int(work_hours)}h"
        else:
            return f"{work_hours:.1f}h"
            
    except Exception:
        return "-"


def parse_time_string(time_str: str) -> Optional[datetime]:
    """
    Parse a time string into a datetime object.
    
    Args:
        time_str: Time string in various formats
        
    Returns:
        datetime object or None if parsing fails
    """
    time_str = time_str.strip()
    
    # Common time formats to try
    formats = [
        "%H:%M",      # 24-hour format: 09:00, 17:30
        "%I:%M %p",   # 12-hour format: 9:00 AM, 5:30 PM
        "%I:%M%p",    # 12-hour format without space: 9:00AM, 5:30PM
        "%H.%M",      # 24-hour with dot: 09.00, 17.30
        "%H",         # Just hour: 9, 17
        "%I %p",      # Just hour with AM/PM: 9 AM, 5 PM
    ]
    
    for fmt in formats:
        try:
            # Use a base date for parsing
            base_date = datetime(2000, 1, 1)
            parsed_time = datetime.strptime(time_str, fmt)
            # Combine with base date
            return base_date.replace(hour=parsed_time.hour, minute=parsed_time.minute)
        except ValueError:
            continue
    
    return None


def parse_entry_sections(content: str) -> Dict[str, List[Tuple[str, str]]]:
    """
    Parse markdown content and extract sections.
    
    Args:
        content: Markdown content as string
        
    Returns:
        Dictionary mapping section names to lists of (entry_text, comment) tuples
    """
    sections = {
        "accomplished": [],
        "blockers": [],
        "learned": [],
        "improve": []
    }
    
    # Define section patterns
    section_patterns = {
        "accomplished": r"##\s*✅\s*What I accomplished",
        "blockers": r"##\s*🤔\s*What didn't go well / blockers",
        "learned": r"##\s*📚\s*What I learned",
        "improve": r"##\s*🚀\s*What to improve"
    }
    
    for section_key, pattern in section_patterns.items():
        # Find the section header
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            start_pos = match.end()
            
            # Find the next section header or end of content
            next_section_pos = len(content)
            for other_pattern in section_patterns.values():
                if other_pattern != pattern:
                    next_match = re.search(other_pattern, content[start_pos:], re.IGNORECASE)
                    if next_match:
                        next_section_pos = min(next_section_pos, start_pos + next_match.start())
            
            # Extract content between this section and the next
            section_content = content[start_pos:next_section_pos].strip()
            
            # Parse entries from the section
            entries = parse_section_entries(section_content)
            sections[section_key] = entries
    
    return sections


def parse_section_entries(section_content: str) -> List[Tuple[str, str]]:
    """
    Parse entries from a section content.
    
    Args:
        section_content: The content of a section
        
    Returns:
        List of (entry_text, comment) tuples
    """
    entries = []
    
    # Split into lines and process each line
    lines = section_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Remove markdown list markers
        line = re.sub(r'^\s*[-*+]\s*', '', line)
        line = re.sub(r'^\s*\d+\.\s*', '', line)
        
        if line:
            # Check for comments in brackets
            comment_match = re.search(r'\[(.*?)\]', line)
            if comment_match:
                comment = comment_match.group(1)
                entry_text = line.replace(comment_match.group(0), '').strip()
            else:
                comment = ""
                entry_text = line
            
            if entry_text:
                entries.append((entry_text, comment))
    
    return entries


def get_date_from_filename(filename: str) -> str:
    """
    Extract date from filename in YYYY-MM-DD format.
    
    Args:
        filename: Filename like "2025-07-15.md"
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        return date_match.group(1)
    return filename.replace('.md', '')


def parse_journal_entries(entries_dir: Path) -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Parse all journal entries and organize by section.
    
    Args:
        entries_dir: Path to the entries directory
        
    Returns:
        Dictionary mapping section names to lists of (date, entry, comment) tuples
        and time_tracking mapping dates to work time strings
    """
    aggregated = {
        "accomplished": [],
        "blockers": [],
        "learned": [],
        "improve": [],
        "time_tracking": {}
    }
    
    # Process each markdown file in the entries directory
    for entry_file in sorted(entries_dir.glob("*.md")):
        date_str = get_date_from_filename(entry_file.name)
        
        try:
            content = entry_file.read_text(encoding='utf-8')
            sections = parse_entry_sections(content)
            
            # Add entries to aggregated data
            for section_key, entries in sections.items():
                for entry_text, comment in entries:
                    aggregated[section_key].append((date_str, entry_text, comment))
            
            # Parse time tracking information
            time_data = parse_time_tracking(content)
            work_time = calculate_work_time(
                time_data["start_time"],
                time_data["end_time"],
                time_data["extra_hours"]
            )
            aggregated["time_tracking"][date_str] = work_time
            
        except Exception as e:
            print(f"Warning: Could not parse {entry_file.name}: {e}")
    
    return aggregated 