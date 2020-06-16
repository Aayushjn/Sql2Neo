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

_Run the commands from the Sql2Neo root directory._

After databases have been set up and environment variables have been provided, the following commands can be used:
- Migrate source database to Neo4j: `python -m src.sql2neo.py convert --src (mysql|mongo)`. Optionally, `--db <db_name>` option 
can be used to override the source database provided in .env
- Translate SQL queries to Cypher: `python -m src.sql2neo.py translate -q <query> [-f] <file.(txt|sql)>` . If both the flags are
provided, it defaults to `-q`. Furthermore, the translated queries can be run on Neo4j as well. To do so, pass `--run` 
flag. The default action is to use `--dry-run`.
- Delete all created data (including indices and constraints): `python -m src.sql2neo.py --delete-all`.

Verbosity can be reduced by using the `--suppress-logs` flag with any of the commands.

### Testing
- SQL: Test database 'hosp' is used. This can be set up by running; `mysql -u <username> -p < hosp.sql`.
 ([hosp.sql](hosp.sql))
- NoSQL
    - Well-defined schema: [students.json](https://github.com/ozlerhakan/mongodb-json-files/blob/master/datasets/students.json) 
    is used. To import it, run:
    ```shell script
    curl https://raw.githubusercontent.com/ozlerhakan/mongodb-json-files/master/datasets/students.json
    mongoimport -d=test students.json
    ```
    - Irregular schema: [products.json](https://github.com/ozlerhakan/mongodb-json-files/blob/master/datasets/products.json)
    is used. To import it, run:
    ```shell script
    curl https://raw.githubusercontent.com/ozlerhakan/mongodb-json-files/master/datasets/products.json
    mongoimport -d=test products.json
    ```

### Features
- [x] SQL to Neo4j conversion
    - [x] Index creation
    - [x] Node creation
    - [x] Relationship creation
    - [ ] Indexing on non-primary attribute
- [ ] NoSQL to Neo4j conversion
    - [x] Node creation
    - [ ] Relationship creation
- [ ] Query Translation
    - [x] Support basic SELECT, WHERE, DISTINCT, AS, ORDER BY, and LIMIT queries
    - [ ] Support JOIN queries
    
Sql2Neo creates indices for all SQL tables on its primary key. Further, it creates a uniqueness constraint on all non-PK
attributes that are unique. Finally, it creates FK relations from referencing table to the referenced table. 