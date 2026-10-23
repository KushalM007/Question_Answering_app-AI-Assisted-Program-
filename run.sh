#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
streamlit run app/main.py
