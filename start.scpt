#!/usr/bin/osascript
if application "iTerm" is running then
    tell application "iTerm"
        create window with default profile
    end tell
else 
    activate application "iTerm"
end if

tell application "iTerm"
    tell current session of current tab of current window
        write text "cd ~/meme_generator"
        write text "git pull"
        write text "python3 main.py -t"
    end tell
end tell
