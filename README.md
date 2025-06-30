# Kubeflow-KServe-MLOps-Pipeline

End-to-end MLOps pipeline on AWS EC2 using Kubeflow Pipelines v2, KServe for model serving, and S3 for model storage. Includes full infrastructure setup, modular pipeline components, and custom domain inference serving.

---

## 🚀 Project Overview

This project demonstrates how to:

- Build and run a Kubeflow Pipeline that trains and evaluates a Scikit-learn model.
- Upload the trained model to AWS S3.
- Deploy the model using KServe and expose it via Istio Gateway.
- Serve predictions via a custom DNS using `xip.io`.

All steps are performed on a self-managed Ubuntu EC2 instance with Minikube.

---

## 🧰 Requirements

- Ubuntu EC2 Instance (t3.2xlarge recommended)
- AWS IAM User with S3 access
- AWS S3 Bucket
- SSH Keypair
- Open Ports: 22, 80, 443, 8080, 8081, 31380-31390, 30000-32767

---

## ⚙️ Setup Instructions

### 1. Launch and Prepare EC2

```bash
# SSH into instance
chmod 600 <keypair>
ssh -i <keypair> ubuntu@<EC2-Public-IP>
```

### 2. Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io python3-pip python3.12-venv -y
sudo usermod -aG docker $USER && newgrp docker
```

### 3. Install Kubectl & Minikube

```bash
sudo snap install kubectl --classic
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### 4. Start Minikube

```bash
minikube start --cpus=4 --memory=10240 --driver=docker
```

---

## 🧪 Setup Python Env & Kubeflow Pipelines

```bash
python3 -m venv venv && source venv/bin/activate
pip install --upgrade pip
pip install kfp boto3 scikit-learn pandas joblib
```

### 5. Install Kubeflow Pipelines (v2)

```bash
export PIPELINE_VERSION=2.4.0
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION"
```

---

## 📦 Pipeline Structure

```
project-root/
├── pipeline.py
├── pipeline.yaml
├── pipelines/
│   ├── components/
│   │   ├── load_data.py
│   │   ├── preprocess.py
│   │   ├── train.py
│   │   └── evaluate.py
```

Each component is modular and uses `@dsl.component`.

### 6. Compile & Upload Pipeline

```bash
python pipeline.py
kfp pipeline upload pipeline.yaml --name iris-pipeline
```

---

## ☁️ AWS & S3 Setup

### 7. IAM User & Access

- Create IAM User with AmazonS3FullAccess
- Generate Access & Secret Keys
- Export keys:

```bash
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
```

### 8. Create S3 Bucket

Example: `kubeflow-bucket-iquant01`

---

## 🔁 Run the Pipeline

- Open port forwarding for UI:

```bash
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```

- Visit: `localhost:8080`
- Create run, provide secrets (S3 credentials), and start execution

---

## 🧠 Install & Configure KServe

```bash
curl -s https://raw.githubusercontent.com/kserve/kserve/release-0.14/hack/quick_install.sh | bash
```

### 9. Create Namespace, Secret & ServiceAccount

```bash
kubectl create namespace kserve-test
# create s3-credentials secret with AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY
# create ServiceAccount and attach secret
```

### 10. Configure InferenceService YAML

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-iris
  namespace: kserve-test
spec:
  predictor:
    serviceAccountName: s3-sa
    model:
      modelFormat:
        name: sklearn
      storageUri: s3://your-bucket/path/to/model.joblib
```

```bash
kubectl apply -f inference-service.yaml
```

---

## 🌐 Setup Custom Domain with xip.io

```bash
kubectl edit configmap config-domain -n knative-serving
# Add: <EXTERNAL-IP>.xip.io: ""
```

### 11. Find External IP

```bash
kubectl get svc istio-ingressgateway -n istio-system
```

### 12. Run Inference

```bash
export INGRESS_HOST=<external-ip>
export SERVICE_HOSTNAME=<generated xip.io hostname>

cat > iris-input.json <<EOF
{
  "instances": [[6.3, 3.3, 6.0, 2.5]]
}
EOF

curl -v -H "Host: $SERVICE_HOSTNAME" \
     -H "Content-Type: application/json" \
     http://$INGRESS_HOST:<PORT>/v1/models/sklearn-iris:predict \
     -d @iris-input.json
```

---

## 🧹 Clean Up

```bash
kubectl delete isvc sklearn-iris -n kserve-test
minikube stop && minikube delete --all
```

---

## 📄 License

MIT License

---

## 🙌 Acknowledgements

Built with ❤️ using Kubeflow, KServe, and Kubernetes. Special thanks to the open-source community.

---

## 📬 Contact

Maintained by [@tanny1412](https://github.com/tanny1412). Contributions welcome!

