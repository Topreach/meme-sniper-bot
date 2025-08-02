#!/bin/bash
echo "Verifying deployment on CentOS 7"

# Check system version
echo -n "OS Version: "
cat /etc/centos-release

# Check services
echo -e "\nService Status:"
sudo systemctl status sniper-bot
sudo systemctl status sniper-dashboard

# Check ports
echo -e "\nOpen Ports:"
sudo firewall-cmd --list-ports

# Check disk space
echo -e "\nDisk Space:"
df -h

# Check logs
echo -e "\nRecent Bot Logs:"
journalctl -u sniper-bot -n 20 --no-pager

echo -e "\nDeployment verification complete"
