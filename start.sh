#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d venv ]; then
    echo "Setu hasn't been set up yet. Run ./setup.sh first."
    exit 1
fi

source venv/bin/activate
echo "Starting Setu..."
( sleep 1.5 && open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null ) &
python app.py
