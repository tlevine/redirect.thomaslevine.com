Backups
===================
Because of the ReSTfulness, the entire history of both management of redirects
and access of redirects is available in the logs, so backing them up makes so
much sense.

Current state of the site can be rebuilt from the logs, so backing up only the
logs them up should be sufficient. This might take a while to restore, so I
also back up the `/etc/nginx` directory.

Both the logs and the nginx directory are periodically sent somewhere else via
some protocal. For now, they're just SCPed to my desk every day.
