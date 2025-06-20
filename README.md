venv , logger , custom_exception , env , setup requirements project structure files
Project setup done...

1. src/config/config.py
2. src/chains/itinerary_chain.py
3. src/core/planner.py
4. app.py

Then Dockerfile and others so on...
K8s deployment file

- Filebeat (Log Shipper --> Sends to Logstash or directly to Elasticsearch)
- Logstash ( Processor --> Forwards cleaned logs to Elasticsearch)
- Elasticsearch ( Search Engine --> indexes them so they can be searched efficiently)
- Kibana ( Dasboard  --> Provides dashboards, queries, filters, and alerts)


VM instance and so on...