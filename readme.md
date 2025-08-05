
## Structure

The password manager is essentialy divided into frontend and backend, of which the latter can be hosted entirely remotely if in the interest of the user. That being the case, a reverse proxy able to secure the connection using https, such as nginx, should be used. If not, hosting it locally with regular http should be fine.
