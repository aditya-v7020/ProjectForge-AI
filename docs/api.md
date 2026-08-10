# ProjectForge AI — REST API Documentation

Base URL: `http://localhost:8000/api`

## Authentication

All endpoints except `/api/auth/register` and `/api/auth/login` require a Bearer token in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_token>
```

---

## 1. Auth API

### `POST /api/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

---

### `POST /api/auth/login`
Authenticate user and retrieve JWT token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

---

## 2. Projects API

### `POST /api/projects`
Create a new project.

**Request Body:**
```json
{
  "name": "E-Commerce App",
  "description": "Online store with AI recommendations",
  "raw_idea": "Build an e-commerce website for 3 people within 30 days."
}
```

---

### `POST /api/projects/{id}/requirements`
Submit raw project idea and trigger **Phase 1**: Requirement Analyst Agent + Technology Advisor Agent (with Tavily web research).

**Request Body:**
```json
{
  "project_idea": "I want to build an e-commerce website for 3 people within 30 days."
}
```

---

### `GET /api/projects/{id}/technology-options`
Retrieve generated technology alternatives per category with suitability scores, pros, cons, and AI recommendations.

---

### `POST /api/projects/{id}/technology-selection`
User selects and **LOCKS** choices per category.

**Request Body:**
```json
{
  "selections": {
    "frontend": "React",
    "backend": "FastAPI",
    "database": "PostgreSQL",
    "ai_ml": "Scikit-learn",
    "deployment": "Render",
    "authentication": "JWT"
  }
}
```

---

### `POST /api/projects/{id}/generate-plan`
Trigger **Phase 2**: Architecture Agent (using ONLY locked selections) → Task Planner → Timeline Agent → Critic Agent (revision loop max 3) → Final Blueprint.

---

### `GET /api/projects/{id}/blueprint`
Retrieve complete 20-section project blueprint report.

---

### `GET /api/projects/{id}/progress`
Server-Sent Events (SSE) endpoint for real-time agent status streaming.
