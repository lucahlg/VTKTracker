# VTK Homestay Availability Tracker

This project automates the checking of room availability for **VTK Homestay Sapa** on specific dates. It runs every hour via GitHub Actions and sends notifications to [ntfy.sh](https://ntfy.sh) if a room matching "Mountain View" or "Deluxe" is found.

## Features
- **Automated Checks**: Runs hourly using GitHub Actions cron schedule.
- **Headless Browser**: Uses Playwright to render the dynamic booking site.
- **Notifications**: Sends alerts to `ntfy.sh/vtk_homestay_tracker`.

## Setup

### 1. Local Development
1. Clone the repository.
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
4. Run the script:
   ```bash
   python check_availability.py
   ```

### 2. GitHub Actions
The workflow is defined in `.github/workflows/scheduler.yml`. It will automatically run on schedule once pushed to GitHub.

## Configuration
- **Dates**: Modify `DATES_TO_CHECK` list in `check_availability.py`.
- **Keywords**: Modify `KEYWORDS` list in `check_availability.py`.
- **Target URL**: Configured in `BASE_URL` and `HOTEL_CODE`.
