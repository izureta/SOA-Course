FROM python:3.9

WORKDIR /app

COPY user_service/requirements.txt .

RUN pip install -r requirements.txt

COPY user_service/ /app/user_service/

COPY proto/ /app/user_service/proto/

RUN python -m grpc_tools.protoc --proto_path=./user_service/proto/ --python_out=./user_service/ --grpc_python_out=./user_service/ ./user_service/proto/posts.proto

EXPOSE 5000

CMD ["python", "user_service/app.py"]
