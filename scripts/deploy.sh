#!/usr/bin/env bash

cat << EOM

Deploy application with creating wsgi ini-file and systemd unit-file

EOM

while [ $# -gt 0 ]; do
	case "$1" in
		--clear*|-c*)
			if [[ "$1" != *=* ]]; then shift; fi
			CLEAR=true
			;;
		*)
	esac
	shift
done

[ ! -f deployment.json ] \
	&& echo '[-] Deployment data not found' \
	&& echo 'Application deployment fail.' \
	&& exit \
	|| echo '[+] Deployment data found'

# Initiate virtual environment, configuration and database

scripts/venv.sh && scripts/config.sh --version production && scripts/migrate.sh

cat << EOM

Continue deploy application with creating wsgi ini-file and systemd unit-file

EOM

# Serivce (WSGI)

name=$(jq -r '.name' deployment.json)
desc=$(jq -r '.desc' deployment.json)

[ ! -f config/app.ini ] \
	&& jq -r '.wsgi[]' deployment.json > config/app.ini \
	&& echo '[+] Application WSGI ini-file "config/app.ini" created' \
	|| echo '[-] Application WSGI ini-file "config/app.ini" already exists'

[ ! -f config/"$name".service ] \
	&& output=$(jq -r '.service[]' deployment.json) \
	&& output=${output/\$desc/"$desc"} \
	&& output=${output/\$user/$(whoami)} \
	&& output=${output/\$workdir/$(pwd)} \
	&& output=${output/\$bindir/$(pwd)"/.venv/bin"} \
	&& output=${output/\$exec/$(pwd)"/.venv/bin/uwsgi --ini config/app.ini"} \
	&& echo "$output" > config/"$name".service \
	&& echo '[+] Application systemd unit-file "config/'"$name"'.service" created' \
	|| echo '[-] Application systemd unit-file "config/'"$name"'.service" already exists'

[ ! -z $CLEAR ] \
	&& : > deployment.json \
	&& rm deployment.json \
	&& echo '[+] Deployment data cleared' \
	|| echo '[!] Deployment data not cleared'

echo 'Application deployment complete.'
