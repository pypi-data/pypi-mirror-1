#!/usr/bin/sh
#You can run this script as: sh download.sh 
#You can also put in in a cron job to download it every day. It will only get new updates.
#This script will download continue getting the files or download changed files.
wget -cN -i ./download_list.txt
