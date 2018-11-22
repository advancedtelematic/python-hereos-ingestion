default: ingestion_pb2.py
	@echo "Built"

ingestion_pb2.py: protos/ingestion.proto
	python -m grpc_tools.protoc -Iprotos --python_out=. --grpc_python_out=. protos/ingestion.proto

.PHONY: default
