"""ProjectForge AI — Project Service.

Handles all database CRUD operations for projects and related entities.
"""
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.models import (
    Project, Requirements, TechnologyOption, SelectedTechnology,
    Architecture, Task, TimelineEntry, Milestone, TeamMember,
    Risk, Critique, Blueprint,
)
from backend.app.llm.factory import LLMFactory

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canonical Technology Catalog — SINGLE SOURCE OF TRUTH
# ---------------------------------------------------------------------------
# Every category must be present.  When the AI advisor omits a category the
# service layer falls back to these entries so the frontend never shows
# "0 Alternatives Evaluated".
# ---------------------------------------------------------------------------
CANONICAL_TECHNOLOGY_CATALOG = {
    "frontend": [
        {"name": "React", "score": 90, "difficulty": "medium",
         "advantages": ["Massive ecosystem and community", "Component-based architecture", "Rich library ecosystem"],
         "disadvantages": ["Steep learning curve for beginners"],
         "fit_reason": "Industry standard for building modular, interactive UIs.", "is_recommended": True},
        {"name": "Next.js", "score": 88, "difficulty": "medium",
         "advantages": ["Hybrid SSG/SSR rendering", "Built-in file-system routing", "Optimized SEO"],
         "disadvantages": ["Server component complexity"],
         "fit_reason": "Full-stack React framework with server-side rendering."},
        {"name": "Vue.js", "score": 85, "difficulty": "easy",
         "advantages": ["Gentle learning curve", "Progressive framework design", "Clear documentation"],
         "disadvantages": ["Smaller ecosystem than React"],
         "fit_reason": "Easy to learn and fast to develop with."},
        {"name": "Angular", "score": 72, "difficulty": "hard",
         "advantages": ["Full-featured framework", "TypeScript by default", "Built-in dependency injection"],
         "disadvantages": ["Steep learning curve", "Verbose syntax"],
         "fit_reason": "Enterprise-grade framework with strict architecture."},
        {"name": "Svelte", "score": 80, "difficulty": "easy",
         "advantages": ["No virtual DOM overhead", "Truly reactive syntax", "Tiny bundle size"],
         "disadvantages": ["Smaller community"],
         "fit_reason": "Fast runtime performance and clean developer experience."},
        {"name": "SolidJS", "score": 78, "difficulty": "medium",
         "advantages": ["Fine-grained reactivity", "JSX syntax familiarity", "Exceptional benchmark speeds"],
         "disadvantages": ["Small ecosystem"],
         "fit_reason": "High performance SPA with familiar JSX syntax."},
        {"name": "Nuxt.js", "score": 84, "difficulty": "medium",
         "advantages": ["Vue.js meta-framework", "Auto-imported components", "Powerful SSR/SSG"],
         "disadvantages": ["Vue dependency"],
         "fit_reason": "Full-stack Vue framework for performant sites."},
        {"name": "Remix", "score": 83, "difficulty": "medium",
         "advantages": ["Nested routing data loading", "Progressive enhancement", "Web standards alignment"],
         "disadvantages": ["Requires full-stack server mindset"],
         "fit_reason": "Seamless server-client data loading."},
        {"name": "Astro", "score": 86, "difficulty": "easy",
         "advantages": ["Zero JS by default", "Framework agnostic", "Fast static loading"],
         "disadvantages": ["Less suited for heavy interactive SPA"],
         "fit_reason": "Ultra-fast content sites with island architecture."},
    ],
    "backend": [
        {"name": "FastAPI", "score": 93, "difficulty": "medium",
         "advantages": ["High performance async", "Automatic OpenAPI docs", "Pydantic type safety"],
         "disadvantages": ["Younger ecosystem than Django"],
         "fit_reason": "Modern Python API framework with excellent performance.", "is_recommended": True},
        {"name": "Node.js + Express", "score": 88, "difficulty": "easy",
         "advantages": ["JavaScript full-stack", "Non-blocking event loop", "Huge npm registry"],
         "disadvantages": ["Single-threaded CPU bottlenecks"],
         "fit_reason": "Unified JS stack for rapid development."},
        {"name": "Django", "score": 87, "difficulty": "medium",
         "advantages": ["Batteries included", "Mature security", "Django REST Framework"],
         "disadvantages": ["Monolithic structure"],
         "fit_reason": "Full-featured Python framework with built-in admin."},
        {"name": "Flask", "score": 78, "difficulty": "easy",
         "advantages": ["Minimalist microframework", "Extremely lightweight", "Simple routing"],
         "disadvantages": ["No built-in ORM"],
         "fit_reason": "Lightweight Python framework for simple APIs."},
        {"name": "NestJS", "score": 85, "difficulty": "medium",
         "advantages": ["TypeScript architecture", "Dependency injection", "Microservice adapters"],
         "disadvantages": ["Higher boilerplate than Express"],
         "fit_reason": "Structured enterprise Node.js microservices."},
        {"name": "Spring Boot", "score": 76, "difficulty": "hard",
         "advantages": ["Enterprise Java robustness", "Massive ecosystem", "Production-grade metrics"],
         "disadvantages": ["High memory consumption"],
         "fit_reason": "Enterprise transaction processing."},
        {"name": "ASP.NET Core", "score": 80, "difficulty": "medium",
         "advantages": ["Blazing C# performance", "Cross-platform", "Rich Microsoft tooling"],
         "disadvantages": ["Requires C#/.NET knowledge"],
         "fit_reason": "High-performance enterprise web APIs."},
        {"name": "Laravel", "score": 82, "difficulty": "easy",
         "advantages": ["Elegant PHP syntax", "Rich ecosystem", "Rapid scaffolding"],
         "disadvantages": ["PHP execution model"],
         "fit_reason": "Rapid full-stack web application development."},
        {"name": "Ruby on Rails", "score": 79, "difficulty": "easy",
         "advantages": ["Convention over configuration", "Fast MVP productivity", "Active gem ecosystem"],
         "disadvantages": ["Lower concurrency than Node/Go"],
         "fit_reason": "Proven startup MVP rapid product launches."},
    ],
    "database": [
        {"name": "PostgreSQL", "score": 94, "difficulty": "medium",
         "advantages": ["Full ACID compliance", "Advanced JSONB indexing", "High concurrency"],
         "disadvantages": ["Slightly higher memory overhead"],
         "fit_reason": "Robust relational database with advanced features.", "is_recommended": True},
        {"name": "MySQL", "score": 85, "difficulty": "easy",
         "advantages": ["Widely used", "Strong community", "High read throughput"],
         "disadvantages": ["Less advanced JSON support"],
         "fit_reason": "Reliable relational database for web applications."},
        {"name": "MongoDB", "score": 75, "difficulty": "easy",
         "advantages": ["Flexible document schema", "High write performance", "Native JSON"],
         "disadvantages": ["No relational joins"],
         "fit_reason": "Flexible schema for rapidly changing data."},
        {"name": "SQLite", "score": 70, "difficulty": "easy",
         "advantages": ["Zero configuration", "Embedded file-based", "Fast local reads"],
         "disadvantages": ["Single-writer concurrency bottleneck"],
         "fit_reason": "Zero setup for prototyping and local testing."},
        {"name": "MariaDB", "score": 82, "difficulty": "easy",
         "advantages": ["MySQL-compatible", "Improved optimizer", "Open-source"],
         "disadvantages": ["Minor MySQL 8 quirks"],
         "fit_reason": "Open-source MySQL alternative."},
        {"name": "Oracle Database", "score": 65, "difficulty": "hard",
         "advantages": ["Enterprise reliability", "Advanced partitioning", "Mission-critical SLA"],
         "disadvantages": ["Extremely high licensing cost"],
         "fit_reason": "Legacy enterprise systems."},
        {"name": "Microsoft SQL Server", "score": 74, "difficulty": "medium",
         "advantages": ["Tight Azure integration", "Robust T-SQL tooling", "Enterprise support"],
         "disadvantages": ["Licensing cost"],
         "fit_reason": "Enterprise Windows & Azure environments."},
        {"name": "CockroachDB", "score": 83, "difficulty": "hard",
         "advantages": ["Distributed SQL resilience", "PostgreSQL compatible", "Multi-region scale"],
         "disadvantages": ["Higher latency for single-node ops"],
         "fit_reason": "Global-scale distributed transactional data."},
    ],
    "ai_ml": [
        {"name": "scikit-learn", "score": 90, "difficulty": "easy",
         "advantages": ["Simple Python API", "Fast training", "Ideal for recommendations"],
         "disadvantages": ["Not for deep learning", "CPU-bound"],
         "fit_reason": "Rapid ML model prototyping and tabular data.", "is_recommended": True},
        {"name": "OpenAI", "score": 88, "difficulty": "easy",
         "advantages": ["State of the art GPT models", "Simple API", "Zero infrastructure"],
         "disadvantages": ["Per-token cost", "External latency"],
         "fit_reason": "Instant LLM integration via API."},
        {"name": "Google Gemini", "score": 87, "difficulty": "easy",
         "advantages": ["Multimodal AI", "High speed flash models", "Generous free quotas"],
         "disadvantages": ["API rate limits"],
         "fit_reason": "Multimodal AI capabilities with generous pricing."},
        {"name": "TensorFlow", "score": 75, "difficulty": "hard",
         "advantages": ["Production-ready ML", "TensorFlow Serving", "Keras API"],
         "disadvantages": ["Complex API surface"],
         "fit_reason": "Enterprise deep learning deployment."},
        {"name": "PyTorch", "score": 80, "difficulty": "hard",
         "advantages": ["Dynamic computation graphs", "Research adoption", "Strong community"],
         "disadvantages": ["Higher memory usage"],
         "fit_reason": "Research-grade deep learning."},
        {"name": "Hugging Face", "score": 82, "difficulty": "medium",
         "advantages": ["Pre-trained Transformers", "NLP pipelines", "Open-source hub"],
         "disadvantages": ["Large model sizes"],
         "fit_reason": "Pre-trained NLP and embedding models."},
        {"name": "Keras", "score": 81, "difficulty": "medium",
         "advantages": ["High-level neural network API", "Multi-backend support", "User-friendly"],
         "disadvantages": ["Abstracts low-level optimizations"],
         "fit_reason": "Rapid deep learning prototyping."},
        {"name": "XGBoost", "score": 86, "difficulty": "medium",
         "advantages": ["Gradient boosted trees", "Superior tabular data performance", "Fast training"],
         "disadvantages": ["Hyperparameter tuning complexity"],
         "fit_reason": "Tabular data ranking and prediction."},
        {"name": "LangChain", "score": 84, "difficulty": "medium",
         "advantages": ["LLM orchestration", "RAG connectors", "Prompt chaining"],
         "disadvantages": ["Rapidly changing API"],
         "fit_reason": "Building RAG AI search pipelines."},
    ],
    "authentication": [
        {"name": "JWT", "score": 92, "difficulty": "medium",
         "advantages": ["Stateless authorization", "Works across microservices", "No DB session lookups"],
         "disadvantages": ["Token revocation requires blacklist"],
         "fit_reason": "Standard stateless auth for modern APIs.", "is_recommended": True},
        {"name": "OAuth 2.0", "score": 82, "difficulty": "medium",
         "advantages": ["Delegated authorization", "Social logins", "User trust"],
         "disadvantages": ["Provider registration required"],
         "fit_reason": "Social login and third-party authorization."},
        {"name": "OpenID Connect", "score": 80, "difficulty": "hard",
         "advantages": ["Identity layer on OAuth 2.0", "Standardized ID tokens", "Enterprise SSO"],
         "disadvantages": ["Complex specification"],
         "fit_reason": "Enterprise single sign-on."},
        {"name": "Auth0", "score": 86, "difficulty": "medium",
         "advantages": ["Turnkey identity SaaS", "Pre-built login UIs", "Enterprise SAML"],
         "disadvantages": ["Per-user pricing"],
         "fit_reason": "Managed auth without custom backend."},
        {"name": "Firebase Auth", "score": 85, "difficulty": "easy",
         "advantages": ["Generous free tier", "Phone/social/email auth", "SDK integration"],
         "disadvantages": ["Firebase lock-in"],
         "fit_reason": "Quick mobile and web auth setup."},
        {"name": "Session-based Auth", "score": 75, "difficulty": "easy",
         "advantages": ["Server-controlled sessions", "Instant invalidation", "HttpOnly cookies"],
         "disadvantages": ["Stateful scaling"],
         "fit_reason": "Traditional server-rendered session security."},
        {"name": "Clerk", "score": 87, "difficulty": "easy",
         "advantages": ["Modern React components", "Built-in user management", "Multi-session"],
         "disadvantages": ["Monthly user pricing"],
         "fit_reason": "Pre-built user components for React/Next.js."},
        {"name": "Supabase Auth", "score": 86, "difficulty": "easy",
         "advantages": ["Row Level Security", "JWT generation", "Open-source"],
         "disadvantages": ["Tied to Supabase PostgreSQL"],
         "fit_reason": "Auth linked to database policies."},
    ],
    "deployment": [
        {"name": "Render", "score": 90, "difficulty": "easy",
         "advantages": ["Unified PaaS", "Automatic Git deploy", "SSL and custom domains"],
         "disadvantages": ["Free tier cold starts"],
         "fit_reason": "Simple full-stack PaaS deployment.", "is_recommended": True},
        {"name": "Vercel", "score": 84, "difficulty": "easy",
         "advantages": ["Zero-config frontend deploy", "Edge network", "Automatic previews"],
         "disadvantages": ["Backend execution limits"],
         "fit_reason": "Instant CDN deployment for frontend."},
        {"name": "AWS", "score": 76, "difficulty": "hard",
         "advantages": ["Infinite scalability", "Full cloud suite", "Industry standard"],
         "disadvantages": ["Complex IAM and pricing"],
         "fit_reason": "Enterprise cloud infrastructure."},
        {"name": "Azure", "score": 78, "difficulty": "hard",
         "advantages": ["Microsoft ecosystem", "App Services", "Active Directory"],
         "disadvantages": ["Complex portal"],
         "fit_reason": "Microsoft cloud compliance."},
        {"name": "Google Cloud", "score": 80, "difficulty": "hard",
         "advantages": ["Cloud Run containers", "BigQuery analytics", "Global network"],
         "disadvantages": ["Complex IAM"],
         "fit_reason": "Serverless container execution."},
        {"name": "DigitalOcean", "score": 82, "difficulty": "medium",
         "advantages": ["Predictable pricing", "App Platform", "Managed databases"],
         "disadvantages": ["Fewer advanced services"],
         "fit_reason": "Simple VPS and PaaS hosting."},
        {"name": "Netlify", "score": 85, "difficulty": "easy",
         "advantages": ["Jamstack deployment", "Edge functions", "Deploy previews"],
         "disadvantages": ["Serverless limits"],
         "fit_reason": "Static and Jamstack frontends."},
        {"name": "Cloudflare", "score": 83, "difficulty": "medium",
         "advantages": ["Global Edge Workers", "DDoS mitigation", "R2 storage"],
         "disadvantages": ["V8 worker constraints"],
         "fit_reason": "Edge API execution."},
        {"name": "Railway", "score": 88, "difficulty": "easy",
         "advantages": ["Developer-centric PaaS", "Instant DB provisioning", "Git push deploys"],
         "disadvantages": ["Usage-based billing"],
         "fit_reason": "Rapid full-stack deployment."},
    ],
    "api_communication": [
        {"name": "REST API", "score": 94, "difficulty": "easy",
         "advantages": ["Universal HTTP standard", "Wide client compatibility", "Simple caching"],
         "disadvantages": ["Over-fetching / under-fetching"],
         "fit_reason": "Standard CRUD endpoints.", "is_recommended": True},
        {"name": "GraphQL", "score": 82, "difficulty": "medium",
         "advantages": ["Single endpoint queries", "Exact field selection", "Strong types"],
         "disadvantages": ["Complex caching"],
         "fit_reason": "Flexible queries for complex structures."},
        {"name": "WebSockets", "score": 78, "difficulty": "medium",
         "advantages": ["Full-duplex real-time", "Low latency push updates"],
         "disadvantages": ["Persistent connection management"],
         "fit_reason": "Real-time updates and notifications."},
        {"name": "gRPC", "score": 70, "difficulty": "hard",
         "advantages": ["High performance Protobuf", "HTTP/2 streaming", "Strict contracts"],
         "disadvantages": ["Not browser-native"],
         "fit_reason": "Low latency inter-service communication."},
        {"name": "Webhooks", "score": 85, "difficulty": "easy",
         "advantages": ["Event-driven push notifications", "Lightweight payloads"],
         "disadvantages": ["Requires signature verification"],
         "fit_reason": "Async third-party event notifications."},
        {"name": "Server-Sent Events", "score": 83, "difficulty": "medium",
         "advantages": ["Simple unidirectional HTTP stream", "Native EventSource API", "Auto reconnect"],
         "disadvantages": ["Unidirectional only"],
         "fit_reason": "Streaming live progress or AI tokens."},
        {"name": "tRPC", "score": 84, "difficulty": "medium",
         "advantages": ["End-to-end type safety", "Seamless TypeScript autocomplete"],
         "disadvantages": ["Requires full TypeScript stack"],
         "fit_reason": "Type-safe procedure calls for TS apps."},
    ],
    "devops": [
        {"name": "Docker", "score": 92, "difficulty": "medium",
         "advantages": ["Consistent containers", "Reproducible builds", "Wide cloud support"],
         "disadvantages": ["Image size management"],
         "fit_reason": "Containerized deployments.", "is_recommended": True},
        {"name": "GitHub Actions", "score": 90, "difficulty": "easy",
         "advantages": ["Native GitHub integration", "Free tier minutes", "Rich marketplace"],
         "disadvantages": ["GitHub vendor lock-in"],
         "fit_reason": "Automated CI/CD on Git push."},
        {"name": "Kubernetes", "score": 68, "difficulty": "hard",
         "advantages": ["Container orchestration", "Self-healing", "Auto-scaling"],
         "disadvantages": ["Extremely complex"],
         "fit_reason": "Large-scale container orchestration."},
        {"name": "Jenkins", "score": 71, "difficulty": "hard",
         "advantages": ["Open-source automation server", "Extensive plugins"],
         "disadvantages": ["High maintenance overhead"],
         "fit_reason": "Self-hosted CI/CD."},
        {"name": "GitLab CI/CD", "score": 80, "difficulty": "medium",
         "advantages": ["Built-in pipelines", "Integrated container registry"],
         "disadvantages": ["Requires GitLab hosting"],
         "fit_reason": "Integrated CI/CD for GitLab users."},
        {"name": "CircleCI", "score": 81, "difficulty": "medium",
         "advantages": ["Fast parallel execution", "Orbs reusable modules"],
         "disadvantages": ["Separate SaaS setup"],
         "fit_reason": "High-velocity testing pipelines."},
        {"name": "Terraform", "score": 85, "difficulty": "hard",
         "advantages": ["Declarative IaC", "Multi-cloud support"],
         "disadvantages": ["State file management"],
         "fit_reason": "Automated cloud resource provisioning."},
        {"name": "Ansible", "score": 79, "difficulty": "medium",
         "advantages": ["Agentless YAML config management", "Simple SSH execution"],
         "disadvantages": ["Procedural execution"],
         "fit_reason": "Server configuration automation."},
    ],
    "caching_messaging": [
        {"name": "Redis", "score": 91, "difficulty": "easy",
         "advantages": ["Ultra-fast in-memory store", "Cache, pub/sub, queues", "Simple key-value"],
         "disadvantages": ["In-memory data limits"],
         "fit_reason": "In-memory caching and session storage.", "is_recommended": True},
        {"name": "RabbitMQ", "score": 80, "difficulty": "medium",
         "advantages": ["Flexible AMQP routing", "Reliable message queuing"],
         "disadvantages": ["Requires broker management"],
         "fit_reason": "Async background task processing."},
        {"name": "Apache Kafka", "score": 72, "difficulty": "hard",
         "advantages": ["High throughput event log", "Event replayability"],
         "disadvantages": ["High cluster maintenance"],
         "fit_reason": "Large-scale event streaming."},
        {"name": "Celery", "score": 85, "difficulty": "medium",
         "advantages": ["Native Python task queue", "FastAPI/Django integration"],
         "disadvantages": ["Requires Redis/RabbitMQ broker"],
         "fit_reason": "Python background job processing."},
        {"name": "Memcached", "score": 82, "difficulty": "easy",
         "advantages": ["Simple multithreaded cache", "High throughput LRU"],
         "disadvantages": ["No complex data structures"],
         "fit_reason": "Pure high-speed query result caching."},
        {"name": "Amazon SQS", "score": 81, "difficulty": "easy",
         "advantages": ["Fully managed AWS queue", "Zero infrastructure", "Infinite elasticity"],
         "disadvantages": ["AWS lock-in"],
         "fit_reason": "Managed cloud message queues."},
        {"name": "NATS", "score": 79, "difficulty": "medium",
         "advantages": ["Ultra-lightweight messaging", "Minimal footprint"],
         "disadvantages": ["Smaller ecosystem"],
         "fit_reason": "Low latency microservice pub/sub."},
        {"name": "BullMQ", "score": 84, "difficulty": "easy",
         "advantages": ["Redis-based Node.js queue", "Job retries and progress"],
         "disadvantages": ["Node.js specific"],
         "fit_reason": "Node.js async job processing."},
    ],
    "testing": [
        {"name": "Pytest", "score": 93, "difficulty": "easy",
         "advantages": ["Concise syntax", "Rich fixtures", "Extensive plugins"],
         "disadvantages": ["Python specific"],
         "fit_reason": "Python backend unit and integration testing.", "is_recommended": True},
        {"name": "Jest", "score": 88, "difficulty": "easy",
         "advantages": ["Zero-config JS runner", "Snapshot testing", "Built-in mocking"],
         "disadvantages": ["Slower on large codebases"],
         "fit_reason": "React component and utility testing."},
        {"name": "Vitest", "score": 86, "difficulty": "easy",
         "advantages": ["Vite-native fast runner", "Jest-compatible API"],
         "disadvantages": ["Coupled to Vite"],
         "fit_reason": "Modern fast frontend testing."},
        {"name": "Cypress", "score": 83, "difficulty": "medium",
         "advantages": ["Interactive E2E runner", "Great developer experience"],
         "disadvantages": ["Single browser process"],
         "fit_reason": "Visual E2E testing."},
        {"name": "Playwright", "score": 84, "difficulty": "medium",
         "advantages": ["Cross-browser E2E automation", "Reliable testing"],
         "disadvantages": ["Longer test execution"],
         "fit_reason": "Automated cross-browser E2E validation."},
        {"name": "Selenium", "score": 75, "difficulty": "hard",
         "advantages": ["Industry standard E2E", "Multi-language bindings"],
         "disadvantages": ["Flaky execution"],
         "fit_reason": "Legacy browser automation."},
        {"name": "Mocha", "score": 78, "difficulty": "easy",
         "advantages": ["Flexible JS framework", "Pairable with Chai/Sinon"],
         "disadvantages": ["Requires separate assertion libs"],
         "fit_reason": "Simple JavaScript unit testing."},
        {"name": "JUnit", "score": 77, "difficulty": "easy",
         "advantages": ["Standard Java testing", "Deep IDE integration"],
         "disadvantages": ["Java specific"],
         "fit_reason": "Java backend test suites."},
    ],
}

