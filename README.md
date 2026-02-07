# Stratify AI - Global Multi-Factor Influence Intelligence Engine

A production-ready AI-powered platform that analyzes how macroeconomic forces, corporate decisions, regulatory actions, and geopolitical events influence assets across multiple time horizons.

## 🎯 Features

- **JWT Authentication** - Secure user authentication with bcrypt password hashing
- **Real-time Macro Data** - Integrates FRED API for economic indicators and NewsAPI for events
- **Asset Discovery** - CoinGecko integration with conversational fallback for unknown assets
- **Structured Scoring Engine** - Multi-factor influence calculation with sensitivity weighting
- **AI Narrative Layer** - Ollama-powered (local open-source LLM) plain English explanations
- **PDF Report Generation** - Professional reports using ReportLab
- **Clean Architecture** - Modular, readable code following best practices
- **AWS Ready** - Deployment configuration for production hosting

## 🛠️ Tech Stack

### Backend
- **Python** - Core language
- **FastAPI** - Modern web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **bcrypt** - Password hashing
- **ReportLab** - PDF generation

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Router** - Navigation

### APIs
- **CoinGecko** - Crypto market data
- **FRED** - Economic indicators
- **NewsAPI** - Global events
- **Ollama** - AI narratives (local open-source LLM)

## 📁 Project Structure

```
stratify-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # Database setup
│   │   ├── models/              # Database models
│   │   │   ├── user.py
│   │   │   ├── token_profile.py
│   │   │   ├── macro_event.py
│   │   │   └── report.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── user_schema.py
│   │   │   ├── auth_schema.py
│   │   │   └── asset_schema.py
│   │   ├── routes/              # API endpoints
│   │   │   ├── auth_routes.py
│   │   │   └── analysis_routes.py
│   │   ├── services/            # Business logic
│   │   │   ├── coingecko_service.py
│   │   │   ├── macro_service.py
│   │   │   ├── scoring_engine.py
│   │   │   ├── narrative_service.py
│   │   │   └── pdf_service.py
│   │   └── utils/               # Utilities
│   │       ├── security.py
│   │       └── jwt_handler.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── components/
│   │   │   └── ProbabilityCard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Ollama installed (https://ollama.com)
- API Keys (FRED, NewsAPI)

### 1. Clone Repository
```bash
git clone <repository-url>
cd stratify-ai
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp ../.env.example .env
# Edit .env with your configuration and API keys

# Initialize database
# Make sure PostgreSQL is running
# Create database: createdb stratify_db

# Run backend server
cd app
python main.py
# Or use uvicorn: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Setup environment (if needed)
# Create .env file with:
# VITE_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🔑 Environment Variables

Create a `.env` file in the backend directory with your own configuration:

```env
# Database
DATABASE_URL=sqlite:///./stratify.db

# JWT
SECRET_KEY=<generate-your-own-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API Keys
FRED_API_KEY=<get-from-fred.stlouisfed.org>
NEWS_API_KEY=<get-from-newsapi.org>
COINGECKO_API_KEY=<optional-for-free-tier>

# Ollama (local LLM)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Application
APP_NAME=Stratify AI
DEBUG=False
ALLOWED_ORIGINS=http://localhost:3000
```

### Getting API Keys

1. **FRED API**: https://fred.stlouisfed.org/
   - Free registration required
   - Provides economic indicators

2. **NewsAPI**: https://newsapi.org/
   - Free tier available
   - 100 requests/day

3. **Ollama**: https://ollama.com/
   - Free & open-source, runs locally
   - Install and run: `ollama pull llama3.1:8b`
   - Other models: `mistral`, `gemma2`, `phi3`

4. **CoinGecko**: https://www.coingecko.com/en/api
   - Free tier works without key
   - Pro tier optional

## 📊 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Token profiles (for unknown assets)
CREATE TABLE token_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    token_name VARCHAR NOT NULL,
    token_type VARCHAR,
    volatility_level FLOAT,
    liquidity_sensitivity FLOAT,
    regulation_sensitivity FLOAT,
    interest_rate_sensitivity FLOAT,
    geopolitical_sensitivity FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Macro events
CREATE TABLE macro_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR NOT NULL,
    event_description TEXT,
    severity_score FLOAT,
    sentiment_score FLOAT,
    recency_score FLOAT,
    attention_score FLOAT,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analysis reports
