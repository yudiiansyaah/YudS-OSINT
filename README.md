# YudS-OSINT

YudS-OSINT is an Open Source Intelligence (OSINT) tool built with Python, leveraging various libraries to assist users in gathering information from multiple sources. This project is designed to be user-friendly for both beginners and professionals.

## Screenshot
![Main Display](screenshot/main-display.png)

## Key Features
- Integration with multiple APIs via `api_integration.py`.
- Data analysis using `pandas`, `plotly`, and `streamlit`.
- Customizable settings through `config.py`.
- Task automation using `schedule`.

## Prerequisites
Ensure you have the following before starting:
- **Python** version 3.8 or later.
- **Git** to clone the repository.
- **Virtual environment** to isolate project dependencies.

## Installation Steps
Follow the steps below according to your operating system.
YudS-OSINT supports *Linux*, *macOS*, and *Windows*.

## Linux/macOS
1. **Install Git**
   
   - *Open Terminal and use the following commands based on your distribution:*
     
     **Debian/Ubuntu**:
     ```bash
     sudo apt install git
     ```
     **Fedora**:
     ```bash
     sudo dnf install git
     ```
     **Arch Linux**:
     ```bash
     sudo pacman -S git
     ```
     **macOS**:
     ```bash
     brew install git
     ```

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yudiiansyaah/YudS-OSINT.git
   cd YudS-OSINT
   ```

3. **Create and Activate a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**
- To run the API with Uvicorn:
  ```bash
  cd api
  python3 my_api.py
  ```
- To start the application:
  
- *Open a new terminal:*
  ```bash
  cd YudS-OSINT
  streamlit run main.py
  ```

## Windows
1. **Install Git**
   ```cmd
   winget install --id Git.Git -e --source winget
   ```

2. **Clone the Repository**
   ```cmd
   git clone https://github.com/yudiiansyaah/YudS-OSINT.git
   cd YudS-OSINT
   ```

3. **Create and Activate a Virtual Environment**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

5. **Run the Application**
- To run the API with Uvicorn:
  ```cmd
  cd api
  python my_api.py
  ```
- To start the application:
  
- Open a new Command Prompt:
  ```cmd
  cd YudS-OSINT
  streamlit run main.py
  ```

## Troubleshooting

### Dependency Installation Issues
- Ensure you are using the correct Python version.
- Try updating `pip`:
  ```bash
  pip install --upgrade pip
  ```

### Application Execution Issues
- Ensure the virtual environment is activated before running commands:
  - **Linux/macOS**:
    ```bash
    source venv/bin/activate
    ```
  - **Windows**:
    ```cmd
    venv\Scripts\activate
    ```
- Verify the configuration in `config.py`.

### API Not Running
- Ensure the port used by Uvicorn is not occupied by another application.
- Run the API on a specific port:
  ```bash
  uvicorn api_integration:app --reload --port 8080
  ```

## Directory Structure
```
YudS-OSINT/
|-- __pycache__/          # Compiled Python files
|-- api/                  # API-related files and folders
|-- Screenshoot/          # Additional or redundant screenshot folder
|-- LICENSE               # License file
|-- README.md             # Existing README file
|-- api_integration.py    # API integration module
|-- async_utils.py        # Utilities for asynchronous operations
|-- config.py             # Configuration settings
|-- core_functions.py     # Core functional components
|-- extra_functions.py    # Additional functions
|-- main.py               # Main application file
|-- requirements.txt      # Python dependencies
|-- thread_utils.py       # Thread-based utilities
|-- utils.py              # General utility functions
```

## Contribution
We welcome contributions to this project. Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the [MIT License](LICENSE).

