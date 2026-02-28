# The L Project

A Python tool that downloads rejection emails from your Gmail inbox and analyzes patterns in them, including common phrases, time of day distribution, and most frequent sender names, then generates visualizations (charts) to help understand rejection trends.

## Features

- Downloads rejection emails from Gmail using the Gmail API
- Analyzes common phrases in rejection emails
- Shows distribution of rejection emails by time of day
- Identifies most common email sender names
- Generates visualizations (charts)

## Setup

1. Create a project in Google Cloud Console
2. Enable Gmail API
3. Download OAuth credentials (credentials.json)
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python l.py` to download emails and then `python analysis.py` to plot the charts

## Files

- `l.py` - Main script to download emails from Gmail
- `analysis.py` - Analyzes downloaded emails and generates charts
- `phrases.py` - List of rejection phrases to search for
- `rejection_messages_full.json` - Downloaded email data (generated)
- `phrases.png` - Phrase frequency chart (generated)
- `times.png` - Time distribution chart (generated)
- `sender_names.png` - Top sender names chart (generated)
