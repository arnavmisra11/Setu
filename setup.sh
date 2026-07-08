#!/bin/bash
cd "$(dirname "$0")"
echo "Setting up Setu for the first time..."
echo

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo
    echo "IMPORTANT: open the .env file in a text editor and paste your Sarvam API key in it."
    echo "Then run ./start.sh to launch Setu."
else
    echo
    echo "Setup complete. Run ./start.sh to launch Setu."
fi
