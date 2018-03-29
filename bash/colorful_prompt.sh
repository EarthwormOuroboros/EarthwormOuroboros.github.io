# colorful_prompt.sh

# Set color names
DEFAULT="\[\e[0m\]"
RED="\[\e[31;1m\]"
GREEN="\[\e[32;1m\]"
YELLOW="\[\e[33;1m\]"
BLUE="\[\e[34;1m\]"
MAGENTA="\[\e[35;1m\]"
CYAN="\[\e[36;1m\]"
WHITE="\[\e[37;1m\]"

# Get exit status of previous command
if [ "${?}" == "0" ]
then
  EC="${GREEN}:)"
elif [ "${?}" == "1" ]
then
  EC="${RED}:("
else
  EC="${YELLOW}:/"
fi

# Change the string to something resonable.
PROMPT_STRING=""

if [ -z "${PROMPT_STRING}" ] && [ -f /etc/os-release ]
then
  . /etc/os-release
  PROMPT_STRING="${PRETTY_NAME}"
fi

# DO NOT change anything beyond this point!!!  ...Unless you know what you're doing.
if [ ${UID} == "0" ]
then
  # Colorful BASH Prompt for superuser
  PS1="${RED}\u${YELLOW}@${BLUE}\H${YELLOW}:${MAGENTA}\w \n${WHITE}${PROMPT_STRING} ${EC} ${RED}\$ ${DEFAULT}"
else
  # Colorful BASH Prompt for users
  PS1="${GREEN}\u${YELLOW}@${BLUE}\H${YELLOW}:${CYAN}\w \n${WHITE}${PROMPT_STRING} ${EC} ${GREEN}\$ ${DEFAULT}"
fi
