# ДЗ-2: REST API


# Как протестить:

С первого терминала:

```bash
git clone https://github.com/izureta/SOA-Course.git
cd SOA-Course
git fetch origin pull/3/head:check_hw_2
git checkout check_hw_2
cd user-service
docker-compose up --build
```

Со второго:

```bash
curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d '{"username": "user1", "password": "password1"}'
curl -X GET http://localhost:5000/users -H "Content-Type: application/json" -d '{"secret_key": "1234"}'
curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d '{"username": "user2", "password": "password2"}'
curl -X GET http://localhost:5000/users -H "Content-Type: application/json" -d '{"secret_key": "1234"}'
curl -X PUT http://localhost:5000/update -H "Content-Type: application/json" -d '{"username": "user1", "password": "password1", "first_name": "Ilya", "last_name": "Kruchinin", "birth_day": "11.11.2002", "email": "i@k.com", "phone_number": 89995553335353}'
curl -X GET http://localhost:5000/users -H "Content-Type: application/json" -d '{"secret_key": "1234"}'
```
