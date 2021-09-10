#Casting Agency Backend

##Introduction
##Overview
##Main Files: Project Structure

##Roles
###Permissions
##API Endpoints

Motivation for project
Project dependencies, local development and hosting instructions,
Detailed instructions for scripts to install any project dependencies, and to run the development server.
Documentation of API behavior and RBAC controls
Setup environment variables in setup.sh for heroku


##Instructions
Dependencies:
  python 3.9.7

Authorizations:
https://pibcrib.us.auth0.com/authorize?audience=CastingAgency&response_type=token&client_id=jerWZMmUrHOdpTSuloIr7IIX9QyUq7n7&redirect_uri=http://10.100.10.131:8080/

  Assistant:
    get:actors
    get:movies
  Casting Director:
    assistant +
    post:actors
    delete:actors
    patch:actors
    patch:movies
  Executive Producer:
    casting director +
    post:movies
    delete:movies


callback url is local domain, eventually change to heroku domain
