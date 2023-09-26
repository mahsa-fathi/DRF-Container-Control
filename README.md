# DRF Container Control

[![Python 3.9](https://img.shields.io/badge/Python-3.9-green.svg)](https://shields.io/)
[![Django](https://img.shields.io/badge/Django_Rest_Framework-3.14-355E3B)](https://shields.io/)
![Build Status](https://github.com/mahsa-fathi/devops-capstone-project/actions/workflows/ci-build.yaml/badge.svg)

This is a Django Rest Framework project. It has 5 endpoints to build applications and run containers for them.

## How it works

We started the project by creating the docker_control directory for django, and forwarded every /apps/ endpoint to 
our manager app in django. A sqlite database is used for the database.

Manager app has five endpoints. The endpoints are listed below:

- apps/: This endpoint lists all the applications using GET method and creates a new application using POST method
- apps/\<pk\>/: This endpoint gets, updates, and deletes the application in database using GET, PUT, and DELETE methods
- apps/\<pk\>/run/: This endpoint runs a container for the application using GET method
- apps/\<pk\>/history/: This endpoint lists the history of runs for a specific application using GET method

## Data Model

We have two tables in the project; Applications and Run Logs. Applications table keeps each app information,
and Run Logs keeps the running history of every application.

#### Applications

| Name        | Type         | Optional |
|-------------|--------------|----------|
| id          | INTEGER      | False    |
| name        | varchar(50)  | False    |
| image       | varchar(100) | False    |
| envs        | JSON         | False    |
| command     | TEXT         | False    |
| created_at  | datetime     | False    |

#### Run Logs

| Name           | Type         | Optional |
|----------------|--------------|----------|
| id             | INTEGER      | False    |
| envs           | JSON         | False    |
| command        | TEXT         | False    |
| status         | varchar(3)   | False    |
| executed_at    | datetime     | False    |
| application_id | bigint       | False    |
| container_name | varchar(100) | True     |
| logs           | TEXT         | True     |

## Examples

A request for building an application of hello world can be done as followed.

```shell
curl --location --request POST 'http://localhost:8080/apps/' \
--data '{
    "name": "hello-world",
    "image": "alpine",
    "envs": {},
    "command": "echo Hello World"
}'
```

A 201 status code will be returned with the following body.

```json
{
    "id": 1,
    "name": "hello-world",
    "image": "alpine",
    "envs": {},
    "command": "echo Hello World",
    "created_at": "2023-09-24T17:27:46.000665Z"
}
```

if we are willing to get a list of all apps using apps/ endpoint and the output contains a count and results that is a list of all apps.
We can also use apps/1/ endpoint to get, update, and delete the application. delete method will also stop and remove every container of the application. 

Now if we want to run the application we can do as followed.

```shell
curl --location --request GET 'http://localhost:8000/apps/1/run/'
```

This endpoint pulls the image if not available and then adds a container for the application. 
Since the start a log will be in the Run Logs table with the status of Running. After the run of the container is completed, 
status of the log will be updated to Finished, and if the running fails, the log will be updated to finished.
The output of this request then will be the following.

```json
{
    "details": "Successful",
    "containerName": "hello-world_1695576681",
    "logs": "Hello World\n",
    "numContainers": 1
}
```

## Author

[Mahsa Fathi](https://www.linkedin.com/in/mahsa-fathi-68216112b/)
