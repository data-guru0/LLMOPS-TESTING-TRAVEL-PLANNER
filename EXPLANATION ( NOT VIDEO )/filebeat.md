Perfect! Here's a **detailed, beginner-friendly, but slightly deeper technical explanation**, line-by-line for **every single line** of your Filebeat Kubernetes manifest, including how each part works internally. I'll keep it simple, but with some technical depth so you understand *why* it exists.

---

# 📄 **Full YAML Filebeat Kubernetes Explanation (With How It Works)**

---

## **ConfigMap - Storing Filebeat Configuration**

```yaml
apiVersion: v1
```

✅ Tells Kubernetes which API version this resource belongs to.
**`v1`** means it's a basic resource like `ConfigMap`.

```yaml
kind: ConfigMap
```

✅ The type of resource is a `ConfigMap`.
📦 Used to store non-sensitive text data (like config files) for pods to use.

```yaml
metadata:
  name: filebeat-config
  namespace: logging
  labels:
    k8s-app: filebeat
```

✅ Metadata is like the identity card:

* `name`: This ConfigMap is called `filebeat-config`.
* `namespace`: It belongs to the `logging` namespace (grouping for resources).
* `labels`: Extra tags to help filter or select resources.

```yaml
data:
  filebeat.yml: |-
```

✅ Here's where the actual data starts:

* `filebeat.yml` is the filename inside the ConfigMap.
* `|-` means multiline block follows (preserves formatting).

---

## **Filebeat Configuration**

```yaml
    filebeat.inputs:
```

✅ Defines sources where Filebeat reads logs from.

```yaml
    - type: container
```

✅ Log input type is `container`, meaning Filebeat will read logs produced by containers.

```yaml
      paths:
        - /var/log/containers/*.log
```

✅ Filebeat looks for `.log` files inside `/var/log/containers/`.
📂 Kubernetes writes container logs here on each node.

```yaml
      processors:
        - add_kubernetes_metadata:
```

✅ **Processors** enrich logs with more details.
This one adds Kubernetes info like pod name, namespace, labels, etc.

```yaml
            host: ${NODE_NAME}
```

✅ It uses an environment variable `NODE_NAME` to identify which node logs came from.

```yaml
            matchers:
            - logs_path:
                logs_path: "/var/log/containers/"
```

✅ Matcher looks at the logs from `/var/log/containers/` and associates them with correct Kubernetes metadata.

---

## **More Processors for Metadata**

```yaml
    processors:
      - add_cloud_metadata:
      - add_host_metadata:
```

✅ These processors automatically add:

* **Cloud metadata:** If running in AWS, GCP, etc., adds cloud instance info.
* **Host metadata:** Adds node details like hostname, OS, etc.

---

## **Output - Where to Send Logs**

```yaml
    output.logstash:
      hosts: ["logstash.logging.svc.cluster.local:5044"]
```

✅ Send logs to a Logstash service within the cluster:

* DNS: `logstash.logging.svc.cluster.local` → Kubernetes resolves this to the Logstash pod's IP.
* Port `5044` → Standard port for receiving logs from Filebeat.

---

# 🖥️ **DaemonSet - Run Filebeat on Every Node**

```yaml
apiVersion: apps/v1
```

✅ This uses the `apps/v1` API, needed for workloads like DaemonSet, Deployment, etc.

```yaml
kind: DaemonSet
```

✅ DaemonSet ensures:

* **One Filebeat pod runs on every node**.
* If new nodes are added, a Filebeat pod starts there automatically.

---

## **Basic Identification**

```yaml
metadata:
  name: filebeat
  namespace: logging
  labels:
    k8s-app: filebeat
```

✅ Standard resource identity:

* Name: `filebeat`
* Namespace: `logging`
* Labels: Used for filtering/selecting pods.

---

## **Spec - Pod Definition for Filebeat**

```yaml
spec:
  selector:
    matchLabels:
      k8s-app: filebeat
```

