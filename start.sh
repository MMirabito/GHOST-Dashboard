#!/bin/sh
# Shell script to start container service and stremilt application from Docker
set -e

# Get env vars in the Dockerfile to show up in the SSH session
eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1=\2/p" | sed 's/"/\\\"/g' | sed '/=/s//="/' | sed 's/$/"/' >> /etc/profile)

# Display Linux environment
echo "+----------------------------------+"
echo "| System Information...            |"
echo "+----------------------------------+"
echo "| Hostname: $(hostname)"
echo "| Kernel version: $(uname -r)"
echo "| Operating system: $(lsb_release -d | awk '{print $2, $3}')"
echo "| CPU information:"
lscpu | grep "Model name:" | awk '{print "|   " $0}'
echo "| Memory information:"
free -h | grep "Mem:" | awk '{print "|   " $0}'

echo "+----------------------------------+"
echo "| Environment Variables...         |"
echo "+----------------------------------+"
env -0 | sort -z | tr '\0' '\n' | sed 's/^/| /'

# Start SSH Service
echo "+----------------------------------+"
echo "| Starting SSH...                  |"
echo "+----------------------------------+"
service ssh start

# Start Streamlit aplication 
echo "\r\r\r"
echo "+----------------------------------+"
echo "| Starting Streamlit               |"
echo "+----------------------------------+"

streamlit run ./src/app.py