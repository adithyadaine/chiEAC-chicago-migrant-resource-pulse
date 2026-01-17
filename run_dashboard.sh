#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src/dashboard
streamlit run src/dashboard/app.py
