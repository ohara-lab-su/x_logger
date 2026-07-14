#!/usr/bin/env bash
#
#
server="zaiene-hpcs2023"
dst_dir="zaiene_dev/x_logger"

rsync -avz -e ssh --delete ./ "$server:~/$dst_dir/"
