#!/bin/sh
# Convert SVG Files to png using rsvg
# rsvg is part of librsvg from http://librsvg.sourceforge.net

echo "Building Icons..."
for f in icons/*.svg; do
    BASENAME="$(echo $f| cut -d/ -f2| cut -d. -f1)"
    echo "icon $BASENAME"
    for size in "24" "32" "64" "128"; do
        rsvg -w$size -h$size $f "$BASENAME-$size.png"
    done;
done;
echo "Building Smilies..."
for f in smilies/*.svg; do
    BASENAME="$(echo $f| cut -d/ -f2| cut -d. -f1)"
    echo "smiley $BASENAME"
    for size in "20" "32" "64"; do
        rsvg -w$size -h$size $f "smiley-$BASENAME-$size.png"
    done;
done;
