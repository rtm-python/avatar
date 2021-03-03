#!/usr/bin/env bash

cat << EOM

Configurate application from "secrets/deployment.json"

EOM

while [ $# -gt 0 ]; do
	case "$1" in
		--version*|-v*)
			if [[ "$1" != *=* ]]; then shift; fi
			VERSION="${1#*=}"
			;;
		*)
	esac
	shift
done

[ ! -f secrets/deployment.json ] \
	&& echo '[-] Deployment data not found' \
	&& echo 'Application configurating fail.' \
	&& exit \
	|| echo '[+] Deployment data found'

[ ! -d config ] \
	&& mkdir config \
	&& echo '[+] Folder "config" created' \
	|| echo '[-] Folder "config" already exists'

[ -f config/app.json ] \
	&& echo '[-] File "config/app.json" already exists' \
	&& echo 'Application configurating fail.' \
	&& exit

config=$(jq '.data[] | select(.version == "'$VERSION'")' secrets/deployment.json)
[ -z "$config" ] \
	&& echo '[-] Deployment data for version "'"$VERSION"'" not found' \
	&& echo 'Application configurating fail.' \
	&& exit

echo "$config" > config/app.json \
	&& echo '[+] File "config/app.json" created'

echo 'Application configurating complete.'
