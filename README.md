# Toastmasters Club Reporter

A Python application that collects club and member data from Toastmasters International APIs and generates comprehensive reports in multiple formats.

## Overview

This tool helps Toastmasters club officers automate the process of gathering member progress data and generating detailed reports. It authenticates with Toastmasters International's web platform, collects data about club members and their pathway progress, and generates reports in markdown, Excel, and PDF formats.

## Features

- **Automated Data Collection**: Pulls club and member information from Toastmasters APIs
- **Multiple Report Formats**: Generates reports in markdown, Excel, and PDF formats
- **Pathway Analysis**: Analyzes member progress across various Toastmasters pathways
- **Configurable Reports**: Customize report generation through configuration settings
- **Session Management**: Handles authentication and session management automatically

## :camera: Report Examples

*See what your club reports will look like with these examples:*

> :bulb: **Note**: Sample data shown with masked member names for privacy. Your reports will display actual member information.

### Interactive HTML Dashboard
<details>
<summary>Open to view HTML Dashboard</summary>

<img width="1587" height="1272" alt="image" src="https://github.com/user-attachments/assets/58f69007-ae6f-4213-8773-cccb8189bc5a" />

*Complete club status with member statistics, enrollment tracking, and pathway distribution*

<img width="1573" height="752" alt="image" src="https://github.com/user-attachments/assets/411b5f28-b18e-46c4-99bf-630a0f28acbb" />

*Expand member progress overview table for pathway breakdown summary*

</details>

### Markdown Report
<details>
<summary>Open to view Markdown Report</summary>

<img width="649" height="759" alt="image" src="https://github.com/user-attachments/assets/363f4ba8-c491-4179-bfad-43bd8dea8a9f" />

*Overall club status with member statistics, pathway distribution, and focused next step summaries*

<img width="687" height="698" alt="image" src="https://github.com/user-attachments/assets/b948fcde-b6cd-46f4-98f2-7f38e3c00b88" />

*Expand member progress section for pathway breakdown summary*

</details>

### Excel Report
<details>
<summary>Open to view Excel Report</summary>

<img width="1195" height="827" alt="image" src="https://github.com/user-attachments/assets/71262730-272b-404e-96df-257e17da97e9" />

*Overall club status with member statistics and pathway distribution in an editable format*

</details>

## Prerequisites

- uv cli OR Python 3.13 or higher
- Toastmasters Officer account (required for API access)
- Internet connection

## Getting Started

### Option 1: Using uv (Recommended)

1. **Install uv**: If you don't have uv installed, follow the [installation guide](https://docs.astral.sh/uv/getting-started/installation/)

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd toastmasters-club-reporter
   ```

3. **Run the application**:
   ```bash
   uv run src/main.py
   ```

### Option 2: Using Standard Python

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd toastmasters-club-reporter
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python src/main.py
   ```

## Initial Setup

On first startup, the application will create a `.env` file with the following required variables:

```env
EMAIL=your-toastmasters-email@example.com
PASSWORD=your-toastmasters-password
CLUB_NAME=Your Club Name
```

**Important**: You must be a Toastmasters Officer to access the APIs. Regular members will be denied access.

## Configuration

The application behavior can be customized through the `src/config/app_settings.py` file:

- **SAVE_ENDPOINT_DATA**: Whether to save raw API response data
- **REPORT_TYPES**: Configure which report formats to generate:
  - `markdown`: Generate markdown reports
  - `excel`: Generate Excel spreadsheets (requires pandas)
  - `pdf`: Generate PDF reports (requires reportlab)

## Output

The application generates the following outputs:

- **Session Data**: Authentication and API response data stored in `session/auth/`
- **Reports**: Generated reports in `session/reports/` directory
- **Summaries**: Club and member summary data in `session/summary/`
- **Logs**: Application logs in `app.log`

## Project Structure

```
├── src/
│   ├── main.py                 # Application entry point
│   ├── api/                    # API client implementations
│   ├── config/                 # Configuration settings
│   ├── log/                    # Logging utilities
│   ├── manager/                # Data and environment managers
│   ├── model/                  # Data models (Club, Member)
│   ├── security/               # Authentication handling
│   ├── service/                # Business logic services
│   └── utils/                  # Report generation utilities
├── pathways/                   # Toastmasters pathway objects (Pathway specifics)
├── session/                    # Runtime data and outputs
└── pyproject.toml              # Python dependencies (uv)
└── requirements.txt            # Python dependencies (python)
```

## Dependencies

- **playwright**: Web automation for authentication
- **openpyxl**: Excel file generation
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for API calls
- **reportlab**: PDF generation
- **pandas**: Data manipulation for Excel reports

## Troubleshooting

- **Authentication Issues**: 
    - Ensure your Toastmasters credentials are correct and you have officer-level access
    - Expire time for session file is 8 hours (you may need to manually delete the `toastmasters_session.json` file if expiration is different)
    - If you receive an API call failed, try re-running the app before attempting other options. Sometimes the connection to the Toastmasters endpoint abruptly terminated.
- **Missing Reports**: 
    - Check the `app_settings.py` file to ensure desired report types are enabled
- **Permission Errors**: 
    - Make sure you have write permissions in the project directory

## License

This project is licensed under the terms specified in the LICENSE file.
