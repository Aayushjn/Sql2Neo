# Sql2Neo

A command-line tool to convert data between SQL, NoSQL and Neo4j databases

### Installation
- Python 3.8
```shell script
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8
```
Setup a virtual environment and install packages from [requirements.txt](requirements.txt) using 
`python -m pip install -r requirements.txt`.

- MySQL
The simplest way to install MySQL server is to follow the 
[DigitalOcean tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-18-04).

- MongoDB
Install MongoDB by following the official instructions 
[here](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).

- Neo4j
Neo4j requires Java 11 to be installed. Instructions on installing both can be found 
[here](https://neo4j.com/docs/operations-manual/current/installation/linux/debian/).

### Usage
To be updated

### Testing
For testing purposes, the [employees database](https://dev.mysql.com/doc/employee/en/) provided by MySQL is used. It is 
available under the [Creative Commons license](https://creativecommons.org/licenses/by-sa/3.0/). It has 4 million 
records across 6 tables (~160MB). 

### Features
- [ ] SQL to Neo4j conversion
- [ ] NoSQL to Neo4j conversion 
- [ ] Neo4j to SQL conversion 
- [ ] Neo4j to NoSQL conversion 