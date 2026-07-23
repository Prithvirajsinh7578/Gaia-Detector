# API Documentation

## Login

POST /login

### Request

```json
{
  "email": "abc@gmail.com",
  "password": "123456"
}
```

### Response

```json
{
  "token": "JWT_TOKEN",
  "user": {
    "id": 1,
    "name": "John Doe"
  }
}
```

---

## Detect Text

POST /detect/text

### Request

```json
{
  "text": "Hello World"
}
```

### Response

```json
{
  "prediction": "Likely AI",
  "confidence": 92
}
```