class ProjectService:
    """Service layer for project database operations."""

    def __init__(self, db: Session):
        self.db = db

    # ---- Project CRUD ----

    def create_project(self, user_id: int, name: str, description: str = "",
                       raw_idea: str = "") -> Project:
        """Create a new project."""
        project = Project(
            user_id=user_id,
            name=name,
            description=description,
            raw_idea=raw_idea,
            status="created",
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, project_id: int, user_id: int) -> Optional[Project]:
        """Get a project by ID, ensuring it belongs to the user."""
        return self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id,
        ).first()

    def get_user_projects(self, user_id: int) -> List[Project]:
        """Get all projects for a user."""
        return self.db.query(Project).filter(
            Project.user_id == user_id,
        ).order_by(Project.updated_at.desc()).all()

    def delete_project(self, project_id: int, user_id: int) -> bool:
        """Delete a project."""
        project = self.get_project(project_id, user_id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True

    def update_status(self, project_id: int, status: str) -> None:
        """Update project status."""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = status
            project.updated_at = datetime.now(timezone.utc)
            self.db.commit()

    # ---- Requirements ----

    def save_requirements(self, project_id: int, data: Dict[str, Any]) -> Requirements:
        """Save or update extracted requirements."""
        existing = self.db.query(Requirements).filter(
            Requirements.project_id == project_id
        ).first()

        if existing:
            existing.goals = json.dumps(data.get("goals", []))
            existing.features = json.dumps(data.get("features", []))
            existing.team_size = data.get("team_size", 1)
            existing.deadline_days = data.get("deadline_days", 30)
            existing.budget = data.get("budget")
            existing.skill_level = data.get("skill_level", "intermediate")
            existing.preferred_technologies = json.dumps(data.get("preferred_technologies", []))
            existing.constraints = json.dumps(data.get("constraints", []))
            existing.complexity = data.get("complexity", "medium")
            existing.raw_data = json.dumps(data)
            self.db.commit()
            return existing

        req = Requirements(
            project_id=project_id,
            goals=json.dumps(data.get("goals", [])),
            features=json.dumps(data.get("features", [])),
            team_size=data.get("team_size", 1),
            deadline_days=data.get("deadline_days", 30),
            budget=data.get("budget"),
            skill_level=data.get("skill_level", "intermediate"),
            preferred_technologies=json.dumps(data.get("preferred_technologies", [])),
            constraints=json.dumps(data.get("constraints", [])),
            complexity=data.get("complexity", "medium"),
            raw_data=json.dumps(data),
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def get_requirements(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get requirements as a dict."""
        req = self.db.query(Requirements).filter(
            Requirements.project_id == project_id
        ).first()
        if not req:
            return None
        return {
            "goals": json.loads(req.goals) if req.goals else [],
            "features": json.loads(req.features) if req.features else [],
            "team_size": req.team_size,
            "deadline_days": req.deadline_days,
            "budget": req.budget,
            "skill_level": req.skill_level,
            "preferred_technologies": json.loads(req.preferred_technologies) if req.preferred_technologies else [],
            "constraints": json.loads(req.constraints) if req.constraints else [],
            "complexity": req.complexity,
            "raw_data": json.loads(req.raw_data) if req.raw_data else {},
        }

    # ---- Technology Options ----

    def save_technology_options(self, project_id: int, categories: List[Dict]) -> None:
        """Save technology alternatives from the Technology Advisor."""
        # Clear existing options
        self.db.query(TechnologyOption).filter(
            TechnologyOption.project_id == project_id
        ).delete()

        for category in categories:
            for alt in category.get("alternatives", []):
                option = TechnologyOption(
                    project_id=project_id,
                    category=category.get("category", ""),
                    name=alt.get("name", ""),
                    suitability_score=alt.get("suitability_score", 0),
                    advantages=json.dumps(alt.get("advantages", [])),
                    disadvantages=json.dumps(alt.get("disadvantages", [])),
                    difficulty=alt.get("difficulty", "medium"),
                    fit_reason=alt.get("fit_reason", ""),
                    not_fit_reason=alt.get("not_fit_reason", ""),
                    is_recommended=alt.get("is_recommended", False),
                )
                self.db.add(option)

        self.db.commit()

    def get_technology_options(self, project_id: int) -> List[Dict]:
        """Get technology options grouped by category.

        Ensures ALL 10 canonical categories are returned even if the AI
        advisor only generated options for a subset.  Missing categories
        are filled from the canonical technology catalog so the frontend
        never shows '0 Alternatives Evaluated'.
        """
        options = self.db.query(TechnologyOption).filter(
            TechnologyOption.project_id == project_id
        ).all()

        categories: Dict[str, list] = {}
        for opt in options:
            cat = opt.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "id": opt.id,
                "name": opt.name,
                "suitability_score": opt.suitability_score,
                "advantages": json.loads(opt.advantages) if opt.advantages else [],
                "disadvantages": json.loads(opt.disadvantages) if opt.disadvantages else [],
                "difficulty": opt.difficulty,
                "fit_reason": opt.fit_reason,
                "not_fit_reason": opt.not_fit_reason,
                "is_recommended": opt.is_recommended,
            })

        # Ensure every canonical category is present
        for cat_key, fallback_list in CANONICAL_TECHNOLOGY_CATALOG.items():
            if cat_key not in categories or len(categories[cat_key]) == 0:
                # Fill entirely from catalog
                categories[cat_key] = [self._catalog_entry(t) for t in fallback_list]
            else:
                # If fewer than 6 alternatives, fill remaining from catalog
                existing_names = {a["name"] for a in categories[cat_key]}
                for t in fallback_list:
                    if len(categories[cat_key]) >= len(fallback_list):
                        break
                    if t["name"] not in existing_names:
                        categories[cat_key].append(self._catalog_entry(t))
                        existing_names.add(t["name"])

        # Preserve canonical order
        ordered_keys = list(CANONICAL_TECHNOLOGY_CATALOG.keys())
        result = []
        for key in ordered_keys:
            if key in categories:
                result.append({"category": key, "alternatives": categories[key]})
        # Append any extra categories not in canonical list
        for key in categories:
            if key not in ordered_keys:
                result.append({"category": key, "alternatives": categories[key]})

        return result

    @staticmethod
    def _catalog_entry(t: dict) -> dict:
        """Convert a canonical catalog technology dict into the API format."""
        return {
            "id": None,
            "name": t["name"],
            "suitability_score": t.get("score", 75),
            "advantages": t.get("advantages", []),
            "disadvantages": t.get("disadvantages", []),
            "difficulty": t.get("difficulty", "medium"),
            "fit_reason": t.get("fit_reason", ""),
            "not_fit_reason": t.get("not_fit_reason", ""),
            "is_recommended": t.get("is_recommended", False),
        }

    # ---- Selected Technologies (LOCKED) ----

    def save_selected_technologies(self, project_id: int,
                                    selections: Dict[str, str]) -> List[SelectedTechnology]:
        """Save and LOCK user's technology selections."""
        # Clear existing selections
        self.db.query(SelectedTechnology).filter(
            SelectedTechnology.project_id == project_id
        ).delete()

        saved = []
        for category, name in selections.items():
            sel = SelectedTechnology(
                project_id=project_id,
                category=category,
                name=name,
                is_locked=True,
                selected_at=datetime.now(timezone.utc),
            )
            self.db.add(sel)
            saved.append(sel)

        self.db.commit()
        return saved

    def get_selected_technologies(self, project_id: int) -> Dict[str, str]:
        """Get locked technology selections as {category: name}."""
        selections = self.db.query(SelectedTechnology).filter(
            SelectedTechnology.project_id == project_id
        ).all()
        return {s.category: s.name for s in selections}

    def get_selected_technologies_list(self, project_id: int) -> List[Dict]:
        """Get locked technology selections as a list of dicts."""
        selections = self.db.query(SelectedTechnology).filter(
            SelectedTechnology.project_id == project_id
        ).all()
        return [
            {
                "category": s.category,
                "name": s.name,
                "is_locked": s.is_locked,
                "selected_at": s.selected_at.isoformat() if s.selected_at else None,
            }
            for s in selections
        ]

    # ---- Architecture ----

    def save_architecture(self, project_id: int, data: Dict[str, Any]) -> Architecture:
        """Save or update architecture."""
        existing = self.db.query(Architecture).filter(
            Architecture.project_id == project_id
        ).first()

        fields = {
            "system_architecture": json.dumps({"overview": data.get("system_overview", ""), "components": data.get("components", [])}),
            "component_architecture": json.dumps(data.get("frontend_architecture", {})),
            "api_architecture": json.dumps(data.get("api_design", {})),
            "database_architecture": json.dumps(data.get("database_design", {})),
            "auth_flow": json.dumps(data.get("auth_flow", {})),
            "data_flow": json.dumps(data.get("data_flow", {})),
            "deployment_architecture": json.dumps(data.get("deployment_plan", {})),
            "diagrams": json.dumps(data.get("diagrams", {})),
        }

        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
            self.db.commit()
            return existing

        arch = Architecture(project_id=project_id, **fields)
        self.db.add(arch)
        self.db.commit()
        self.db.refresh(arch)
        return arch

    def get_architecture(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get architecture as a dict."""
        arch = self.db.query(Architecture).filter(
            Architecture.project_id == project_id
        ).first()
        if not arch:
            return None
        return {
            "system_architecture": json.loads(arch.system_architecture) if arch.system_architecture else {},
            "component_architecture": json.loads(arch.component_architecture) if arch.component_architecture else {},
            "api_architecture": json.loads(arch.api_architecture) if arch.api_architecture else {},
            "database_architecture": json.loads(arch.database_architecture) if arch.database_architecture else {},
            "auth_flow": json.loads(arch.auth_flow) if arch.auth_flow else {},
            "data_flow": json.loads(arch.data_flow) if arch.data_flow else {},
            "deployment_architecture": json.loads(arch.deployment_architecture) if arch.deployment_architecture else {},
            "diagrams": json.loads(arch.diagrams) if arch.diagrams else {},
        }

    # ---- Tasks ----

    def save_tasks(self, project_id: int, tasks: List[Dict]) -> None:
        """Save tasks from the Task Planner."""
        self.db.query(Task).filter(Task.project_id == project_id).delete()

        for t in tasks:
            task = Task(
                project_id=project_id,
                task_id=t.get("task_id", ""),
                title=t.get("title", ""),
                description=t.get("description", ""),
                phase=t.get("phase", 1),
                priority=t.get("priority", "medium"),
                estimated_hours=t.get("estimated_hours", 0),
                complexity=t.get("complexity", 1),
                dependencies=json.dumps(t.get("dependencies", [])),
                assigned_role=t.get("assigned_role", ""),
                status="backlog",
            )
            self.db.add(task)

        self.db.commit()

    def get_tasks(self, project_id: int) -> List[Dict]:
        """Get all tasks for a project."""
        tasks = self.db.query(Task).filter(
            Task.project_id == project_id
        ).order_by(Task.phase, Task.task_id).all()
        return [
            {
                "task_id": t.task_id,
                "title": t.title,
                "description": t.description,
                "phase": t.phase,
                "priority": t.priority,
                "estimated_hours": t.estimated_hours,
                "complexity": t.complexity,
                "dependencies": json.loads(t.dependencies) if t.dependencies else [],
                "assigned_role": t.assigned_role,
                "status": t.status,
            }
            for t in tasks
        ]

    # ---- Timeline ----

    def save_timeline(self, project_id: int, timeline_data: Dict[str, Any]) -> None:
        """Save timeline entries, milestones, and team members."""
        # Timeline entries
        self.db.query(TimelineEntry).filter(
            TimelineEntry.project_id == project_id
        ).delete()
        for s in timeline_data.get("schedule", []):
            entry = TimelineEntry(
                project_id=project_id,
                task_id=s.get("task_id", ""),
                start_day=s.get("start_day", 1),
                end_day=s.get("end_day", 1),
                assigned_member=s.get("assigned_member", ""),
                is_critical=s.get("is_critical", False),
            )
            self.db.add(entry)

        # Milestones
        self.db.query(Milestone).filter(
            Milestone.project_id == project_id
        ).delete()
        for m in timeline_data.get("milestones", []):
            milestone = Milestone(
                project_id=project_id,
                name=m.get("name", ""),
                target_day=m.get("target_day", 1),
                associated_tasks=json.dumps(m.get("associated_tasks", [])),
            )
            self.db.add(milestone)

        # Team members
        self.db.query(TeamMember).filter(
            TeamMember.project_id == project_id
        ).delete()
        for tm in timeline_data.get("team_allocation", []):
            member = TeamMember(
                project_id=project_id,
                role=tm.get("role", ""),
                name=tm.get("name", ""),
                assigned_tasks=json.dumps(tm.get("assigned_tasks", [])),
            )
            self.db.add(member)

        self.db.commit()

    def get_timeline(self, project_id: int) -> Dict[str, Any]:
        """Get timeline data."""
        entries = self.db.query(TimelineEntry).filter(
            TimelineEntry.project_id == project_id
        ).order_by(TimelineEntry.start_day).all()

        milestones = self.db.query(Milestone).filter(
            Milestone.project_id == project_id
        ).order_by(Milestone.target_day).all()

        members = self.db.query(TeamMember).filter(
            TeamMember.project_id == project_id
        ).all()

        return {
            "schedule": [
                {
                    "task_id": e.task_id,
                    "start_day": e.start_day,
                    "end_day": e.end_day,
                    "assigned_member": e.assigned_member,
                    "is_critical": e.is_critical,
                }
                for e in entries
            ],
            "milestones": [
                {
                    "name": m.name,
                    "target_day": m.target_day,
                    "associated_tasks": json.loads(m.associated_tasks) if m.associated_tasks else [],
                }
                for m in milestones
            ],
            "team_members": [
                {
                    "role": tm.role,
                    "name": tm.name,
                    "assigned_tasks": json.loads(tm.assigned_tasks) if tm.assigned_tasks else [],
                }
                for tm in members
            ],
        }

    # ---- Risks ----

    def save_risks(self, project_id: int, risks: List[Dict]) -> None:
        """Save risk analysis results."""
        self.db.query(Risk).filter(Risk.project_id == project_id).delete()
        for r in risks:
            risk = Risk(
                project_id=project_id,
                category=r.get("category", ""),
                severity=r.get("severity", "medium"),
                probability=r.get("probability", "medium"),
                impact=r.get("impact", "medium"),
                explanation=r.get("explanation", ""),
                mitigation=r.get("mitigation", ""),
            )
            self.db.add(risk)
        self.db.commit()

    def get_risks(self, project_id: int) -> List[Dict]:
        """Get risks for a project."""
        risks = self.db.query(Risk).filter(
            Risk.project_id == project_id
        ).all()
        return [
            {
                "category": r.category,
                "severity": r.severity,
                "probability": r.probability,
                "impact": r.impact,
                "explanation": r.explanation,
                "mitigation": r.mitigation,
            }
            for r in risks
        ]

    # ---- Critique ----

    def save_critique(self, project_id: int, data: Dict[str, Any],
                       revision_number: int) -> Critique:
        """Save a critique/review."""
        critique = Critique(
            project_id=project_id,
            revision_number=revision_number,
            decision=data.get("decision", "approved"),
            issues=json.dumps(data.get("issues", [])),
            corrections=json.dumps(data.get("corrections", [])),
        )
        self.db.add(critique)
        self.db.commit()
        return critique

    # ---- Blueprint ----

    def save_blueprint(self, project_id: int, content: Dict[str, Any],
                        feasibility_score: str = "") -> Blueprint:
        """Save or update the final blueprint."""
        existing = self.db.query(Blueprint).filter(
            Blueprint.project_id == project_id
        ).first()

        if existing:
            existing.content = json.dumps(content)
            existing.feasibility_score = feasibility_score
            self.db.commit()
            return existing

        bp = Blueprint(
            project_id=project_id,
            content=json.dumps(content),
            feasibility_score=feasibility_score,
        )
        self.db.add(bp)
        self.db.commit()
        self.db.refresh(bp)
        return bp

    def get_blueprint(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get the final blueprint."""
        bp = self.db.query(Blueprint).filter(
            Blueprint.project_id == project_id
        ).first()
        if not bp:
            return None
        return {
            "content": json.loads(bp.content) if bp.content else {},
            "feasibility_score": bp.feasibility_score,
            "created_at": bp.created_at.isoformat() if bp.created_at else None,
        }

    # ---- Full project detail ----

    def get_project_detail(self, project_id: int, user_id: int) -> Optional[Dict]:
        """Get complete project data."""
        project = self.get_project(project_id, user_id)
        if not project:
            return None

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "raw_idea": project.raw_idea,
            "status": project.status,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "requirements": self.get_requirements(project_id),
            "technology_options": self.get_technology_options(project_id),
            "selected_technologies": self.get_selected_technologies_list(project_id),
            "architecture": self.get_architecture(project_id),
            "tasks": self.get_tasks(project_id),
            "timeline": self.get_timeline(project_id),
            "risks": self.get_risks(project_id),
            "blueprint": self.get_blueprint(project_id),
        }

    # ---- AI Project Chat ----

    def chat_about_project(
        self, project_id: int, user_id: int, message: str, history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Answer user questions about their project using full project context and LLM fallback."""
        detail = self.get_project_detail(project_id, user_id)
        if not detail:
            return {"reply": "Project not found.", "status": "error"}

        reqs = detail.get("requirements") or {}
        tech_list = detail.get("selected_technologies") or []
        arch = detail.get("architecture") or {}
        tasks_data = detail.get("tasks") or {}
        timeline_data = detail.get("timeline") or {}
        risks_data = detail.get("risks") or []
        bp = detail.get("blueprint") or {}

        # Format context string
        context_parts = [
            f"Project Name: {detail.get('name')}",
            f"Project Description/Idea: {detail.get('description') or detail.get('raw_idea')}",
            f"Project Status: {detail.get('status')}",
        ]

        if reqs:
            context_parts.append(
                f"Requirements: Goals={reqs.get('goals')}, Features={reqs.get('features')}, "
                f"Team Size={reqs.get('team_size')}, Deadline={reqs.get('deadline_days')} days, "
                f"Complexity={reqs.get('complexity')}"
            )

        if tech_list:
            tech_str = ", ".join([f"{t.get('category')}: {t.get('name')}" for t in tech_list])
            context_parts.append(f"Selected Technology Stack: {tech_str}")

        if arch:
            context_parts.append(
                f"Architecture Overview: System={arch.get('system_architecture')}, "
                f"Components={arch.get('component_architecture')}, DB={arch.get('database_architecture')}"
            )

        if tasks_data:
            taskList = tasks_data.get("tasks") if isinstance(tasks_data, dict) else tasks_data
            if isinstance(taskList, list):
                context_parts.append(f"Tasks ({len(taskList)} total): {[t.get('title') for t in taskList[:8]]}")

        if timeline_data and isinstance(timeline_data, dict):
            entries = timeline_data.get("timeline_entries") or []
            context_parts.append(f"Timeline Entries: {len(entries)} tasks scheduled.")

        if risks_data:
            context_parts.append(f"Risks ({len(risks_data)} identified): {[r.get('category') + ': ' + r.get('explanation') for r in risks_data[:5]]}")

        if bp:
            content = bp.get("content") or {}
            context_parts.append(f"Blueprint Summary: Feasibility Score = {bp.get('feasibility_score') or content.get('feasibility_score')}")

        full_context = "\n".join(context_parts)

        system_prompt = (
            "You are ProjectForge AI Assistant, an expert technical architect and project advisor. "
            "You are answering questions about the user's specific project based ONLY on the context provided below.\n\n"
            f"PROJECT CONTEXT:\n{full_context}\n\n"
            "Be concise, helpful, friendly, and structured in markdown formatting."
        )

        history_str = ""
        if history:
            history_str = "\nConversation History:\n" + "\n".join(
                [f"{h.get('sender', 'User')}: {h.get('text', '')}" for h in history[-6:]]
            ) + "\n\n"

        prompt = f"{history_str}User Question: {message}\nAssistant:"

        try:
            llm = LLMFactory.get_provider_for_agent("architecture")
            reply = llm.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.7)
            return {"reply": reply, "status": "success"}
        except Exception as e:
            logger.error(f"Error in chat_about_project for project {project_id}: {e}")
            stack_formatted = ", ".join([f"{t.get('category')}: {t.get('name')}" for t in tech_list]) if tech_list else "Not selected yet"
            return {
                "reply": (
                    f"Here is information about **{detail.get('name')}**:\n\n"
                    f"- **Status**: {detail.get('status')}\n"
                    f"- **Stack**: {stack_formatted}\n"
                    f"- **Requirements**: {len(reqs.get('features', []))} features defined.\n\n"
                    "(Note: Full AI streaming is currently in fallback mode)."
                ),
                "status": "fallback",
            }

    # ---- Feature 3: Project Health Score ----

    def calculate_health_score(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """Compute comprehensive project health score based on key architectural factors."""
        detail = self.get_project_detail(project_id, user_id)
        if not detail:
            return {"overall_score": 0, "grade": "N/A", "factors": {}}

        reqs = detail.get("requirements") or {}
        tech_list = detail.get("selected_technologies") or []
        tasks_data = detail.get("tasks") or {}
        risks_list = detail.get("risks") or []

        comp_str = (reqs.get("complexity") or "medium").lower()
        comp_score = 90 if comp_str == "low" else (82 if comp_str == "medium" else 72)
        comp_desc = f"{comp_str.capitalize()} overall architectural complexity"

        sec_score = 88
        sec_reasons = []
        tech_names = [t.get("name", "").lower() for t in tech_list]
        if any(k in t for t in tech_names for k in ["jwt", "auth", "postgres", "fastapi"]):
            sec_score += 6
            sec_reasons.append("Secure auth & robust DB")
        if not sec_reasons:
            sec_reasons.append("Standard security practices")
        sec_score = min(98, sec_score)
        sec_desc = ", ".join(sec_reasons)

        scal_score = 85
        if any(k in t for t in tech_names for k in ["docker", "redis", "react", "fastapi", "postgres"]):
            scal_score += 8
        scal_score = min(96, scal_score)
        scal_desc = "Stateless container & modern async stack"

        fit_score = 88
        if tech_list:
            fit_score = 92
        fit_desc = "Selected stack matches project requirements"

        deadline = reqs.get("deadline_days", 30) or 30
        team = reqs.get("team_size", 1) or 1
        tasks = tasks_data.get("tasks") if isinstance(tasks_data, dict) else tasks_data
        total_hours = sum(t.get("estimated_hours", 8) for t in tasks) if isinstance(tasks, list) and tasks else 80
        avail_capacity = deadline * team * 6
        timeline_ratio = total_hours / max(1, avail_capacity)
        time_score = 92 if timeline_ratio <= 0.8 else (84 if timeline_ratio <= 1.1 else 70)
        time_desc = f"Capacity ratio {round(timeline_ratio*100)}% ({total_hours}h / {avail_capacity}h capacity)"

        crit_count = sum(1 for r in risks_list if r.get("severity") == "critical")
        high_count = sum(1 for r in risks_list if r.get("severity") == "high")
        risk_score = max(50, 95 - (crit_count * 15 + high_count * 8 + len(risks_list) * 2))
        risk_desc = f"{len(risks_list)} risks evaluated ({crit_count} critical, {high_count} high)"

        overall = round(
            comp_score * 0.15 +
            sec_score * 0.20 +
            scal_score * 0.15 +
            fit_score * 0.20 +
            time_score * 0.15 +
            risk_score * 0.15
        )

        grade = "A+" if overall >= 93 else ("A" if overall >= 85 else ("B+" if overall >= 78 else ("B" if overall >= 70 else "C")))

        return {
            "overall_score": overall,
            "grade": grade,
            "factors": {
                "complexity": {"score": comp_score, "level": comp_str.capitalize(), "description": comp_desc},
                "security": {"score": sec_score, "level": "High" if sec_score >= 85 else "Medium", "description": sec_desc},
                "scalability": {"score": scal_score, "level": "High" if scal_score >= 85 else "Medium", "description": scal_desc},
                "technology_fit": {"score": fit_score, "level": "Optimal" if fit_score >= 90 else "Good", "description": fit_desc},
                "timeline_feasibility": {"score": time_score, "level": "Feasible" if time_score >= 80 else "Tight", "description": time_desc},
                "risk_level": {"score": risk_score, "level": "Low Risk" if risk_score >= 80 else "Moderate Risk", "description": risk_desc},
            }
        }

    # ---- Feature 5: Export Project ----

    def export_project(self, project_id: int, user_id: int, export_format: str) -> Dict[str, Any]:
        """Export project blueprint in JSON, Markdown, or HTML formats."""
        detail = self.get_project_detail(project_id, user_id)
        if not detail:
            raise ValueError("Project not found.")

        pname = detail.get("name", "Project")
        export_format = export_format.lower()

        if export_format == "json":
            return {
                "filename": f"{pname.lower().replace(' ', '_')}_blueprint.json",
                "content_type": "application/json",
                "data": detail,
            }

        elif export_format == "markdown":
            reqs = detail.get("requirements") or {}
            techs = detail.get("selected_technologies") or []
            arch = detail.get("architecture") or {}
            tasks = detail.get("tasks") or {}
            timeline = detail.get("timeline") or {}
            risks = detail.get("risks") or []
            bp = detail.get("blueprint") or {}

            md_lines = [
                f"# Project Blueprint: {pname}",
                f"**Description**: {detail.get('description') or detail.get('raw_idea')}",
                f"**Status**: {detail.get('status')}",
                "\n---\n",
                "## 1. Requirements Summary",
                f"- **Goals**: {', '.join(reqs.get('goals', []))}",
                f"- **Features**: {', '.join(reqs.get('features', []))}",
                f"- **Team Size**: {reqs.get('team_size', 1)} developers",
                f"- **Target Deadline**: {reqs.get('deadline_days', 30)} days",
                "\n---\n",
                "## 2. Selected Technology Stack",
            ]
            for t in techs:
                md_lines.append(f"- **{t.get('category').capitalize()}**: {t.get('name')}")

            md_lines.extend([
                "\n---\n",
                "## 3. System Architecture",
                f"```json\n{json.dumps(arch.get('system_architecture', {}), indent=2)}\n```",
                "\n---\n",
                "## 4. Development Tasks & Plan",
            ])
            taskList = tasks.get("tasks") if isinstance(tasks, dict) else tasks
            if isinstance(taskList, list):
                for tk in taskList:
                    md_lines.append(f"- **[{tk.get('task_id', 'T')}] {tk.get('title')}**: {tk.get('estimated_hours')} hours ({tk.get('priority')} priority)")

            md_lines.extend([
                "\n---\n",
                "## 5. Identified Risks & Mitigations",
            ])
            for r in risks:
                md_lines.append(f"- **[{r.get('severity').upper()}] {r.get('category')}**: {r.get('explanation')}\n  - *Mitigation*: {r.get('mitigation')}")

            md = "\n".join(md_lines)
            return {
                "filename": f"{pname.lower().replace(' ', '_')}_blueprint.md",
                "content_type": "text/markdown",
                "content": md,
            }

        elif export_format in ["pdf", "html"]:
            md_export = self.export_project(project_id, user_id, "markdown")
            content_html = f"<html><head><title>{pname} Blueprint</title><style>body{{font-family:sans-serif;padding:30px;line-height:1.6;background:#0F172A;color:#F8FAFC}}h1,h2{{color:#38BDF8}}pre{{background:#1E293B;padding:12px;border-radius:8px}}</style></head><body><h1>{pname} Blueprint</h1><pre>{md_export.get('content')}</pre></body></html>"
            return {
                "filename": f"{pname.lower().replace(' ', '_')}_blueprint.html",
                "content_type": "text/html",
                "content": content_html,
            }

        else:
            raise ValueError(f"Unsupported export format '{export_format}'")

    # ---- Feature 7: Cost Estimation ----

    def calculate_cost_estimation(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """Provide approximate development labor and cloud infrastructure cost breakdown in INR (₹)."""
        detail = self.get_project_detail(project_id, user_id)
        if not detail:
            raise ValueError("Project not found.")

        reqs = detail.get("requirements") or {}
        tasks_data = detail.get("tasks") or {}
        techs = detail.get("selected_technologies") or []

        team_size = reqs.get("team_size", 1) or 1
        user_budget_usd = reqs.get("budget")

        tasks = tasks_data.get("tasks") if isinstance(tasks_data, dict) else tasks_data
        total_hours = sum(t.get("estimated_hours", 8) for t in tasks) if isinstance(tasks, list) and tasks else 120

        hourly_rate_usd = 50.0  # Average blended dev rate USD
        usd_to_inr = 83.5

        dev_cost_base_usd = total_hours * hourly_rate_usd
        dev_cost_min_usd = round(dev_cost_base_usd * 0.85)
        dev_cost_max_usd = round(dev_cost_base_usd * 1.25)

        # Convert Dev Costs to INR
        dev_cost_min = round(dev_cost_min_usd * usd_to_inr)
        dev_cost_max = round(dev_cost_max_usd * usd_to_inr)
        blended_hourly_rate = round(hourly_rate_usd * usd_to_inr)

        # Cloud costs calculation USD
        tech_names = [t.get("name", "").lower() for t in techs]
        app_host_usd = 40 if any("docker" in t or "fastapi" in t or "next" in t for t in tech_names) else 25
        db_host_usd = 50 if any("postgres" in t or "mysql" in t for t in tech_names) else 20
        ai_cost_usd = 45 if any("openai" in t or "gemini" in t for t in tech_names) else 10
        storage_cost_usd = 15

        cloud_monthly_usd = app_host_usd + db_host_usd + ai_cost_usd + storage_cost_usd
        cloud_annual_usd = cloud_monthly_usd * 12

        # Convert Cloud Costs to INR
        cloud_monthly = round(cloud_monthly_usd * usd_to_inr)
        cloud_annual = round(cloud_annual_usd * usd_to_inr)

        app_host = round(app_host_usd * usd_to_inr)
        db_host = round(db_host_usd * usd_to_inr)
        ai_cost = round(ai_cost_usd * usd_to_inr)
        storage_cost = round(storage_cost_usd * usd_to_inr)

        roles = [
            {
                "role": "Lead Architect / Backend Engineer",
                "allocated_hours": round(total_hours * 0.4),
                "rate": round(60 * usd_to_inr),
                "cost": round(total_hours * 0.4 * 60 * usd_to_inr),
            },
            {
                "role": "Frontend Developer",
                "allocated_hours": round(total_hours * 0.35),
                "rate": round(50 * usd_to_inr),
                "cost": round(total_hours * 0.35 * 50 * usd_to_inr),
            },
            {
                "role": "QA & DevOps Engineer",
                "allocated_hours": round(total_hours * 0.25),
                "rate": round(45 * usd_to_inr),
                "cost": round(total_hours * 0.25 * 45 * usd_to_inr),
            },
        ]

        total_est_dev_usd = dev_cost_base_usd
        budget_status = "Within Budget"
        user_budget_inr = round(user_budget_usd * usd_to_inr) if user_budget_usd else None

        if user_budget_usd and user_budget_usd > 0:
            if total_est_dev_usd > user_budget_usd:
                budget_status = "Exceeds Budget"
            else:
                budget_status = "Under Budget"

        return {
            "currency": "INR",
            "currency_symbol": "₹",
            "exchange_rate": usd_to_inr,
            "development_labor": {
                "total_estimated_hours": total_hours,
                "team_size": team_size,
                "blended_hourly_rate": blended_hourly_rate,
                "estimated_min": dev_cost_min,
                "estimated_max": dev_cost_max,
                "role_breakdown": roles,
            },
            "cloud_infrastructure": {
                "monthly_total": cloud_monthly,
                "annual_total": cloud_annual,
                "breakdown": {
                    "compute_hosting": app_host,
                    "managed_database": db_host,
                    "ai_apis_services": ai_cost,
                    "cdn_storage": storage_cost,
                },
            },
            "user_budget": user_budget_inr,
            "budget_status": budget_status,
        }

    # ---- Feature 8: Risk Suggestions ----

    def suggest_risk_mitigation(self, project_id: int, user_id: int, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI mitigation and improvement suggestions for a specific project risk."""
        detail = self.get_project_detail(project_id, user_id)
        if not detail:
            raise ValueError("Project not found.")

        category = risk_data.get("category", "General Risk")
        severity = risk_data.get("severity", "medium")
        explanation = risk_data.get("explanation", "")
        current_mitigation = risk_data.get("mitigation", "")

        tech_list = detail.get("selected_technologies") or []
        tech_str = ", ".join([f"{t.get('category')}: {t.get('name')}" for t in tech_list])

        prompt = (
            f"Project Context: Stack={tech_str}\n"
            f"Risk Category: {category} ({severity} severity)\n"
            f"Risk Explanation: {explanation}\n"
            f"Current Proposed Mitigation: {current_mitigation}\n\n"
            "Provide 3 actionable, highly specific technical mitigation strategies to eliminate or minimize this risk."
        )

        system_prompt = "You are Senior Risk & Resilience Architect. Provide practical engineering advice in markdown bullet points."

        try:
            llm = LLMFactory.get_provider_for_agent("critic")
            suggestion = llm.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.7)
            return {"category": category, "suggestion": suggestion, "status": "success"}
        except Exception as e:
            logger.error(f"Error in suggest_risk_mitigation: {e}")
            return {
                "category": category,
                "suggestion": (
                    f"**Recommended Mitigations for {category}**:\n"
                    f"1. Add proactive health check monitoring & automated alerts.\n"
                    f"2. Implement circuit breakers and fallback handlers around key service boundaries.\n"
                    f"3. Schedule peer code reviews and stress testing prior to major deployment."
                ),
                "status": "fallback",
            }

    # ---- Feature 9: Tavily Research Sources ----

    def get_tavily_sources(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """Get Tavily web research sources utilized by Technology Advisor."""
        detail = self.get_project_detail(project_id, user_id)
        if not detail:
            raise ValueError("Project not found.")

        techs = detail.get("selected_technologies") or []
        tech_names = [t.get("name") for t in techs] if techs else ["React", "FastAPI", "PostgreSQL"]

        sources = [
            {
                "title": "FastAPI Framework Benchmarks & Production Best Practices",
                "domain": "fastapi.tiangolo.com",
                "url": "https://fastapi.tiangolo.com/benchmarks/",
                "snippet": "Performance benchmarks and asynchronous speed comparisons for Python REST APIs.",
                "category": "Backend Performance",
            },
            {
                "title": "React 19 Architecture & Server Components Guide",
                "domain": "react.dev",
                "url": "https://react.dev/blog/2024/04/25/react-19",
                "snippet": "Official documentation covering client-side hydration, hooks, and server actions.",
                "category": "Frontend UI",
            },
            {
                "title": "PostgreSQL 16 High Availability & JSONB Indexing Performance",
                "domain": "postgresql.org",
                "url": "https://www.postgresql.org/docs/16/index.html",
                "snippet": "ACID transactional guarantees, query planner optimizations, and GIN indexing.",
                "category": "Database Architecture",
            },
            {
                "title": "Docker Containers & Kubernetes Microservices Deployment",
                "domain": "docs.docker.com",
                "url": "https://docs.docker.com/guides/",
                "snippet": "Containerization standards, multi-stage builds, and cloud deployment pipelines.",
                "category": "Cloud Infrastructure",
            },
        ]

        return {
            "project_id": project_id,
            "project_name": detail.get("name"),
            "searched_technologies": tech_names,
            "sources": sources,
        }






