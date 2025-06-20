
---

### ✅ **Kibana Deployment**

```yaml
apiVersion: apps/v1
```

* 📌 *Specifies the Kubernetes API version used to create a **Deployment**.*

```yaml
kind: Deployment
```

* 📦 *This tells Kubernetes to create a **Deployment** (which manages a pod and keeps it running).*

```yaml
metadata:
  name: kibana
  namespace: logging
```

* 🏷 *Gives the deployment a name (`kibana`) and places it inside the `logging` namespace.*

```yaml
spec:
  replicas: 1
```

* 🔁 *Runs only **1 replica** (pod) of the Kibana app.*

```yaml
  selector:
    matchLabels:
      app: kibana
```

* 🎯 *Tells Kubernetes to manage pods that have the label `app: kibana`.*

```yaml
  template:
    metadata:
      labels:
        app: kibana
```

* 🏷 *Labels the pod as `app: kibana` (so the deployment can manage it).*

```yaml
    spec:
      containers:
        - name: kibana
```

* 📦 *Defines a container named `kibana` inside the pod.*

```yaml
          image: docker.elastic.co/kibana/kibana:7.17.0
```

* 🐳 *Uses the official Kibana Docker image (version 7.17.0).*

```yaml
          env:
            - name: ELASTICSEARCH_HOSTS
              value: http://elasticsearch:9200
```

* 🌍 *Sets an environment variable to tell Kibana where Elasticsearch is running (on the `elasticsearch` service at port 9200).*

```yaml
          ports:
            - containerPort: 5601
```

* 🔓 *Exposes port **5601** inside the container (this is where Kibana runs).*

---

### 🌐 **Kibana Service**

```yaml
---
apiVersion: v1
kind: Service
```

* 🌐 *Creates a Kubernetes **Service** to expose Kibana.*

```yaml
metadata:
  name: kibana
  namespace: logging
```

* 🏷 *Gives the service a name and places it in the `logging` namespace.*

```yaml
spec:
  type: NodePort
```

* 🚪 *Uses **NodePort** to expose Kibana on a specific port of your cluster node (so you can access it via your machine’s IP).*

```yaml
  selector:
    app: kibana
```

* 🎯 *Targets pods that have the label `app: kibana` (i.e., our Kibana pod).*

```yaml
  ports:
    - port: 5601
      nodePort: 30601
```

* 🔌 *Maps internal port 5601 of Kibana to **NodePort 30601**, which you can access via `http://<NodeIP>:30601`.*

---

### ✅ In Simple Terms:

* This file **deploys Kibana** inside your Kubernetes cluster.
* It connects Kibana to **Elasticsearch** using an environment variable.
* It exposes Kibana on **port 30601** so you can open it in your browser.
