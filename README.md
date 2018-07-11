# Linux Server project
## Project descriptions

The goal of this project was to get our item catalog project from an earlier course project up and running on our own Linux Server.

### Relevant Information
1. IP Address and SSH port
  * IP Address: 18.217.209.223
  * SSH Port: 2200

2. URL to web application
  * http://18.217.209.223.xip.io

3. Software installed:
  * PostgreSQL
  * httplib2
  * pip
  * SQLAlchemy
  * requests
  * git
  * Flask
  * oauth2client

4. Configuration changes:
  * SSH Port changed from 22 to 2200
  * UFW set to allow incoming connections for SSH, HTTP, & NTP
  * grader given permission to sudo
  * Local timezone set to UTC
  * PostgreSQL - Configured to not allow remote connections

5. 3rd-party Resources:
  * Amazon Lightsail
  * Google Auth

