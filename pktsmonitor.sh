#!/bin/bash
svip="Wakeel-Anty"
servername="LCD-Masjid"
owner_id="2"
services=("apache2" "nginx")
containers=("phpadmin" "mysq_server2")
lst_down_service=""
lst_down_container=""
maxTries=3
endpoint="http://127.0.0.1:5000/service-down"

# Check the status of each service and container
for service in "${services[@]}"; do
  tryCount=0
  while true; do
    # Check if the service is running
    if systemctl is-active "$service" >/dev/null; then
      # Service is running, clear the error message
      status="running"
      break
    fi

    tryCount=$((tryCount + 1))

    if [ $tryCount -ge $maxTries ]; then
      # Service is down/not running, set the status variable and add to lst_down_service
      status="not running"
      lst_down_service+="${service},"
      break
    fi
    sleep 5
  done
done 
for container in "${containers[@]}"; do
  lst_down_container=""
  tryCount=0

  while true; do
    # Check if the container is running
    if docker ps --format '{{.Names}}:{{.State}}' | grep "$container" | grep -q "running"; then
      # Container is running, clear the error message
      container_down="running"
      break
    fi

    tryCount=$((tryCount + 1))

    if [ $tryCount -ge $maxTries ]; then
      # Container is down/not running, set the container_down variable and add to lst_down_container
      container_down="not running"
      lst_down_container+="${container},"
      break
    fi
    sleep 5
  done
done

# Send a HTTP POST request to the Flask endpoint
if [ ! -z "$lst_down_service" ] || [ ! -z "$lst_down_container" ]; then
fi
