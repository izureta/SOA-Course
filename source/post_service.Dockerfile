FROM python:3.9-slim

WORKDIR /app/

COPY post_service/requirements.txt .

RUN pip install -r requirements.txt

COPY post_service/ /app/post_service/

COPY proto/ /app/post_service/proto/

RUN python -m grpc_tools.protoc --proto_path=./post_service/proto/ --python_out=./post_service/ --grpc_python_out=./post_service/ ./post_service/proto/posts.proto

EXPOSE 50051

CMD ["python", "post_service/app.py"]
