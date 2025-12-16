#!/bin/bash
# System Health Monitor - Bash Version

logfile="system_health_log.txt"
timestamp=$(date +"%d-%m-%Y %H:%M:%S")

echo "===================== System Health Report ($timestamp) =====================" | tee -a "$logfile"

echo "CPU Usage:" | tee -a "$logfile"
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
echo "$CPU%" | tee -a "$logfile"

echo -e "\nMemory Usage:" | tee -a "$logfile"
free -h | tee -a "$logfile"

echo -e "\nDisk Usage:" | tee -a "$logfile"
df -h | tee -a "$logfile"

echo -e "\nTop 5 CPU-Consuming Processes:" | tee -a "$logfile"
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -n 6 | tee -a "$logfile"

echo -e "\nSystem Uptime:" | tee -a "$logfile"
uptime -p | tee -a "$logfile"

echo "==============================================================================" | tee -a "$logfile"
echo

# Alerts
if command -v bc >/dev/null 2>&1; then
    if (( $(echo "$CPU > 80" | bc -l) )); then
        echo "⚠️  ALERT: CPU usage is above 80%!" | tee -a "$logfile"
    fi
fi

