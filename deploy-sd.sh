#!/bin/sh
B="$HOME/Library/Application Support/Plex Media Server/Plug-ins/RuSDtv.bundle"
I="$B/Contents"
mkdir -p "$B/"
cp -r "Contents" "$B/"
mv "$I/Resources/art-sd.png" "$I/Resources/art-tv.png"
mv "$I/Resources/icon-sd.png" "$I/Resources/icon-tv.png"

sed -i .bak 's/ruhd/rusd/g' "$I/Code/__init__.py"
sed -i .bak 's/ruhd/rusd/g' "$I/Info.plist"
sed -i .bak 's/RuHD/RuSD/g' "$I/Strings/en.json"
echo "Done. God bless git and Linus."
