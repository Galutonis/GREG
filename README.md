# GREG
GREG (Gitlab REport Generator) is a simple python script designed to read from a given gitlab url (provided you have the right API key) and then generate a text file which organises all repos visible from the api key organised by milestone. You can customis further the output via the config.

## Description

This project generates reports from GitLab groups by combing through all projects and repositories to gather detailed information based on milestones. The generated reports provide insights and summaries of the milestones, making it easier to track progress and manage projects effectively.

## Building Script Into an Executable

To build the executable, PyInstaller must be installed first.

1. **Install PyInstaller**:
    ```sh
    pip install pyinstaller
    ```

2. **Build the Executable**:
    ```sh
    pyinstaller --onefile --name Report --icon icons/icon.ico gitlab_report.py
    ```

    This will create an executable in the `dist` folder.

## Configuration.txt File Impact on Executable File Processes

The `configuration.txt` file controls various aspects of the executable file behavior. Here are the details of each parameter:

### verboseMode

- **Description**: Controls the verbosity of the program's output.
- **Impact**:
  - When set to `1`, verbose mode is enabled, and the program will provide detailed output, useful for debugging and monitoring.
  - When set to `0`, verbose mode is disabled, and the program will run with minimal output, suitable for regular operation.

### monthsSinceClosed

- **Description**: Specifies the time frame for displaying closed milestones.
- **Impact**: Determines how far back the program will look for closed milestones. For instance, if set to `3`, the program will display closed milestones from the last three months.

### gitlab_url

- **Description**: The URL of the associated GitLab group.
- **Impact**: Defines the GitLab server endpoint the program will interact with. This URL is essential for connecting to the correct GitLab instance.

### private_token

- **Description**: The private token for API access.
- **Impact**: Provides authentication and authorization for the program to access the GitLab API. This token ensures the program has the necessary permissions to perform actions and retrieve data securely.
