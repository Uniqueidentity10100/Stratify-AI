# Stratify AI - API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com/api
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2024-02-07T12:00:00"
}
```

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2024-02-07T12:00:00"
}
```

---

### Analysis

#### Analyze Asset
```http
POST /analysis/analyze
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "asset_name": "Bitcoin"
}
```

**Response (200) - Asset Found:**
```json
{
  "asset_found": true,
  "asset_name": "Bitcoin",
  "symbol": "BTC",
  "probabilities": {
    "short_term": 0.652,
    "medium_term": 0.578,
    "long_term": 0.612
  },
  "narratives": {
    "short": "Bitcoin shows moderately positive short-term outlook...",
    "medium": "Medium-term factors suggest...",
    "long": "Long-term structural conditions indicate..."
  },
  "most_likely_scenario": "Based on current macro conditions...",
  "confidence_level": "High",
  "report_id": "uuid",
  "macro_events_analyzed": 8
}
```

**Response (200) - Asset Not Found:**
```json
{
  "asset_found": false,
  "message": "Asset not found in CoinGecko. Please create a custom profile.",
  "requires_profile": true
}
```

#### Get User Reports
```http
GET /analysis/reports
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "reports": [
    {
      "id": "uuid",
      "token_name": "Bitcoin",
      "short_term_prob": 0.652,
      "medium_term_prob": 0.578,
      "long_term_prob": 0.612,
      "confidence_level": "High",
      "created_at": "2024-02-07T12:00:00"
    }
  ],
  "total": 1
}
```

#### Generate PDF Report
```http
POST /analysis/generate-pdf/{report_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "PDF generated successfully",
  "pdf_path": "/tmp/stratify_reports/stratify_report_Bitcoin_20240207_120000.pdf",
  "filename": "stratify_report_Bitcoin_20240207_120000.pdf"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Report not found"
}
```

### 500 Internal Server Error
```json
{
  "message": "An internal error occurred",
  "detail": "Error details (in debug mode)"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting in production:
- 100 requests per hour per user for analysis
- 1000 requests per hour for authentication

---

## Data Models

### User
```typescript
{
  id: UUID
  email: string
  created_at: datetime
}
```

### Report
```typescript
{
  id: UUID
  token_name: string
  short_term_prob: float  // 0.0 to 1.0
  medium_term_prob: float
  long_term_prob: float
  short_term_narrative: string
  medium_term_narrative: string
  long_term_narrative: string
  most_likely_scenario: string
  confidence_level: "High" | "Medium" | "Low"
  created_at: datetime
}
```

---

## Testing with cURL

### Register and Login
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### Analyze Asset
```bash
# Get token first
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | jq -r .access_token)

# Analyze
curl -X POST http://localhost:8000/analysis/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"asset_name":"Bitcoin"}'
```

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these for testing and exploring the API.
