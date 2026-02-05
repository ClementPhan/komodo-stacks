#!/bin/bash

# Validate all compose.yaml files in the current directory and subdirectories.
shopt -s globstar

errors=""
for file in stacks/**/compose.yaml; do
    echo -n "Validating $file"
    OUTPUT="$(docker compose -f "$file" config 2>&1)"
    if [ $? -eq 0 ]; then
        echo " - OK"
    else
        echo " - FAILED"
        errors="${errors}\nValidation failed for $file\n$(echo "$OUTPUT" | sed 's/^/>> /g')\n"
    fi
done

if [ -n "$errors" ]; then
    echo ""
    echo "Validation errors found:"
    echo -e "$errors"
    exit 1
else
    echo "All compose files validated successfully."
fi
