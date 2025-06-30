# kubeflow-kserve-mlops-pipeline
End-to-end MLOps project using Kubeflow Pipelines and KServe on AWS EC2. Includes training a Scikit-learn model, uploading to S3, and deploying with KServe using custom DNS and inference via Istio gateway.

✅ Prerequisites
Make sure the following tools are installed and configured:
Docker (Desktop or Engine)
Kubectl
Minikube
Python (3.12+) and venv
AWS IAM User with S3 Access
AWS S3 Bucket
Helm
kfp SDK
🖥️ Local Environment Setup
# Update and install system packages
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io python3-pip python3.12-venv -y

# Docker setup
sudo usermod -aG docker $USER && newgrp docker

# Kubectl
sudo snap install kubectl --classic

# Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install kfp
🧱 Kubernetes & Kubeflow Setup
# Minikube installation
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start --cpus=4 --memory=10240 --driver=docker

# Kubeflow Pipelines
export PIPELINE_VERSION=2.4.0
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION"
⚙️ Build and Upload Pipeline
# Activate venv
source .venv/bin/activate

# Compile the pipeline
python pipeline.py

# Create and upload pipeline
kfp pipeline create -p IrisClassifier pipeline.yaml
☁️ AWS S3 Configuration
Create an IAM user with AmazonS3FullAccess
Generate and save Access Key & Secret Key
Configure AWS CLI:
aws configure
Create or select an S3 bucket (e.g., kubeflow-bucket-mlops-demo)
🌐 Access Kubeflow UI
Local:
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
EC2 (SSH Tunnel):
ssh -i <keypair> -L 8080:localhost:8080 ubuntu@<EC2-Public-IP>
Then go to: http://localhost:8080
📦 Model Serving with KServe
# Install dependencies
sudo snap install helm --classic
curl -s https://raw.githubusercontent.com/kserve/kserve/release-0.14/hack/quick_install.sh | bash
minikube addons enable ingress
minikube tunnel
Deploy InferenceService:
kubectl create namespace kserve-test

kubectl apply -n kserve-test -f - <<EOF
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "s3://<your-bucket-name>/iris-model/"
EOF
🔍 Model Inference
Create a sample input file:
cat > iris-input.json <<EOF
{
  "instances": [
    [6.8, 2.8, 4.8, 1.4],
    [6.0, 3.4, 4.5, 1.6]
  ]
}
EOF
Send request:
SERVICE_HOSTNAME=$(kubectl get inferenceservice sklearn-iris -n kserve-test -o jsonpath='{.status.url}' | cut -d "/" -f 3)
INGRESS_HOST=$(minikube ip)
INGRESS_PORT=80  # or use port lookup

curl -v -H "Host: $SERVICE_HOSTNAME" -H "Content-Type: application/json" \
"http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/sklearn-iris:predict" \
-d @iris-input.json
🧹 Cleanup
kubectl delete isvc sklearn-iris -n kserve-test
minikube stop
minikube delete --all
