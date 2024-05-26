#!/bin/bash

# Function to load environment variables from the secrets file
load_env() {
  if [ -f "$1" ]; then
    export $(grep -v '^#' $1 | xargs)
  else
    echo "Secrets file $1 not found."
    exit 1
  fi
}

# Check if a secrets file is provided
if [ -z "$SECRETS_FILE" ]; then
  echo "No secrets file provided."
  echo "Do you want to generate a new encryption key? (y/n): "
  read generate_key
  if [ "$generate_key" = "y" ]; then
    python generate_key.py --secrets_file secrets.env --key_name ENCRYPTION_KEY
    export SECRETS_FILE=secrets.env
  else
    echo "Exiting. Please provide a secrets file to run the application."
    exit 1
  fi
fi

# Load the secrets from the secrets file
load_env $SECRETS_FILE

# Start the Flask application
exec flask run --host=0.0.0.0
