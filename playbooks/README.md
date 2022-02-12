# Playbook Structure and Summary

```
group_vars/          # here we assign variables to particular groups
    README.md
    COE-packages.yml
    keycloak.yml
    wildfly.yml
host_vars/           # here we assign variables to particular systems
    README.md

library/

module_utils/

filter_plugins/

roles/
    COE/
        files/
        tasks/
        templates/
    general/
        files/
        tasks/
        templates/
    keycloak/
        files/
        tasks/
        templates/
    wildfly/
        files/
        tasks/
        templates/

hosts.prod           # inventory file for production servers
hosts.test           # inventory file for test servers
hosts.stage          # inventory file for staging servers

```
