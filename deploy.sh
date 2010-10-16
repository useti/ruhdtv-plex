#!/bin/sh
B="$HOME/Library/Application Support/Plex Media Server/Plug-ins/RuHDtv.bundle"
test -d "$B" || B="$HOME/Library/Application Support/Plex Media Server/Plug-ins/RuHD.tv.bundle"
I="$B/Contents"
mkdir -p "$B/"
cp -r "Contents" "$B/"
mv "$I/Resources/art-hd.png" "$I/Resources/art-tv.png"
mv "$I/Resources/icon-hd.png" "$I/Resources/icon-tv.png"


echo "Done. God bless git and Linus."
