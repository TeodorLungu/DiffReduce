#!/bin/bash

# Check for Conda installation
if ! command -v conda &> /dev/null
then
    echo "Conda could not be found, please install it first."
    exit 1
fi

# Prompt the user for the environment name
read -p "Enter the name of the Conda environment: " env_name

# Check if the environment already exists
env_exists=$(conda info --envs | awk '{print $1}' | grep "^$env_name$")

if [ "$env_exists" ]; then
    echo "An environment named '$env_name' already exists."
    read -p "Do you want to use this existing environment? (y/n): " use_existing
    if [[ $use_existing != "y" ]]; then
        echo "Setup aborted. Please rerun the script and choose another environment name or use the existing one."
        exit 0
    fi
else
    # Create Conda environment with specified Python version
    conda create -n "$env_name" python=3.10.13 -y
fi

# Activate the environment
echo "Activating the environment $env_name..."
eval "$(conda shell.bash hook)"
conda activate "$env_name"

# Confirm continuation with installation of dependencies
read -p "Install Python dependencies from requirements.txt? (y/n): " install_deps
if [[ $install_deps == "y" ]]; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "requirements.txt not found. Please ensure it's in the current directory."
        exit 1
    fi
fi

# Create .env file inside the dash_app subdirectory
mkdir -p dash_app  # Create the directory if it does not exist
cat > dash_app/.env << EOF
BASE_DIR_FALLBACK=/path/to/fallback/data
BASE_DIR_FULL=/path/to/full/data
EOF

echo "A template .env file has been created in the dash_app directory. Please update it with your actual paths."

echo "Setup is complete."

# Final activation of the environment
conda activate "$env_name"

