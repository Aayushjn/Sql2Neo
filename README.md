# Sql2Neo

A command-line tool to convert data between SQL, NoSQL and Neo4j databases

_Due to lack of semantics, SQL records converted to Neo4j use FK (Foreign Key) as a general relationship._

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

- MySQL: The simplest way to install MySQL server is to follow the 
[DigitalOcean tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-18-04).

- MongoDB: Install MongoDB by following the official instructions 
[here](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).

- Neo4j: It requires Java 11 to be installed. Instructions on installing both can be found 
[here](https://neo4j.com/docs/operations-manual/current/installation/linux/debian/).

### Usage
A .env file must exist in the project root with the following keys
- MYSQL_DB_USER
- MYSQL_DB_PASS
- MYSQL_DB_NAME
- MONGO_HOST (default: _localhost_)
- MONGO_PORT (default: _27017_)
- MONGO_USER (default: _None_)
- MONGO_PASS (default: _None_)
- MONGO_DB_NAME
- NEO4J_HOST (default: _localhost_)
- NEO4J_PORT (default: _7474_)
- NEO4J_USER (default: _neo4j_)
- NEO4J_PASS (default: _neo4j_)
- NEO4J_SCHEME (default: _http_)

Run `python sql2neo.py convert --src <src_db> --dest <dest_db>`.

### Testing
For testing purposes, the [employees database](https://dev.mysql.com/doc/employee/en/) provided by MySQL is used. It is 
available under the [Creative Commons license](https://creativecommons.org/licenses/by-sa/3.0/). It has 4 million 
records across 6 tables (~160 MB). 

### Features
- [x] SQL to Neo4j conversion
    - [x] Index creation
    - [x] Node creation
    - [x] Relationship creation
    - [ ] Indexing on non-primary attribute
- [ ] NoSQL to Neo4j conversion
    - [x] Node creation
    - [ ] Relationship creation
    
Sql2Neo creates indices for all SQL tables on its primary key. Further, it creates a uniqueness constraint on all non-PK
attributes that are unique. Finally, it creates FK relations from referencing table to the referenced table. 