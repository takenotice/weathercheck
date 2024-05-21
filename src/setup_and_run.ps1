try {
    # Navigate to the shared folder
    cd "\\server2k12\Public\IT\Scripts\weathercheck"

    # Create a virtual environment if it doesn't exist
    if (!(Test-Path -Path ".\myenv")) {
        Write-Output "Creating virtual environment..."
        python -m venv myenv
    }

    # Activate the virtual environment
    Write-Output "Activating virtual environment..."
    & .\myenv\Scripts\Activate.ps1

    # Install dependencies
    Write-Output "Installing dependencies..."
    pip install -r requirements.txt

    # Run the app
    Write-Output "Running the app..."
    python main.py
} catch {
    Write-Error "An error occurred: $_"
}
