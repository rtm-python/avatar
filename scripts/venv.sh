#!/usr/bin/env bash

cat << EOM

Initiate virtual environment (use --initial/-i to create blank web venv)

EOM

while [ $# -gt 0 ]; do
	case "$1" in
		--initial*|-v*)
			if [[ "$1" != *=* ]]; then shift; fi
			INITIAL=true
			;;
		*)
	esac
	shift
done

[ ! -d .venv ] \
	&& python3 -m venv .venv \
	&& echo '[+] Virtual environment ".venv" created' \
	|| echo '[-] Virtual environment ".venv" already exists'

. .venv/bin/activate \
	&& pip install --upgrade pip \
	&& pip install wheel

if [ ! -z $INITIAL ]
then
	pip install flask flask-login flask-paranoid flask-wtf flask-sqlalchemy flask-migrate \
		&& pip install requests uwsgi flask-socketio gevent gevent-websocket pillow opencv-python \
		&& pip freeze > requirements.txt \
		&& deactivate \
		&& echo '[+] Virtual environment ".venv" initiated (freezed to requirements.txt)'
else
	pip install -r requirements.txt \
		&& deactivate \
		&& echo '[+] Virtual environment ".venv" initiated (loaded from requirements.txt)'
fi
