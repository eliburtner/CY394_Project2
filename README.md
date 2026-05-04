# CY394 Project 2

## Instructions

File Directory Structure: refer to Directory-Structure-Preview.jpg

1. Clone this repository:

```bash
git clone https://github.com/eliburtner/CY394_Project2.git
```

2. Enter into the CY394_Project2 Directory:

3. Build and push the images to be used in Rancher

```bash
docker build -f Backend/flask.Dockerfile -t <your-dockerhub-username>/seat-scout-backend:v1 ./Backend

docker build -f Frontend/frontend.Dockerfile -t <your-dockerhub-username>/seat-scout-frontend:v1 ./Frontend

docker push <your-dockerhub-username>/seat-scout-backend:v1
docker push <your-dockerhub-username>/seat-scout-frontend:v1
```

Once you push your DockerHub specific image, go into each <file>-deployment.yaml and change the image desinator to the image you built and pushed.

4. Deploy in Rancher Kubernetes

```bash
kubectl create namespace <your-namespace>

kubectl apply -f proj2_k8s/database/ -n <your-namespace>
kubectl apply -f proj2_k8s/backend/ -n <your-namespace>
kubectl apply -f proj2_k8s/frontend/ -n <your-namespace>
```

5. Kube-score Security and Validation

```bash
cd proj2_k8s

docker pull zegl/kube-score

cd backend
(Get-Content backend-deployment.yaml) + "---" + (Get-Content backend-network-policy.yaml) + "---" + (Get-Content backend-service.yaml) | docker run -i zegl/kube-score score -

cd ..
cd frontend
(Get-Content frontend-deployment.yaml) + "---" + (Get-Content frontend-network-policy.yaml) + "---" + (Get-Content frontend-service.yaml) + "---" + (Get-Content frontend-ingress.yaml) | docker run -i zegl/kube-score score -

cd ..
cd database
(Get-Content mysql-headlessService.yaml) + "---" + (Get-Content mysql-network-policy.yaml) + "---" + (Get-Content mysql-statefulset.yaml) | docker run -i zegl/kube-score score -
```

6. Debug with these Commands

```bash
kubectl get pods -n <your-namespace>
kubectl describe pod <pod-name> -n <your-namespace>
kubectl logs <pod-name> -n <your-namespace>
kubectl get svc -n <your-namespace>
```


## Legacy Instructions for Reference

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
docker run --env=MYSQL_ROOT_PASSWORD=123 --env=MYSQL_DATABASE=phase2-mysql-database --env MYSQL_USER=burt --env MYSQL_PASSWORD=123 --network phase2-network --volume phase2-mysql-vol:/var/lib/mysql --name phase2-mysql -v "$PWD/Database/init.sql:/docker-entrypoint-initdb.d/init.sql" -d mysql:latest
docker commit phase2-mysql phase2-mysql
docker build -f /Backend/flask.Dockerfile -t phase2-flask .
docker commit phase2-flask phase2-flask
docker build -f /Frontend/frontend.Dockerfile -t phase2-front .
docker commit phase2-front phase2-front
docker compose up -d
```
