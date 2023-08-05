#!/bin/sh
#
# This script creates a stunnel certificate for https
# and starts a tunnel from :80 to :443. It's meant as en example so
# use it with care.
#
# An example for the openssl config file can be found in
# conf-examples/openssl.cnf .
#

set -eu

test $# -ne 2 && echo "Usage: $(basename $0) OPENSSL_CONF_FILE CERT_FILE" && exit 1

TMP_FILE=/tmp/cryptobox-cert.tmp
## vcert values are in openssl.conf
#OPENSSL_CONF_FILE="../conf-examples/openssl.cnf"
OPENSSL_CONF_FILE="$1"
## filename for the created cert
#CERTFILE="cryptobox.cert"
CERTFILE="$2"
## source & destination ports
SRC_PORT="8080"
DST_PORT="443"


[ ! -f "$OPENSSL_CONF_FILE" ] && echo "`basename $0`: $OPENSSL_CONF_FILE not found" && exit 2
# this command creates the certificate
# the "\n" are required, because the certbuilding asks for 5 returns
echo -ne "\n\n\n\n\n" | openssl req -new -x509 -nodes -days 3650 -config "$OPENSSL_CONF_FILE" -out "$CERTFILE" -keyout "$CERTFILE"
chmod 600 "$CERTFILE"

# next step needs a lot of randomdata
dd if=/dev/urandom of="$TMP_FILE" bs=1024 count=1024
openssl dhparam -rand "$TMP_FILE" 512 >> "$CERTFILE"
rm "$TMP_FILE"

## print out cert values
#openssl x509 -subject -dates -fingerprint -in stunnel.pem

stunnel -p ${CERTFILE} -r localhost:${SRC_PORT} -d ${DST_PORT}

