#!/usr/bin/env bash

cat << EOM

Run application manually

EOM

. .venv/bin/activate \
	&& python source/run.py \
	&& deactivate
