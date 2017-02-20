#!/usr/bin/env bash

set -e

usage() {
  echo "Usage: script.sh $1 $2 $3"
  echo " e.g.: db_url db_user db_pass"
  echo " "
  exit 1
}

if [ -z "$1" ];then
  usage
fi


DB=$1
USER=$2
PASS=$3

cd /usr/local/openvpn_as/scripts

./dbcvt -t certs -s sqlite:////usr/local/openvpn_as/etc/db/certs.db -d mysql://$USER:$PASS@$DB/as_certs
echo "Certs migration complete!"
./dbcvt -t config -s sqlite:////usr/local/openvpn_as/etc/db/config.db -d mysql://$USER:$PASS@$DB/as_config
echo "Config migration complete!"
./dbcvt -t log -s sqlite:////usr/local/openvpn_as/etc/db/log.db -d mysql://$USER:$PASS@$DB/as_log
echo "Log migration complete!"
./dbcvt -t user_prop -s sqlite:////usr/local/openvpn_as/etc/db/userprop.db -d mysql://$USER:$PASS@$DB/as_userprop
echo "User migration complete!"
echo " "
echo "Script complete!"