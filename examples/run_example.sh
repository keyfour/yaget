#!/bin/bash

# Navigate to the example project directory
cd $(dirname "$0")/simple_project
# Run Yaget on the example project
python ../../yaget.py . --before_lines 2 --dotenv_path $(pwd)/.env

