#!/bin/bash

# Exit on any error
set -e

# Define AWS variables
DOMAIN="stock-analyser"
DOMAIN_OWNER="108782078484"
REGION="eu-north-1"  # Replace with your AWS region if different
REPO="stock_analyser_lib"

# Get CodeArtifact token
# aws codeartifact get-authorization-token --domain stock-analyser --domain-owner 108782078484 -
CODEARTIFACT_AUTH_TOKEN=$(aws codeartifact get-authorization-token --domain $DOMAIN --domain-owner $DOMAIN_OWNER --query authorizationToken --output text --region $REGION)

# Update pip config to use CodeArtifact
pip config set global.index-url https://aws:$CODEARTIFACT_AUTH_TOKEN@$DOMAIN-$DOMAIN_OWNER.d.codeartifact.$REGION.amazonaws.com/pypi/$REPO/simple/

# Print a message
echo "✅ Pip config updated with CodeArtifact repository."

# Activate virtual environment
# source /home/zaki/finance_apps/stock_analyser_lib_parent/venv-lib/bin/activate

# Install dependencies if needed
# pip install --upgrade pip
# pip install -r requirements.txt

# Run main.py
#pip install -e 
