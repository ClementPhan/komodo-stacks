#!/bin/sh

# This script injects 1password secrets into all files containing "op://" in the current directory and subdirectories.
# Argument: The token to authenticate with 1password

OP_SERVICE_ACCOUNT_TOKEN=$1

if [ -z "$OP_SERVICE_ACCOUNT_TOKEN" ]; then
    echo "Usage: $0 <op_service_account_token>"
    exit 1
fi

# Start injection
find . -type f -exec grep -l "op://" {} \; | while read file; do
    if [ "$(basename "$file")" = "inject.sh" ]; then
        continue
    fi
    echo "Injecting into $file"
    cat "$file" | docker run -i -e OP_SERVICE_ACCOUNT_TOKEN=$OP_SERVICE_ACCOUNT_TOKEN 1password/op op inject > temp
    mv temp "$file"
done
