import os
import subprocess
import uuid
import sys

#        Under deployment etter image-nøkkelen legger du inn:
#    command: [ "/bin/bash" ]
#    args: [ "-c", "streamlit run app.py --server.port 8501 --server.baseUrlPath /appnavn"]


def build_docker_tag(appname, unique_id):
    """Builds a docker image from a github repo and tags it for GCP 
    - the repo must have a file named 'Dockerfile'
    appname is the name for app"""
    

    p = subprocess.run(['docker', 'build', '-t', f'gcr.io/norwegian-language-bank/{appname}:{unique_id}', '.'])
    return p

def push_docker(appname, unique_id):
    """ Pushes a docker image already tagged for GCP """
    p = subprocess.run(['docker', 'push', f'gcr.io/norwegian-language-bank/{appname}:{unique_id}'])
    return p


def yaml_template(APP_PY_FILE, APPNAME, unique_id, PORT = "8501"):
    with open("deployment.yaml", "w", encoding = "utf-8") as yaml_file:
        yaml_file.write(
            f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {APPNAME}-deployment
  labels:
    app: {APPNAME}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {APPNAME}
  template:
    metadata:
      labels:
        app: {APPNAME}
    spec:
      containers:
      - name: {APPNAME}
        image: gcr.io/norwegian-language-bank/{APPNAME}:{unique_id}
        command: [ "/bin/bash" ]
        args: [ "-c", "streamlit run {APP_PY_FILE} --server.port {PORT} --server.baseUrlPath /{APPNAME} --browser.gatherUsageStats=False"]
        ports:
        - containerPort: {PORT}
        resources:
          limits:
            cpu: 750m
            ephemeral-storage: 256Mi
            memory: 1Gi
          requests:
            cpu: 750m
            ephemeral-storage: 256Mi
            memory: 1Gi"""
        )

def kubectl_apply(a_file):
    """ Adds a pushed image to GCP kubernets cluster"""
    p = subprocess.run(
        [
            'kubectl',
            'apply',
            '-f', 
            a_file,
        ]
    ) 
    return p



def kubectl_autoscale(appname, cpu_percent = 80, minimum = 1, maximum = 5):
    p = subprocess.run([
        'kubectl',
        'autoscale',
        'deployment',
        appname,
        '--cpu-percent= {cpu_percent}'.format(cpu_percent = cpu_percent),
        '--min= {minimum}'.format(minimum = minimum),
        '--max= {maximum}'.format(maximum = maximum)])
    return p

def kubectl_expose(appname, port = "8501"): 
    p = subprocess.run([
        'kubectl',
        'expose',
        'deployment',
        f'{appname}-deployment',
        f'--name={appname}-service',
        f'--type=ClusterIP',
        f'--port=80',
        f'--target-port={port}'
    ])
    return p

def make_docker(streamlit_app = 'app.py', target_dir = '.', port = "8501"):
    """Creates a dockerfile named 'Dockerfile' and writes in the current directory
    app is the name of the .py file to be run"""
    
    text = f"""FROM python:3.9
        EXPOSE {port}
        WORKDIR /{streamlit_app}
        COPY requirements.txt {target_dir}/requirements.txt
        RUN apt-get update && apt-get install -y graphviz graphviz-dev
        RUN pip install -r requirements.txt
        COPY . .
        CMD streamlit run {streamlit_app}
        """
    with open("Dockerfile", 'w', encoding = "utf-8") as dockerfile:
        dockerfile.write(text)

def make_ingress(APPNAME, port = 80):
    with open('ingress.yaml', 'w') as file:
        file.write(f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-{APPNAME}
  annotations:
    kubernetes.io/ingress.class: "nginx"
    kubernetes.io/ingress.allow-http: "false"
spec:
  tls:
  - secretName: nginx-ingress-secret
    hosts:
     - "beta.nb.no"
  rules:
  - host: "beta.nb.no"
    http:
      paths:
      - pathType: Prefix
        path: "/{APPNAME}"
        backend:
          service:
            name: {APPNAME}-service
            port:
              number: {port}""")
        
def update_or_create_gcp_app(streamlit_app, gcp_appname, port = "8501"):
    unique_id = str(uuid.uuid4())
    print(f'make docker {streamlit_app} with {gcp_appname}:{unique_id}')
    make_docker(streamlit_app, port = port)
    print(f'make_ingress')
    make_ingress(gcp_appname)
    print(f'build {gcp_appname}:{unique_id}')
    build_docker_tag(gcp_appname, unique_id)
    print(f'push image to gcp {gcp_appname}:{unique_id}')
    push_docker(gcp_appname, unique_id)
    yaml_template(streamlit_app, gcp_appname, unique_id, PORT = port)
    print(f'update or create {gcp_appname}:{unique_id}')
    p = kubectl_apply('deployment.yaml')
    print(p)
    print('expose')
    try:
        kubectl_expose(gcp_appname, port = port)
    except:
        print('feil i expose')
    print(f'make ingress')
    p = kubectl_apply('ingress.yaml')
    return "Done" 

if __name__ == "__main__":
    streamlitapp = sys.argv[1]
    gcp_appname = sys.argv[2]
    try:
        port = sys.argv[3]
    except:
        port = "8501"
    update_or_create_gcp_app(streamlitapp, gcp_appname, port)