CREATE TABLE reports (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    token_name VARCHAR NOT NULL,
    short_term_prob FLOAT,
    medium_term_prob FLOAT,
    long_term_prob FLOAT,
    short_term_narrative TEXT,
    medium_term_narrative TEXT,
    long_term_narrative TEXT,
    most_likely_scenario TEXT,
    confidence_level VARCHAR,
    pdf_path VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔐 Authentication Flow

1. User registers with email and password
2. Password is hashed with bcrypt
3. User logs in with credentials
4. JWT token is generated and returned
5. Token is included in all subsequent requests
6. Protected routes verify token before processing

## 🧮 Scoring Engine Logic

### Influence Calculation

```
Influence Score = Asset Sensitivity × Event Severity × Sentiment × Recency × Attention
```

### Time Horizon Probabilities

- **Short-term (0-4 weeks)**: Events from last 30 days, weighted 60%
- **Medium-term (1-6 months)**: Events from last 6 months, weighted 30%
- **Long-term (6-24 months)**: All events, weighted 10%

### Asset Sensitivities

- Volatility Level
- Liquidity Sensitivity
- Regulation Sensitivity
- Interest Rate Sensitivity
- Geopolitical Sensitivity

## 📄 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user (protected)

### Analysis
- `POST /analysis/analyze` - Analyze an asset (protected)
- `GET /analysis/reports` - Get user's reports (protected)
- `POST /analysis/generate-pdf/{report_id}` - Generate PDF report (protected)

## 🚢 AWS Deployment

### Backend Deployment (EC2)

1. **Launch EC2 Instance**
   - Ubuntu 24.04 LTS
   - t2.medium or larger
   - Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **Setup Server**
```bash
# SSH into instance
ssh ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y
```

3. **Deploy Application**
```bash
# Clone repository
git clone <your-repo>
cd stratify-ai/backend

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment variables
nano .env  # Add all API keys

# Install Gunicorn
pip install gunicorn
```

4. **Configure Gunicorn**

Create `/etc/systemd/system/stratify.service`:
```ini
[Unit]
Description=Stratify AI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/stratify-ai/backend/app
Environment="PATH=/home/ubuntu/stratify-ai/backend/venv/bin"
ExecStart=/home/ubuntu/stratify-ai/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

5. **Configure Nginx**

Create `/etc/nginx/sites-available/stratify`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Enable Services**
```bash
sudo systemctl enable stratify
sudo systemctl start stratify
sudo systemctl enable nginx
sudo systemctl restart nginx
```

7. **Setup HTTPS (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Frontend Deployment (S3 + CloudFront)

1. **Build Frontend**
```bash
cd frontend
npm run build
```

2. **Create S3 Bucket**
- Enable static website hosting
- Upload `dist/` folder contents

3. **Configure CloudFront**
- Create distribution
- Point to S3 bucket
- Configure SSL certificate

### Database (RDS)

1. Create PostgreSQL RDS instance
2. Update `DATABASE_URL` in backend `.env`
3. Run migrations

## 🧪 Testing

### Test Login System
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### Test Analysis
```bash
# Login first to get token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | jq -r .access_token)

# Analyze asset
curl -X POST http://localhost:8000/analysis/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"asset_name":"Bitcoin"}'
```

## 📈 Usage

1. **Register/Login** - Create account or log in
2. **Enter Asset Name** - Type asset name (e.g., "Bitcoin")
3. **View Analysis** - See probability scores and narratives
4. **Download PDF** - Generate professional report
5. **View History** - Check past analyses

## 🔧 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
cd app
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## 📝 Code Quality

- Clean, modular architecture
- Comprehensive comments
- Type hints in Python
- Error handling throughout
- Security best practices
- No hardcoded secrets

## 🤝 Contributing

This is a production-ready application. Code follows these principles:

- Simple and readable
- Well-commented
- Modular structure
- Security-focused
- Performance-optimized

## 📄 License

Private project - All rights reserved

## 🆘 Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review environment variables
3. Verify API keys are valid
4. Check logs for errors

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Custom asset profile builder UI
- [ ] Historical analysis comparison
- [ ] Email report delivery
- [ ] Mobile app
- [ ] Advanced charting
- [ ] Real-time notifications

---

**Stratify AI** - Professional macro intelligence for informed decision-making
