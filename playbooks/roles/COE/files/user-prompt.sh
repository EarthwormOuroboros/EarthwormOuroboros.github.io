##  /etc/profile.d/user-prompt.sh
##
##  Created by:  Lorenzo Wacondo, TEKsystems
##  Created on: 2015/05/05
##
##  Purpose:  Set a colorful prompt for superuser and non-superuser accounts which allows for a quick visual distiction.
##

PROMPT_STRING="DS, WildFly 1"

if [ $UID = "0" ]
then
    # Colorful prompt for superuser
    PS1="\[\e[31;1m\]\u\[\e[37;1m\]@\[\e[34;1m\]\h\[\e[37;1m\]:\[\e[35;1m\]\w \[\e[33;1m\]\n (${PROMPT_STRING}) \[\e[31;1m\]\$\[\e[0m\] "
else
    # Colorful prompt for regular users
    PS1="\[\e[32;1m\]\u\[\e[37;1m\]@\[\e[34;1m\]\h\[\e[37;1m\]:\[\e[36;1m\]\w \[\e[33;1m\]\n (${PROMPT_STRING}) \[\e[32;1m\]\$\[\e[0m\] "
fi

