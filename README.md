# Overleaf Bibliography Auto-Refresh

This project contains a Python Selenium script that automatically logs into Overleaf using ORCID credentials, navigates to a specified project, and refreshes the bibliography section. The script is designed to be run periodically (e.g., via a CRON job or using GitHub Actions) to ensure that the bibliography is always up to date.

## Features

- Automatically logs into Overleaf via ORCID credentials.
- Navigates to a specified Overleaf project.
- Refreshes the bibliography to sync the latest changes.
- Can be set up to run on GitHub Actions, enabling automated, scheduled bibliography updates.
- Handles cookie consent pop-ups (if they appear).

## Files in this Repository

### `src/refresh.py`

The main Python script that performs the following tasks:

1. **Login to Overleaf**: Uses your ORCID credentials to log into your Overleaf account. Using ORCID credentials bypasses the CAPTCHA that Overleaf natively imposes.
2. **Navigate to the Project**: Navigates to the project specified by URL.
3. **Navigate to the Bibliography**: Locates and navigates to the bibliography file in the selected project.
4. **Refresh the Bibliography**: Clicks the "Refresh" button to update the bibliography.

### `.github/workflows/update_bib.yml`

This GitHub Actions workflow file automates the process of running the Selenium script in a CI/CD pipeline. It:

- Installs the required dependencies (Python, Selenium, ChromeDriver).
- Runs the Selenium script periodically based on the schedule defined or when changes are pushed to the repository.
- Reports the success or failure of the operation in the workflow logs.

### `requirements.txt`

A file containing all the dependencies needed to run the Python script, including:

- `selenium`: For automating web browser interaction.
- `webdriver-manager`: To automatically manage browser drivers.
- `python-dotenv`: For loading environment variables from a `.env` file.

### `.env` (Not included in the repo, needs to be created locally)

A file where you store sensitive information like ORCID credentials. The script uses this to fetch your login details securely.

Example `.env` file:

```env
ORCID_EMAIL=your_orcid_email@example.com
ORCID_PASSWORD=your_orcid_password
```

You need to add these as secrets in your GitHub repo if you're using GitHub Actions. There is a step in the workflow that does this.

### `README.md`

This file, which provides an overview of the project, instructions for setting it up, and usage guidelines.

## Installation & Setup

### Prerequisites

- Python 3.x
- Chrome browser installed (for running Selenium with ChromeDriver).
- ORCID credentials.

### Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/j-jayes/overleaf-bib-refresh.git
   cd your-repo
   ```
2. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Set up the `.env` file with your ORCID credentials:

   ```bash
   echo "ORCID_EMAIL=your_orcid_email@example.com" > .env
   echo "ORCID_PASSWORD=your_orcid_password" >> .env
   ```
4. Run the script locally:

   ```bash
   python src/refresh.py
   ```

### Running with GitHub Actions

This project is designed to run the Selenium script via GitHub Actions, automating the process of refreshing your Overleaf bibliography at regular intervals.

#### Steps:

1. Add your ORCID credentials to **GitHub Secrets**:

   - Go to your repository’s **Settings** > **Secrets and variables** > **Actions**.
   - Click **New repository secret**.
   - Add `ORCID_EMAIL` and `ORCID_PASSWORD` as secrets with your credentials.
2. The workflow is triggered automatically when:

   - Changes are pushed to the repository.
   - The scheduled CRON job triggers (based on the configuration in the `selenium.yml` file).
3. Review the logs of the GitHub Actions workflow to see the status of the script run.

## GitHub Actions Workflow (`.github/workflows/selenium.yml`)

This workflow:

- Runs on push events and at scheduled intervals (e.g., daily at midnight).
- Sets up Python, installs dependencies, and runs the Selenium script.
- Logs success or failure in the GitHub Actions interface.

Here is a summary of what each section does:

- **Set up Python**: Ensures that the runner is using the correct Python version.
- **Install dependencies**: Installs the required packages (Selenium, etc.).
- **Run Selenium script**: Executes the Python script that performs the Overleaf login and bibliography refresh.
- **Report success/failure**: Logs the result of the run and provides feedback on success or failure.

## Handling Cookie Consent

The script includes functionality to handle cookie consent pop-ups that may appear during the login process. It attempts to dismiss the consent banner if it's present. If the banner does not appear (which can vary based on location or session), the script skips this step and continues.

## Known Issues

- **Browser Compatibility**: This script uses Google Chrome and ChromeDriver. Ensure these are installed and properly set up if running locally.

## Future Enhancements

- Improve error handling to retry login in case of failure.
- Support more complex project navigation scenarios (e.g., selecting specific projects by name).
- Add support for running in other browsers (e.g., Firefox via GeckoDriver).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
