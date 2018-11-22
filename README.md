HereOS Ingestion
===

This project is a simple python gRPC server that posts data to OLP. It authenticates to the platform using credentials that can be generated at https://platform.here.com, and which must be provided in a config.yaml file:

```
client_id: <YOUR_CLIENT_ID>
client_secret: <YOUR_CLIENT_SECRET>
```
