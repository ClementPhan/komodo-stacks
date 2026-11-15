#!/usr/bin/env bash

task() {
  /usr/local/share/acme.sh/acme.sh --cron --home /usr/local/share/acme.sh
}

start_s=$(date +%s)
if task; then
  success="true"
else
  success="false"
fi
end_s=$(date +%s)
elapsed_s=$((end_s - start_s))

curl -X POST -H "Authorization: Bearer ${GATUS_TOKEN}" "https://gatus.${TLD}/api/v1/endpoints/Tasks_Gul-Certificate-Renewal/external?success=${success}&duration=${elapsed_s}s"

if [ "${success}" == "true" ]; then
  echo "Task succeeded in ${elapsed_s}s"
  exit 0
else
  echo "Task failed"
  exit 1
fi