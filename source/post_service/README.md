# ДЗ-3: GRPC


# Как протестить:

С первого терминала:

```bash
git clone https://github.com/izureta/SOA-Course.git
cd SOA-Course
cd source
docker-compose up --build
```

Со второго:

```bash
curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -H "Login: user1" -H "Password: password1" -d '{}'
curl -X POST http://localhost:5000/create_post -H "Login: user1" -H "Password: password1" -H "Content-Type: application/json" -d '{
  "user_id": "1",            
  "title": "My First Post",    
  "content": "Hahaha first post!!!"
}'
curl -X GET http://localhost:5000/get_post -H "Login: user1" -H "Password: password1" -H "Content-Type: application/json" -d '{           
  "post_id": "1"
}'
curl -X POST http://localhost:5000/update_post -H "Login: user1" -H "Password: password1" -H "Content-Type: application/json" -d '{
  "user_id": "1",            
  "post_id": "1",    
  "title": "Not my First Post",
  "content": "Hahaha not first post!!!"
}'
curl -X GET http://localhost:5000/get_post -H "Login: user1" -H "Password: password1" -H "Content-Type: application/json" -d '{           
  "post_id": "1"
}'
curl -X DELETE http://localhost:5000/delete_post -H "Login: user1" -H "Password: password1" -H "Content-Type: application/json" -d '{
  "user_id": "1",            
  "post_id": "1"
}'
curl -X GET http://localhost:5000/list_posts -H "Login: user1" -H "Password: password1" -H "Content-Type: application/json" -d '{           
  "user_id": "1"
}'
```
