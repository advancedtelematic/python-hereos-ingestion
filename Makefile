default: ingestion_pb2.py
	@echo "Built"

ingestion_pb2.py: protos/ingestion.proto
	python -m grpc_tools.protoc -Iprotos --python_out=. --grpc_python_out=. protos/ingestion.proto

clean:
	rm -f ingestion_pb2.py ingestion_grpc_pb2.py

.PHONY: default clean