✅ Selects pods with the label `k8s-app: filebeat` to be controlled by this DaemonSet.

---

### **Pod Template Inside DaemonSet**

```yaml
  template:
    metadata:
      labels:
        k8s-app: filebeat
```

✅ Any pods created will automatically have the label `k8s-app: filebeat`.

---

## **Pod Specifications**

```yaml
    spec:
      serviceAccountName: filebeat
```

✅ Pods will use `filebeat` ServiceAccount for RBAC permissions.

```yaml
      terminationGracePeriodSeconds: 30
```

✅ When pod stops, Kubernetes waits **30 seconds** before forcefully killing it, allowing graceful shutdown.

```yaml
      hostNetwork: true
```

✅ Pod shares the node's network stack:

* Same IP as the node
* Useful for monitoring node-level logs.

```yaml
      dnsPolicy: ClusterFirstWithHostNet
```

✅ Adjusts DNS settings since pod uses host's network.

---

## **Container Definition**

```yaml
      containers:
      - name: filebeat
        image: docker.elastic.co/beats/filebeat:7.17.28
```

✅ Creates a container:

* Name: `filebeat`
* Uses Filebeat Docker image version `7.17.28`.

---

### **Startup Arguments**

```yaml
        args: [
          "-c", "/etc/filebeat.yml",
          "-e",
        ]
```

✅ Start Filebeat with:

* `-c /etc/filebeat.yml`: Tells Filebeat where to find its config.
* `-e`: Logs output goes to console (useful for debugging).

---

### **Environment Variables**

```yaml
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
```

✅ Sets `NODE_NAME` env variable dynamically with the name of the node where the pod runs.
💡 Used inside Filebeat config to attach node details to logs.

---

### **Security Context**

```yaml
        securityContext:
          runAsUser: 0
```

✅ Runs container processes as `root` (user ID 0).
Needed to access system files like `/var/log/containers/`.

```yaml
          # If using Red Hat OpenShift uncomment this:
          #privileged: true
```

✅ OpenShift often restricts container permissions.
You may need to run as privileged to access host logs.

---

## **Resource Requests and Limits**

```yaml
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 100Mi
```

✅ Defines:

* **Limits:** Max memory allowed (`200Mi`)
* **Requests:** Guaranteed minimum resources (`100m` CPU, `100Mi` memory)
  Helps prevent resource starvation.

---

## **Mount Volumes**

```yaml
        volumeMounts:
        - name: config
          mountPath: /etc/filebeat.yml
          readOnly: true
          subPath: filebeat.yml
```

✅ Mounts the `filebeat.yml` config file from ConfigMap to `/etc/filebeat.yml`.

* `readOnly`: Prevents modifications
* `subPath`: Only mounts the specific file, not the whole directory.

```yaml
        - name: data
          mountPath: /usr/share/filebeat/data
```

✅ Directory where Filebeat stores registry data:

* Keeps track of which logs were already sent.
* Avoids resending duplicate logs after pod restarts.

```yaml
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
```

✅ Mounts host's Docker container logs:

* Location varies by container runtime.
* Allows Filebeat to read raw container logs.

```yaml
        - name: varlog
          mountPath: /var/log
          readOnly: true
```

✅ Mounts the host's `/var/log` directory to access general system logs.

---

## **Volumes from Host**

```yaml
      volumes:
      - name: config
        configMap:
          defaultMode: 0640
          name: filebeat-config
```

✅ Provides the `filebeat-config` ConfigMap as a volume to the pod.

```yaml
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

✅ HostPath volume, directly mounts directory from host's filesystem.

```yaml
      - name: varlog
        hostPath:
          path: /var/log
```

✅ Same as above, mounts `/var/log` from host.

```yaml
      - name: data
        hostPath:
          path: /var/lib/filebeat-data
          type: DirectoryOrCreate
