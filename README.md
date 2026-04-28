# CY394 Phase 2

## Instructions

1. Ensure you are in a WSL Environment

2. Clone this directory:

```bash
git clone https://github.com/eliburtner/CY394_Project2.git
```

4. Enter into the CY394_Project2 Directory:

```bash
cd CY394_Project2
```

5. Run the following commands in your terminal:



```bash
docker run --env=MYSQL_ROOT_PASSWORD=123 --env=MYSQL_DATABASE=phase2-mysql-database --env MYSQL_USER=burt --env MYSQL_PASSWORD=123 --network phase2-network --volume phase2-mysql-vol:/var/lib/mysql --name phase2-mysql -v "$PWD/init.sql:/docker-entrypoint-initdb.d/init.sql" -d mysql:latest
docker commit phase2-mysql phase2-mysql
docker build -f flask.Dockerfile -t phase2-flask .
docker commit phase2-flask phase2-flask
docker build -f frontend.Dockerfile -t phase2-front .
docker commit phase2-front phase2-front
docker compose up -d
```
