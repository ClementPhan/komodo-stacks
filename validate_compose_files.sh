#!/bin/sh

# Validate all compose.yaml files in the current directory and subdirectories.
find . \( \( -type d -name .git -prune \) -o -type f \) -a -name 'compose.yaml' | while read file; do
    echo "Validating $file"
    OUTPUT="$(docker compose -f "$file" config 2>&1)"
    if [ $? -ne 0 ]; then
        echo "Validation failed for $file"
        echo "$OUTPUT" | sed 's/^/>> /g'
        exit 1
    fi
done
