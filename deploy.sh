#!/bin/sh
B="$HOME/Library/Application Support/Plex Media Server/Plug-ins/RuHDtv.bundle/Contents"
mkdir -p "$B"
cp -r "Contents" "$B"
echo "Done. God bless git and Linus."
