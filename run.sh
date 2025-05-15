#!/bin/bash

ENV_FILE=".env"

modify_server() {
    local new_value=$1
    if grep -q "^S_SERVER=" "$ENV_FILE"; then
        sed -i "s|^S_SERVER=.*|S_SERVER=$new_value|" "$ENV_FILE"
    else
        echo "S_SERVER=$new_value" >> "$ENV_FILE"
    fi
}

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found!"
    exit 1
fi

PROD_VALUE=$(grep "^PRODUCTION=" "$ENV_FILE" | cut -d '=' -f2 | tr -d "'\"")

if [ "$PROD_VALUE" == "1" ]; then
    modify_server "https://orion.genesistechnologies.org:443"
else
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    modify_server "http://$LOCAL_IP:8080"
fi
