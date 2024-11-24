#!/bin/bash

# CPU usage
endpoint="http://127.0.0.1:5000/serverperformance"
svip=""
servername="Sharjeel-badmash"
cpu_cores=$(grep -c processor /proc/cpuinfo)
cpu_total=100
list_cores=""
#echo "CPU Usage: Total: $cpu_total%"

for ((i=0; i<$cpu_cores; i++)); do
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk -v var=$i '{print $var+2}' | sed -n '1p')
    string_var=$(printf "%.2f" $cpu_usage)
    list_cores+="${string_var},"
    echo "Core $i Usage: $cpu_usage%"
done

# RAM usage
mem_total=$(free -m | awk '/Mem/{print $2}')
mem_used=$(free -m | awk '/Mem/{print $3}')
mem_used_percent=$(free | awk '/Mem/{printf("%.2f%"), $3/$2*100}')
echo "RAM Usage: Used: $mem_used MB ($mem_used_percent), Total: $mem_total MB"

# Disk usage
disk_used=$(df -h / | awk '/\//{print $3}')
disk_total=$(df -h / | awk '/\//{print $2}')
disk_used_percent=$(df -h / | awk '/\//{print $5}')
echo "Disk Usage: Used: $disk_used ($disk_used_percent), Total: $disk_total"


# Print number of users
echo "Number of Users:"
numbers=$(getent passwd | wc -l)
numb_user=$(printf "%d" $numbers)
# Print list of all users

getent passwd | cut -d: -f1 > allusers.txt
echo "the All new users are: $users"

# Print list of sudo users
echo "Sudo Users:"
getent group sudo | cut -d: -f4 | tr ',' '\n'

# Number of running processes
process_count=$(ps -e | wc -l)
echo "Number of Running Processes: $((process_count-1))"
echo $list_cores
echo "Success" 
