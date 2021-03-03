#!/usr/bin/env bash

cat << EOM

Migrate database for application from "source/run.py" with virtual environment "from .venv"

EOM

export FLASK_APP=source/run.py

. .venv/bin/activate \
	&& echo '[+] Virtual environment activated'

[ ! -d database ] \
	&& mkdir database \
	&& echo '[+] Folder "database" created' \
	&& flask db init \
	&& echo '[+] Application database initiated' \
	|| echo '[-] Folder "database" already exists'

flask db migrate \
	&& echo '[+] Application database migrated' \
	&& flask db upgrade \
	&& echo '[+] Application database upgraded'

deactivate \
	&& echo '[+] Virtual environment deactivated'

echo 'Application database migrating complete.'
