
---

## 🚀 What is Filebeat?

**Filebeat** is a lightweight log shipper that **collects logs from each Kubernetes node** and sends them to **Logstash**.

---

## 💡 What is a DaemonSet?

> A **DaemonSet** ensures that **one pod runs on every node** in the Kubernetes cluster.
>
> In this case: One Filebeat pod is installed **on each node** to collect logs from containers.

---

### 🔷 PART 1: `ConfigMap` (Stores Filebeat Config)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: logging
  labels:
    k8s-app: filebeat
```

* Creates a config map named `filebeat-config` in the `logging` namespace.

```yaml
data:
  filebeat.yml: |-
    filebeat.inputs:
    - type: container
      paths:
        - /var/log/containers/*.log
```

* Filebeat will read log files from Kubernetes containers.

```yaml
      processors:
        - add_kubernetes_metadata:
            host: ${NODE_NAME}
            matchers:
            - logs_path:
                logs_path: "/var/log/containers/"
```

* Adds Kubernetes metadata (pod name, namespace, etc.) to each log line.

```yaml
    processors:
      - add_cloud_metadata:
      - add_host_metadata:
```

* Adds cloud and host-level metadata for better visibility.

```yaml
    output.logstash:
      hosts: ["logstash.logging.svc.cluster.local:5044"]
```

* Sends logs to Logstash at port 5044 inside the cluster.

---

### 🔷 PART 2: `DaemonSet` (Runs Filebeat on Every Node)

```yaml
apiVersion: apps/v1
kind: DaemonSet
```

* This ensures **1 Filebeat pod per node**.

```yaml
metadata:
  name: filebeat
  namespace: logging
  labels:
    k8s-app: filebeat
```

* Names the DaemonSet and adds labels.

```yaml
spec:
  selector:
    matchLabels:
      k8s-app: filebeat
```

* Selects pods with label `k8s-app: filebeat`.

```yaml
  template:
    metadata:
      labels:
        k8s-app: filebeat
```

* Template for each pod Filebeat will create.

```yaml
    spec:
      serviceAccountName: filebeat
      terminationGracePeriodSeconds: 30
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
```

* Uses a **ServiceAccount** named `filebeat`.
* `hostNetwork: true` allows it to access host logs directly.

```yaml
      containers:
      - name: filebeat
        image: docker.elastic.co/beats/filebeat:7.17.28
```

* Uses Filebeat image version 7.17.28.

```yaml
        args: [
          "-c", "/etc/filebeat.yml",
          "-e",
        ]
```

* Tells Filebeat to use the config at `/etc/filebeat.yml`.

```yaml
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
```

* Gets the node name dynamically and injects it into the config.

```yaml
        securityContext:
          runAsUser: 0
```

* Runs Filebeat as root user (to access log files).

```yaml
        volumeMounts:
        - name: config
          mountPath: /etc/filebeat.yml
          readOnly: true
          subPath: filebeat.yml
```

* Mounts the config file into the container.

```yaml
        - name: data
          mountPath: /usr/share/filebeat/data
```

* Stores internal registry data (so logs aren't sent twice).

```yaml
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true

        - name: varlog
          mountPath: /var/log
          readOnly: true
```

* Mounts host paths to read Docker and container logs.

```yaml
      volumes:
      - name: config
        configMap:
          defaultMode: 0640
          name: filebeat-config
```

* Pulls config from the ConfigMap created earlier.

```yaml
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: varlog
        hostPath:
          path: /var/log
      - name: data
        hostPath:
          path: /var/lib/filebeat-data
          type: DirectoryOrCreate
```

* Mounts host log directories and a local path for registry data.

---

### 🔐 PART 3: RBAC Permissions (Role-Based Access Control)

> Filebeat needs permission to read Kubernetes metadata (pods, namespaces, configmaps, etc.)

#### ✅ `ServiceAccount`

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: filebeat
  namespace: logging
```

* This account will be used by the Filebeat DaemonSet.

#### ✅ `ClusterRoleBinding`

```yaml
kind: ClusterRoleBinding
subjects:
- kind: ServiceAccount
  name: filebeat
  namespace: logging
roleRef:
  kind: ClusterRole
  name: filebeat
```

* Grants cluster-wide permissions to the `filebeat` service account.

#### ✅ `RoleBindings` (Namespace-level)

* First two bind the service account to roles in the `logging` namespace.

```yaml
kind: RoleBinding
roleRef:
  kind: Role
  name: filebeat
```

```yaml
kind: RoleBinding
roleRef:
  kind: Role
  name: filebeat-kubeadm-config
```

#### ✅ `ClusterRole` (Global access to pods, nodes)

```yaml
kind: ClusterRole
rules:
- resources:
  - namespaces
  - pods
  - nodes
  verbs:
  - get
  - watch
  - list
```

* Lets Filebeat **read pod, node, and namespace info** across the cluster.

#### ✅ `Role` (Within logging namespace)

```yaml
kind: Role
rules:
  - apiGroups:
      - coordination.k8s.io
    resources:
      - leases
    verbs: ["get", "create", "update"]
```

* Needed for leader election and coordination.

#### ✅ `Role` for kubeadm config access

```yaml
kind: Role
rules:
  - resources:
      - configmaps
    resourceNames:
      - kubeadm-config
```

* Lets Filebeat read Kubernetes setup config (optional for metadata).

---

## ✅ Summary Table

| Resource           | Purpose                               |
| ------------------ | ------------------------------------- |
| **ConfigMap**      | Stores `filebeat.yml` configuration   |
| **DaemonSet**      | Runs Filebeat pod on each node        |
| **Volumes**        | Mount host log directories            |
| **RBAC Roles**     | Allow access to pods, nodes, metadata |
| **ServiceAccount** | Used by the DaemonSet to authenticate |

---
