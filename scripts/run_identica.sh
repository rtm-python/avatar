#!/usr/bin/env bash

cat << EOM

Run identica manually

EOM

export FLASK_APP=source/run.py

. .venv/bin/activate \
	&& flask run-identica \
	&& deactivate