```

✅ Creates `/var/lib/filebeat-data` if it doesn't exist:

* Persistent storage for registry files, even across restarts.

---

# 🔑 **RBAC - Grant Filebeat Permissions**

## **ClusterRoleBinding - Attach ClusterRole**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: filebeat
```

✅ Gives Filebeat permissions across the whole cluster.

```yaml
subjects:
- kind: ServiceAccount
  name: filebeat
  namespace: logging
```

✅ Applies to the `filebeat` ServiceAccount in `logging` namespace.

```yaml
roleRef:
  kind: ClusterRole
  name: filebeat
  apiGroup: rbac.authorization.k8s.io
```

✅ Connects ServiceAccount to `filebeat` ClusterRole for permissions.

---

## **RoleBinding - Namespace Permissions**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: filebeat
  namespace: logging
```

✅ Grants extra permissions inside `logging` namespace only.

```yaml
subjects:
  - kind: ServiceAccount
    name: filebeat
    namespace: logging
roleRef:
  kind: Role
  name: filebeat
  apiGroup: rbac.authorization.k8s.io
```

✅ Binds ServiceAccount to `filebeat` Role for namespace-specific permissions.

---

## **Extra RoleBinding for kubeadm-config**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: filebeat-kubeadm-config
  namespace: logging
```

✅ Another RoleBinding, just for accessing the `kubeadm-config`.

```yaml
subjects:
  - kind: ServiceAccount
    name: filebeat
    namespace: logging
roleRef:
  kind: Role
  name: filebeat-kubeadm-config
  apiGroup: rbac.authorization.k8s.io
```

✅ Allows Filebeat to read `kubeadm-config` for Kubernetes cluster setup details.

---

## **ClusterRole - Global Permissions**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: filebeat
  labels:
    k8s-app: filebeat
```

✅ Defines permissions that apply cluster-wide.

```yaml
rules:
- apiGroups: [""]
  resources:
  - namespaces
  - pods
  - nodes
  verbs:
  - get
  - watch
  - list
```

✅ Allows Filebeat to:

* Read (`get`)
* Watch for changes
* List all namespaces, pods, and nodes.

```yaml
- apiGroups: ["apps"]
  resources:
    - replicasets
  verbs: ["get", "list", "watch"]
```

✅ Same for ReplicaSets:

* Useful for attaching metadata to logs about deployments.

---

## **Role for Namespace Resource Leases**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: filebeat
  namespace: logging
  labels:
    k8s-app: filebeat
```

✅ Role for working with resource leases in `logging` namespace.

```yaml
rules:
  - apiGroups:
      - coordination.k8s.io
    resources:
      - leases
    verbs: ["get", "create", "update"]
```

✅ Leases are used for coordination:

* Helps avoid conflicts if multiple Filebeat instances compete for the same task.

---

## **Role for kubeadm-config Access**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: filebeat-kubeadm-config
  namespace: logging
  labels:
    k8s-app: filebeat
```

✅ Special Role to access Kubernetes configuration.

```yaml
rules:
  - apiGroups: [""]
    resources:
      - configmaps
    resourceNames:
      - kubeadm-config
    verbs: ["get"]
```

✅ Allows read-only access to `kubeadm-config` ConfigMap, helpful for understanding cluster details.

---

# **Service Account - Identity for Filebeat**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: filebeat
  namespace: logging
  labels:
    k8s-app: filebeat
```

✅ Creates a ServiceAccount called `filebeat`.
👤 Used by pods to securely access the Kubernetes API.

---

# 🎉 **All Done!**

✅ Filebeat reads container logs from each node.
✅ Adds Kubernetes, cloud, and host metadata.
✅ Sends enriched logs to Logstash.
✅ Uses RBAC for secure access.
✅ Runs one Filebeat per node via DaemonSet.

---

Want me to explain **log flow**, **troubleshooting**, or **how Logstash connects to Elasticsearch** next? Just ask! 🚀
