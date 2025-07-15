# jlog - A Markdown-based CLI Journaling Tool

A simple command-line tool for managing daily journal entries in markdown format with git integration.

## Features

- **Daily entries**: Create daily journal entries with predefined templates
- **Aggregation**: Extract and organize entries by category into markdown tables
- **Git integration**: Automatic git commit and push functionality
- **Simple setup**: Interactive initialization with folder structure creation

## Installation

```bash
pip install .
```

## Usage

### Initialize a new journal

```bash
jlog init
```

### Create today's entry

```bash
jlog today
```

### Aggregate all entries

```bash
jlog aggregate
```

### Commit and push changes

```bash
jlog push
```

## Requirements

- Python 3.8+
- Git (for version control features)

## License

MIT License 