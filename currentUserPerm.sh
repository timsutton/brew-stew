#!/bin/bash

# Run this script via Outset or in Self-Service.
# in case you'll run manually you need to use sudo.
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    exit 1
fi

loggedInUser=`/bin/ls -l /dev/console | /usr/bin/awk '{ print $3 }'`

# Add staff to developer group
dseditgroup -o edit -a staff -t group _developer

# use _developer group
groupScope="_developer"

/bin/chmod u+rwx /usr/local/bin
/bin/chmod g+rwx /usr/local/bin
# process  symlinks only, ensure to exclude symlinks for jamf, autopkg, outset, santactl
find /usr/local/bin/ -type l -and ! -name "jamf" -and ! -name "autopkg" -and ! -name "outset" ! -name "santactl"  -exec chown -R $loggedI$
find /usr/local/bin/ -type l -and ! -name "jamf" -and ! -name "autopkg" -and ! -name "outset" ! -name "santactl"  -exec chgrp -R $groupSc$
/bin/mkdir -p /usr/local/Cellar /usr/local/Homebrew /usr/local/Frameworks /usr/local/etc /usr/local/include /usr/local/lib /usr/local/opt$
/bin/chmod g+rwx /usr/local/Cellar /usr/local/Homebrew /usr/local/Frameworks /usr/local/etc /usr/local/include /usr/local/lib /usr/local/$
/bin/chmod 755 /usr/local/share/zsh /usr/local/share/zsh/site-functions
/usr/sbin/chown -R $loggedInUser /usr/local/Cellar /usr/local/Homebrew /usr/local/Frameworks /usr/local/etc /usr/local/include /usr/local$
/usr/bin/chgrp -R $groupScope /usr/local/Cellar /usr/local/Homebrew /usr/local/Frameworks /usr/local/etc /usr/local/include /usr/local/li$
/bin/mkdir -p /Users/$loggedInUser/Library/Caches/Homebrew
/bin/chmod g+rwx /Users/$loggedInUser/Library/Caches/Homebrew
/usr/sbin/chown -R $loggedInUser /Users/$loggedInUser/Library/Caches/Homebrew
/bin/mkdir -p /Library/Caches/Homebrew
/bin/chmod g+rwx /Library/Caches/Homebrew
/usr/sbin/chown $loggedInUser /Library/Caches/Homebrew
