#!/bin/sh

# Inject dummy secrets into all YAML files in the current directory and subdirectories.
# This is useful for testing purposes.

# Replace any secret url with 'example.com'
find . \( \( -type d -name .git -prune \) -o -type f \) -a \( -name '*.yaml' -o -name '*.env' \) -exec sed -i -e 's@\({{\)\?op://docker/home_address/url/\(old_\)\?url\(}}\)\?@example.com@g' {} \;

# Replace any secret IP with '10.0.0.0'
find . \( \( -type d -name .git -prune \) -o -type f \) -a \( -name '*.yaml' -o -name '*.env' \) -exec sed -i -e 's@\({{\)\?op://docker/TrueNas/config/services_ip\(}}\)\?@10.0.0.0@g' {} \;

# Replace any remaining secret with 'DUMMY_SECRET'
find . \( \( -type d -name .git -prune \) -o -type f \) -a \( -name '*.yaml' -o -name '*.env' \) -exec sed -i -e 's@\({{\)\?op://docker/.*\(}}\)\?@10.0.0.0@g' {} \;
