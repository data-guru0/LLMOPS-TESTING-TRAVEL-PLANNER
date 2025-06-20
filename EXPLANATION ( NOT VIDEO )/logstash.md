Absolutely! Here's a **simple line-by-line explanation** for your **Logstash setup in Kubernetes**, which includes:

* `ConfigMap` for Logstash configuration
* `Deployment` to run the Logstash container
* `Service` to expose Logstash inside the cluster


---

### 📄 **Logstash YAML Explained**

---

### 🛠️ ConfigMap (Stores Logstash config file)

```yaml
apiVersion: v1
kind: ConfigMap
```

* ⚙️ *Creates a ConfigMap to store non-sensitive config data.*

```yaml
metadata:
  name: logstash-config
  namespace: logging
```

* 📛 *Names the ConfigMap as `logstash-config` and places it in the `logging` namespace.*

```yaml
data:
  logstash.conf: |
    input {
      beats {
        port => 5044
      }
    }

    filter {
      
    }

    output {
      elasticsearch {
        hosts => ["http://elasticsearch.logging.svc.cluster.local:9200"]
        index => "filebeat-%{+YYYY.MM.dd}"
      }
    }
```

* 📁 *This is the actual Logstash config file (`logstash.conf`) stored as plain text.*

  * `input`: Accepts logs from **Filebeat** on port **5044**
  * `filter`: Empty for now (can be used to modify/clean logs)
  * `output`: Sends logs to **Elasticsearch**, creating a daily index like `filebeat-2025.06.20`

---

### 🚀 Deployment (Runs Logstash Pod)

```yaml
apiVersion: apps/v1
kind: Deployment
```

* 🚀 *This tells Kubernetes to manage the Logstash app using a Deployment.*

```yaml
metadata:
  name: logstash
  namespace: logging
```

* 📛 *Names the Deployment and places it in the `logging` namespace.*

```yaml
spec:
  replicas: 1
```

* 🔁 *Runs only 1 pod of Logstash.*

```yaml
  selector:
    matchLabels:
      app: logstash
```

* 🔍 *Matches pods with the label `app: logstash`.*

```yaml
  template:
    metadata:
      labels:
        app: logstash
```

* 🏷️ *Adds label to the pod so it can be discovered by the Service.*

```yaml
    spec:
      containers:
      - name: logstash
        image: docker.elastic.co/logstash/logstash:7.17.0
```

* 🐳 *Uses the official Logstash Docker image (version 7.17.0).*

```yaml
        ports:
        - containerPort: 5044
        - containerPort: 9600
```

* 🌐 *Exposes port `5044` (for Filebeat input) and `9600` (Logstash monitoring API).*

```yaml
        volumeMounts:
        - name: config-volume
          mountPath: /usr/share/logstash/pipeline/logstash.conf
          subPath: logstash.conf
```

* 📦 *Mounts the `logstash.conf` from ConfigMap into the container's path, so Logstash can read it.*

```yaml
      volumes:
      - name: config-volume
        configMap:
          name: logstash-config
          items:
          - key: logstash.conf
            path: logstash.conf
```

* 🗂 *Defines a volume linked to the ConfigMap and specifies which file (`logstash.conf`) to mount.*

---

### 🌐 Service (Internal Access for Filebeat)

```yaml
apiVersion: v1
kind: Service
```

* 🌐 *Defines a Kubernetes Service to expose Logstash inside the cluster.*

```yaml
metadata:
  name: logstash
  namespace: logging
```

* 🏷 *Service named `logstash` inside the `logging` namespace.*

```yaml
spec:
  selector:
    app: logstash
```

* 🎯 *Targets pods with the label `app: logstash` (our Logstash pod).*

```yaml
  ports:
    - protocol: TCP
      port: 5044
      targetPort: 5044
```

* 🔌 *Exposes Logstash on port **5044**, so Filebeat can send logs to it.*

---

### 🧠 Summary (For Beginners):

| Component       | Role                                                    |
| --------------- | ------------------------------------------------------- |
| **ConfigMap**   | Holds Logstash config (`input`, `filter`, `output`)     |
| **Deployment**  | Runs a pod using the Logstash Docker image              |
| **VolumeMount** | Injects `logstash.conf` from ConfigMap into the pod     |
| **Service**     | Exposes port `5044` for Filebeat to connect to Logstash |

✅ Once deployed, **Filebeat → Logstash → Elasticsearch → Kibana** flow is complete!

Let me know if you'd like the same for `filebeat.yaml` next!
