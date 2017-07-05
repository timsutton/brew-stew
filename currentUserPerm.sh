#!/bin/bash

# Run this script via Outset or in Self-Service. 
# in case you'll run manually you need to use sudo.
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 
    exit 1
fi

# Get current logged in user
loggedInUser=`/bin/ls -l /dev/console | /usr/bin/awk '{ print $3 }'`

# Add staff to _developer group
dseditgroup -o edit -a staff -t group _developer

# chgrp scope to _developer 
groupScope="_developer" 

/bin/chmod u+rwx /usr/local/bin
/bin/chmod g+rwx /usr/local/bin
/usr/sbin/chown -R $loggedInUser /usr/local/bin
/usr/bin/chgrp -R $groupScope /usr/local/bin
/bin/mkdir -p /usr/local/Cellar /usr/local/Homebrew /usr/local/Frameworks /usr/local/etc /usr/local/include /usr/local/lib /usr/local/opt /usr/local/sbin /usr/local/share /usr/local/share/zsh /usr/local/share/zsh/site-functions /usr/local/var
/bin/chmod g+rwx /usr/local/Cellar /usr/local/Homebrew /usr/local/Frameworks /usr/local/etc /usr/local/include /usr/local/lib /usr/local/opt /usr/local/sbin /usr/local/share /usr/local/share/zsh /usr/local/share/zsh/site-functions /usr/local/var
/bin/chmod 755 /usr/local/share/zsh /usr/local/share/zsh/site-functions
/usr/sbin/chown -R $loggedInUser /usr/local/Cellar /usr/local/Homebrew /usr/local/Frameworks /usr/local/etc /usr/local/include /usr/local/lib /usr/local/opt /usr/local/sbin /usr/local/share /usr/local/share/zsh /usr/local/share/zsh/site-functions /usr/local/var
/usr/bin/chgrp -R $groupScope /usr/local/Cellar /usr/local/Homebrew /usr/local/Frameworks /usr/local/etc /usr/local/include /usr/local/lib /usr/local/opt /usr/local/sbin /usr/local/share /usr/local/share/zsh /usr/local/share/zsh/site-functions /usr/local/var
/bin/mkdir -p /Users/$loggedInUser/Library/Caches/Homebrew
/bin/chmod g+rwx /Users/$loggedInUser/Library/Caches/Homebrew
/usr/sbin/chown -R $loggedInUser /Users/$loggedInUser/Library/Caches/Homebrew
/bin/mkdir -p /Library/Caches/Homebrew
/bin/chmod g+rwx /Library/Caches/Homebrew
/usr/sbin/chown $loggedInUser /Library/Caches/Homebrew
