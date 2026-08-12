#!/usr/bin/env bash
#
#
server="zaiene-hpcs2024"
dst_dir="zaiene_dev/x_logger"

rsync -avz -e ssh --delete ./ "$server:~/$dst_dir/"

# 転送先で pip install . を実行
ssh "$server" "cd ~/$dst_dir && ~/.pyenv/shims/pip install ."
