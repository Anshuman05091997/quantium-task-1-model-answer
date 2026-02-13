#!/bin/bash
# CI script: Runs the Dash app test suite.
# Exit 0 if all tests pass, 1 otherwise.

set -e  # Exit immediately if any command fails

# Get the directory where this script lives (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    if command -v python3 &> /dev/null; then
        python3 -m venv venv
    else
        python -m venv venv
    fi
fi

# Activate virtual environment (Linux/Mac vs Windows)
echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Error: Could not find virtual environment activate script"
    exit 1
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run the test suite
echo "Running test suite..."
pytest test_app.py -v --headless

# pytest returns 0 on success, 1 on failure - we pass that through
exit $?
