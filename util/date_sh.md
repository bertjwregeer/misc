# Create X dates starting from certain date

    for ((I=0; I <= 60; I++)); do date -j -v+${I}d 111100002012 +"%Y-%m-%d"; done

Handy for creating a bunch of dates to paste into Google Docs or another
spreadsheet where dragging down doesn't work...
