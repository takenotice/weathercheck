try {
    # Define the local directory for the virtual environment
    $localEnvPath = "$env:USERPROFILE\python\weathercheck_env"

    # Navigate to the shared folder where the app resides
    $appPath = "\\server2k12\Public\IT\Scripts\weathercheck"
    cd $appPath

    # Create a virtual environment in the user's local directory if it doesn't exist
    if (!(Test-Path -Path $localEnvPath)) {
        Write-Output "Creating virtual environment in $localEnvPath..."
        python -m venv $localEnvPath
    }

    # Activate the virtual environment
    Write-Output "Activating virtual environment..."
    & "$localEnvPath\Scripts\Activate.ps1"

    # Install dependencies using python -m pip
    Write-Output "Installing dependencies..."
    python -m pip install -r requirements.txt

    # Run the app
    Write-Output "Running the app..."
    python main.py
} catch {
    Write-Error "An error occurred: $_"
}