"""ProjectForge AI — Demo Data.

Creates a sample project with pre-generated requirements and technology options
so the user can test the application without needing LLM API keys.

Technologies are NOT pre-selected — the user must select them in the UI.
"""
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.models import (
    Project, Requirements, TechnologyOption,
)


def create_demo_project(db: Session, user_id: int) -> Project:
    """Create a demo project with sample data.

    Technologies are generated but NOT selected — the user
    must explicitly select and lock them.
    """

    # --- Create Project ---
    project = Project(
        user_id=user_id,
        name="AI-Powered E-Commerce Platform",
        description="A modern e-commerce platform with AI-powered product recommendations, "
                    "user reviews, shopping cart, payment integration, and admin dashboard.",
        raw_idea="I want to build an e-commerce website for 3 people within 30 days. "
                 "It should have product listings, user authentication, shopping cart, "
                 "payment processing, and AI-powered product recommendations.",
        status="tech_analysis_done",
    )
    db.add(project)
    db.flush()

    # --- Create Requirements ---
    requirements = Requirements(
        project_id=project.id,
        goals=json.dumps([
            "Build a functional e-commerce platform",
            "Implement AI-powered product recommendations",
            "Provide secure user authentication",
            "Enable online payment processing",
            "Create an admin dashboard for product management",
        ]),
        features=json.dumps([
            "User registration and authentication",
            "Product catalog with categories and search",
            "Shopping cart and checkout flow",
            "Payment gateway integration",
            "AI product recommendations",
            "Order tracking and history",
            "Admin dashboard for inventory management",
            "Product reviews and ratings",
            "Responsive design for mobile and desktop",
            "Email notifications for orders",
        ]),
        team_size=3,
        deadline_days=30,
        budget=None,
        skill_level="intermediate",
        preferred_technologies=json.dumps([]),
        constraints=json.dumps([
            "30-day deadline",
            "Team of 3 developers",
            "Must be production-ready",
        ]),
        complexity="high",
        raw_data=json.dumps({
            "project_name": "AI-Powered E-Commerce Platform",
            "project_description": "A modern e-commerce platform with AI-powered product recommendations",
            "goals": [
                "Build a functional e-commerce platform",
                "Implement AI-powered product recommendations",
                "Provide secure user authentication",
                "Enable online payment processing",
                "Create an admin dashboard for product management",
            ],
            "features": [
                "User registration and authentication",
                "Product catalog with categories and search",
                "Shopping cart and checkout flow",
                "Payment gateway integration",
                "AI product recommendations",
                "Order tracking and history",
                "Admin dashboard for inventory management",
                "Product reviews and ratings",
                "Responsive design for mobile and desktop",
                "Email notifications for orders",
            ],
            "team_size": 3,
            "deadline_days": 30,
            "budget": None,
            "skill_level": "intermediate",
            "preferred_technologies": [],
            "constraints": [
                "30-day deadline",
                "Team of 3 developers",
                "Must be production-ready",
            ],
            "complexity": "high",
            "special_requirements": [
                "AI/ML for product recommendations",
                "Secure payment handling",
            ],
        }),
    )
    db.add(requirements)

    # --- Create Technology Options (4 options per category) ---
    tech_options = [
        # 1. Frontend
        {"category": "frontend", "name": "React", "score": 92, "difficulty": "medium",
         "advantages": ["Massive ecosystem and community", "Component-based architecture", "Rich library ecosystem (Redux, React Router)"],
         "disadvantages": ["Steep learning curve for beginners", "Requires additional libraries for full state management"],
         "fit": "React's component architecture is ideal for building modular e-commerce UIs with reusable product cards and cart panels.",
         "not_fit": "Requires boilerplate configuration compared to lightweight frameworks.",
         "recommended": True},

        {"category": "frontend", "name": "Next.js", "score": 89, "difficulty": "medium",
         "advantages": ["Hybrid SSG / SSR rendering", "Built-in file-system routing", "Optimized SEO and image handling"],
         "disadvantages": ["Vendor lock-in optimizations for Vercel", "Server component complexity"],
         "fit": "Excellent for e-commerce performance with server-rendered product pages for SEO.",
         "not_fit": "Adds server complexity if simple static SPA is desired.",
         "recommended": False},

        {"category": "frontend", "name": "Vue.js", "score": 85, "difficulty": "easy",
         "advantages": ["Gentle learning curve", "Progressive framework design", "Clear documentation and template syntax"],
         "disadvantages": ["Smaller ecosystem than React", "Fewer enterprise examples"],
         "fit": "Easy to learn and fast to develop with. Great for small teams wanting rapid delivery.",
         "not_fit": "Fewer ready-made e-commerce component kits compared to React.",
         "recommended": False},

        {"category": "frontend", "name": "Angular", "score": 72, "difficulty": "hard",
         "advantages": ["Full-featured framework", "TypeScript by default", "Built-in dependency injection"],
         "disadvantages": ["Steep learning curve", "Verbose syntax and heavy bundle size"],
         "fit": "Great for large enterprise applications with strict architectural requirements.",
         "not_fit": "Too heavy and complex for a 3-person team with a 30-day deadline.",
         "recommended": False},

        {"category": "frontend", "name": "Svelte", "score": 80, "difficulty": "easy",
         "advantages": ["No virtual DOM overhead", "Truly reactive syntax", "Tiny bundle size and high speed"],
         "disadvantages": ["Smaller community", "Fewer third-party UI component packages"],
         "fit": "Extremely fast runtime performance and clean developer experience.",
         "not_fit": "Niche ecosystem may require writing custom components from scratch.",
         "recommended": False},

        {"category": "frontend", "name": "SolidJS", "score": 78, "difficulty": "medium",
         "advantages": ["Fine-grained reactivity without virtual DOM", "JSX syntax familiarity", "Exceptional benchmark speeds"],
         "disadvantages": ["Small ecosystem", "Fewer UI component libraries"],
         "fit": "High performance SPA rendering with familiar JSX template syntax.",
         "not_fit": "Smaller developer ecosystem for rapid hiring.",
         "recommended": False},

        {"category": "frontend", "name": "Nuxt.js", "score": 84, "difficulty": "medium",
         "advantages": ["Vue.js meta-framework", "Auto-imported components", "Powerful SSR and SSG capabilities"],
         "disadvantages": ["Vue dependency", "Nuxt 3 migration learning curve"],
         "fit": "Full-stack Vue framework ideal for content-heavy performant sites.",
         "not_fit": "Requires Vue expertise.",
         "recommended": False},

        {"category": "frontend", "name": "Remix", "score": 83, "difficulty": "medium",
         "advantages": ["Nested routing data loading", "Progressive enhancement built-in", "Web standards alignment"],
         "disadvantages": ["Requires full-stack server mindset"],
         "fit": "Seamless server-client data loading and optimistic UI updates.",
         "not_fit": "Requires node runtime server deployment.",
         "recommended": False},

        {"category": "frontend", "name": "Astro", "score": 86, "difficulty": "easy",
         "advantages": ["Zero JS by default island architecture", "Framework agnostic (use React/Vue/Svelte)", "Fast static loading"],
         "disadvantages": ["Less suited for highly interactive dynamic SPA state"],
         "fit": "Ultra-fast product landing pages and marketing sites.",
         "not_fit": "Heavy client-side interactive state management requires islands.",
         "recommended": False},

        # 2. Backend
        {"category": "backend", "name": "FastAPI", "score": 93, "difficulty": "medium",
         "advantages": ["High performance (async native)", "Automatic OpenAPI documentation", "Pydantic type safety"],
         "disadvantages": ["Younger ecosystem than Django", "Requires manual ORM setup"],
         "fit": "Fast development speed, built-in OpenAPI docs, and seamless integration with Python AI libraries.",
         "not_fit": "Requires manual authentication setup.",
         "recommended": True},

        {"category": "backend", "name": "Node.js + Express", "score": 88, "difficulty": "easy",
         "advantages": ["JavaScript across frontend and backend", "Non-blocking event loop", "Huge npm package registry"],
         "disadvantages": ["Single-threaded CPU bottlenecks", "Requires TypeScript for strict typing"],
         "fit": "Unified JS stack enables high team velocity and rapid endpoint building.",
         "not_fit": "Less native ML library support compared to Python.",
         "recommended": False},

        {"category": "backend", "name": "Django", "score": 87, "difficulty": "medium",
         "advantages": ["Batteries included (ORM, Admin, Auth)", "Mature security features", "Django REST Framework"],
         "disadvantages": ["Monolithic structure", "Higher memory footprint than microframeworks"],
         "fit": "Built-in admin panel and ORM accelerate e-commerce product catalog management.",
         "not_fit": "Heavier monolith structure when lightweight microservices are preferred.",
         "recommended": False},

        {"category": "backend", "name": "Flask", "score": 78, "difficulty": "easy",
         "advantages": ["Minimalist microframework", "Extremely lightweight", "Simple route definitions"],
         "disadvantages": ["No built-in ORM or auth", "Requires manual structure as app grows"],
         "fit": "Lightweight Python framework perfect for simple API backends.",
         "not_fit": "Lacks async speed of FastAPI and batteries-included feature set of Django.",
         "recommended": False},

        {"category": "backend", "name": "NestJS", "score": 85, "difficulty": "medium",
         "advantages": ["Angular-inspired TypeScript architecture", "Dependency injection", "Built-in microservice adapters"],
         "disadvantages": ["Higher boilerplate than Express"],
         "fit": "Structured scalable enterprise Node.js microservices.",
         "not_fit": "Overhead for tiny prototype APIs.",
         "recommended": False},

        {"category": "backend", "name": "Spring Boot", "score": 76, "difficulty": "hard",
         "advantages": ["Enterprise Java robustness", "Massive ecosystem", "Production-grade metrics and security"],
         "disadvantages": ["High memory consumption", "Verbose configuration"],
         "fit": "High throughput enterprise transaction processing.",
         "not_fit": "Too heavy for small rapid dev MVPs.",
         "recommended": False},

        {"category": "backend", "name": "ASP.NET Core", "score": 80, "difficulty": "medium",
         "advantages": ["Blazing C# performance", "Cross-platform runtime", "Rich Microsoft enterprise tooling"],
         "disadvantages": ["Requires C#/.NET knowledge"],
         "fit": "High-performance enterprise web APIs.",
         "not_fit": "Team skill alignment if Python/JS is preferred.",
         "recommended": False},

        {"category": "backend", "name": "Laravel", "score": 82, "difficulty": "easy",
         "advantages": ["Elegant PHP syntax", "Rich ecosystem (Eloquent, Artisan)", "Rapid web app scaffolding"],
         "disadvantages": ["PHP execution model"],
         "fit": "Rapid full-stack web application development.",
         "not_fit": "Less suitable for heavy real-time async pipelines.",
         "recommended": False},

        {"category": "backend", "name": "Ruby on Rails", "score": 79, "difficulty": "easy",
         "advantages": ["Convention over configuration", "Fast MVP developer productivity", "Active gem ecosystem"],
         "disadvantages": ["Lower CPU concurrency speed than Node/Go"],
         "fit": "Proven startup MVP rapid product launches.",
         "not_fit": "Higher memory and scaling footprint.",
         "recommended": False},

        # 3. Database
        {"category": "database", "name": "PostgreSQL", "score": 94, "difficulty": "medium",
         "advantages": ["Full ACID compliance", "Advanced JSONB indexing", "High concurrency and reliability"],
         "disadvantages": ["Slightly higher memory overhead", "More complex tuning"],
         "fit": "Relational integrity for orders and payments combined with JSONB for flexible product attributes.",
         "not_fit": "Requires explicit database server management.",
         "recommended": True},

        {"category": "database", "name": "MySQL", "score": 85, "difficulty": "easy",
         "advantages": ["Widely used relational DB", "Strong community and hosting support", "High read throughput"],
         "disadvantages": ["Less advanced JSON support than PostgreSQL", "Fewer complex data types"],
         "fit": "Reliable relational database for traditional e-commerce order management.",
         "not_fit": "Lacks advanced JSON/indexing features offered by PostgreSQL.",
         "recommended": False},

        {"category": "database", "name": "MongoDB", "score": 75, "difficulty": "easy",
         "advantages": ["Flexible document schema", "High write performance", "Native JSON representation"],
         "disadvantages": ["No relational joins", "Requires careful schema modeling for transactions"],
         "fit": "Ideal for rapidly changing product catalog structures.",
         "not_fit": "Financial orders and user relations are inherently relational.",
         "recommended": False},

        {"category": "database", "name": "SQLite", "score": 70, "difficulty": "easy",
         "advantages": ["Zero configuration required", "Embedded file-based DB", "Extremely fast local reads"],
         "disadvantages": ["Single-writer lock concurrency bottleneck", "Not suitable for multi-server production"],
         "fit": "Zero setup overhead for rapid prototyping and local testing.",
         "not_fit": "Concurrency bottlenecks under high user traffic.",
         "recommended": False},

        {"category": "database", "name": "MariaDB", "score": 82, "difficulty": "easy",
         "advantages": ["Open-source MySQL drop-in enhancement", "Improved query optimizer", "MariaDB ColumnStore"],
         "disadvantages": ["Minor compatibility quirks with MySQL 8"],
         "fit": "Drop-in open-source relational alternative to MySQL.",
         "not_fit": "Fewer managed cloud DB offerings.",
         "recommended": False},

        {"category": "database", "name": "Oracle Database", "score": 65, "difficulty": "hard",
         "advantages": ["Enterprise Grade Reliability", "Advanced partitioning and security", "Mission-critical transaction SLA"],
         "disadvantages": ["Extremely high licensing cost", "Heavy administration overhead"],
         "fit": "Legacy enterprise banking and financial backend systems.",
         "not_fit": "Prohibitive cost and complexity for startups.",
         "recommended": False},

        {"category": "database", "name": "Microsoft SQL Server", "score": 74, "difficulty": "medium",
         "advantages": ["Tight Azure integration", "Robust T-SQL & SSMS tooling", "Enterprise support"],
         "disadvantages": ["Licensing cost for Enterprise features"],
         "fit": "Enterprise Windows & Azure cloud environments.",
         "not_fit": "Higher licensing costs.",
         "recommended": False},

        {"category": "database", "name": "CockroachDB", "score": 83, "difficulty": "hard",
         "advantages": ["Distributed SQL resilience", "PostgreSQL wire compatible", "Multi-region horizontal scale"],
         "disadvantages": ["Higher latency for simple single-node operations"],
         "fit": "Global scale zero-downtime distributed transactional data.",
         "not_fit": "Complex operational model for small MVPs.",
         "recommended": False},

        # 4. AI/ML
        {"category": "ai_ml", "name": "Scikit-learn", "score": 90, "difficulty": "easy",
         "advantages": ["Simple intuitive Python API", "Fast training algorithms", "Ideal for recommendation systems"],
         "disadvantages": ["Not designed for deep neural networks", "CPU-bound training"],
         "fit": "Collaborative filtering and matrix factorization for e-commerce recommendations in record time.",
         "not_fit": "Not suitable for unstructured image/vision or deep learning models.",
         "recommended": True},

        {"category": "ai_ml", "name": "OpenAI", "score": 88, "difficulty": "easy",
         "advantages": ["State of the art GPT models", "Simple API endpoint integration", "Zero ML infrastructure hosting"],
         "disadvantages": ["Per-token API cost", "External API latency"],
         "fit": "Instant integration of product summaries, chatbots, and semantic search via API.",
         "not_fit": "Requires outbound internet requests and per-token pricing.",
         "recommended": False},

        {"category": "ai_ml", "name": "Google Gemini", "score": 87, "difficulty": "easy",
         "advantages": ["Multimodal AI vision & text capabilities", "High speed flash models", "Generous free quotas"],
         "disadvantages": ["API rate limits under heavy traffic"],
         "fit": "Multimodal product image tag extraction and recommendation generation.",
         "not_fit": "Third-party cloud dependency.",
         "recommended": False},

        {"category": "ai_ml", "name": "PyTorch", "score": 80, "difficulty": "hard",
         "advantages": ["Dynamic computation graphs", "Dominant research adoption", "Strong community"],
         "disadvantages": ["Higher memory usage", "Requires ML expertise"],
         "fit": "Deep neural collaborative filtering for recommendation engines.",
         "not_fit": "Steeper learning curve for web developers.",
         "recommended": False},

        {"category": "ai_ml", "name": "TensorFlow", "score": 75, "difficulty": "hard",
         "advantages": ["Production-ready ML framework", "TensorFlow Serving for deployment", "Keras high-level API"],
         "disadvantages": ["Complex API surface", "Steep learning curve"],
         "fit": "Enterprise deep learning models for high-scale recommendations.",
         "not_fit": "High complexity for a 30-day MVP project.",
         "recommended": False},

        {"category": "ai_ml", "name": "Hugging Face", "score": 82, "difficulty": "medium",
         "advantages": ["Pre-trained Transformer models", "Pipelines for NLP and embeddings", "Active open-source hub"],
         "disadvantages": ["Large model sizes", "Higher inference latency"],
         "fit": "Semantic product search and AI text generation using pre-trained transformers.",
         "not_fit": "Higher memory requirements for hosting model weights.",
         "recommended": False},

        {"category": "ai_ml", "name": "Keras", "score": 81, "difficulty": "medium",
         "advantages": ["High-level neural network API", "Runs on top of TensorFlow/JAX/PyTorch", "User-friendly prototyping"],
         "disadvantages": ["Abstracts low-level tensor optimizations"],
         "fit": "Rapid deep learning model prototyping.",
         "not_fit": "Requires underlying backend tensor engine.",
         "recommended": False},

        {"category": "ai_ml", "name": "XGBoost", "score": 86, "difficulty": "medium",
         "advantages": ["Gradient boosted decision trees", "Superior performance on tabular data", "Fast CPU/GPU training"],
         "disadvantages": ["Hyperparameter tuning complexity"],
         "fit": "Tabular product ranking and customer churn prediction.",
         "not_fit": "Not designed for unstructured text or vision.",
         "recommended": False},

        {"category": "ai_ml", "name": "LangChain", "score": 84, "difficulty": "medium",
         "advantages": ["LLM orchestration framework", "RAG vector database connectors", "Prompt chaining"],
         "disadvantages": ["Rapidly changing API surface"],
         "fit": "Building RAG AI search over product catalogs.",
         "not_fit": "Overhead for simple single-prompt completions.",
         "recommended": False},

        # 5. Deployment
        {"category": "deployment", "name": "Render", "score": 90, "difficulty": "easy",
         "advantages": ["Unified PaaS for web services & PostgreSQL", "Automatic Git deploy pipeline", "SSL and custom domains"],
         "disadvantages": ["Free tier instances sleep after inactivity"],
         "fit": "Deploys both Python FastAPI backend and PostgreSQL database effortlessly.",
         "not_fit": "Cold starts on free tier instances.",
         "recommended": True},

        {"category": "deployment", "name": "Vercel", "score": 84, "difficulty": "easy",
         "advantages": ["Zero-config frontend deployments", "Edge network performance", "Automatic previews"],
         "disadvantages": ["Serverless backend execution limits", "Higher cost for bandwidth"],
         "fit": "Instant global CDN deployment for React/Vue frontends.",
         "not_fit": "Requires separate backend server hosting for Python APIs.",
         "recommended": False},

        {"category": "deployment", "name": "AWS", "score": 76, "difficulty": "hard",
         "advantages": ["Infinite cloud scalability", "Full suite of cloud services (EC2, RDS, S3)", "Industry standard"],
         "disadvantages": ["Complex IAM and pricing", "Steep DevOps learning curve"],
         "fit": "Enterprise scalability and complete cloud infrastructure control.",
         "not_fit": "DevOps overhead can slow down small team velocity.",
         "recommended": False},

        {"category": "deployment", "name": "DigitalOcean", "score": 82, "difficulty": "medium",
         "advantages": ["Predictable pricing", "App Platform for PaaS deployment", "Managed databases"],
         "disadvantages": ["Fewer advanced managed services than AWS"],
         "fit": "Simple VPS Droplets and PaaS hosting with straightforward costs.",
         "not_fit": "Less automated scaling than specialized serverless platforms.",
         "recommended": False},

        {"category": "deployment", "name": "Azure", "score": 78, "difficulty": "hard",
         "advantages": ["Microsoft Enterprise ecosystem", "Azure App Services", "Strong Active Directory integration"],
         "disadvantages": ["Complex portal configuration"],
         "fit": "Enterprise applications requiring Microsoft cloud compliance.",
         "not_fit": "DevOps setup overhead for small teams.",
         "recommended": False},

        {"category": "deployment", "name": "Google Cloud", "score": 80, "difficulty": "hard",
         "advantages": ["Google Cloud Run container execution", "Superior BigQuery data analytics", "Global network backbone"],
         "disadvantages": ["Complex IAM roles"],
         "fit": "Serverless container execution via Cloud Run.",
         "not_fit": "Steeper cloud IAM learning curve.",
         "recommended": False},

        {"category": "deployment", "name": "Netlify", "score": 85, "difficulty": "easy",
         "advantages": ["Git-based Jamstack deployment", "Forms and edge functions", "Instant deploy previews"],
         "disadvantages": ["Serverless function execution limits"],
         "fit": "Static site generation and Jamstack frontends.",
         "not_fit": "Long-running backend APIs require separate hosting.",
         "recommended": False},

        {"category": "deployment", "name": "Cloudflare", "score": 83, "difficulty": "medium",
         "advantages": ["Global Edge Workers", "DDoS mitigation & CDN", "R2 object storage without egress fees"],
         "disadvantages": ["Worker V8 isolation constraints"],
         "fit": "Ultra-low latency edge API execution.",
         "not_fit": "Requires V8 worker script architecture.",
         "recommended": False},

        {"category": "deployment", "name": "Railway", "score": 88, "difficulty": "easy",
         "advantages": ["Developer-centric cloud PaaS", "Instant database provisioning", "Git push builds"],
         "disadvantages": ["Usage-based billing requires monitoring"],
         "fit": "Rapid full-stack deployment with instant PostgreSQL/Redis add-ons.",
         "not_fit": "Fewer enterprise compliance certifications.",
         "recommended": False},

        # 6. Authentication
        {"category": "authentication", "name": "JWT", "score": 92, "difficulty": "medium",
         "advantages": ["Stateless authorization", "Works across distributed microservices", "No DB session lookups"],
         "disadvantages": ["Token revocation requires blacklist mechanism"],
         "fit": "Standard stateless auth payload ideal for React SPA communicating with REST API.",
         "not_fit": "Requires secure client-side storage handling.",
         "recommended": True},

        {"category": "authentication", "name": "OAuth 2.0", "score": 82, "difficulty": "medium",
         "advantages": ["Delegated authorization", "Supports social logins (Google, GitHub)", "User trust"],
         "disadvantages": ["Provider registration required", "Redirect flow handling"],
         "fit": "Enables frictionless social login for end users.",
         "not_fit": "Adds external provider dependencies.",
         "recommended": False},

        {"category": "authentication", "name": "OpenID Connect", "score": 80, "difficulty": "hard",
         "advantages": ["Identity layer on top of OAuth 2.0", "Standardized ID tokens", "Enterprise SSO integration"],
         "disadvantages": ["Complex specification", "Higher setup overhead"],
         "fit": "Standardized identity protocol for multi-app enterprise ecosystems.",
         "not_fit": "Overkill for single-tenant web apps.",
         "recommended": False},

        {"category": "authentication", "name": "Session-based Authentication", "score": 75, "difficulty": "easy",
         "advantages": ["Server-controlled session state", "Instant session invalidation", "HttpOnly cookie security"],
         "disadvantages": ["Server memory/Redis lookup per request", "Stateful scaling requirements"],
         "fit": "Traditional server-rendered cookie session security.",
         "not_fit": "Less seamless for cross-domain mobile/API clients.",
         "recommended": False},

        {"category": "authentication", "name": "Auth0", "score": 86, "difficulty": "medium",
         "advantages": ["Turnkey identity management SaaS", "Pre-built login UIs", "Enterprise SAML & OAuth support"],
         "disadvantages": ["Tiered pricing per active user"],
         "fit": "Outsourced secure authentication without maintaining custom auth backend.",
         "not_fit": "Third-party vendor dependency and MAU cost.",
         "recommended": False},

        {"category": "authentication", "name": "Firebase Auth", "score": 85, "difficulty": "easy",
         "advantages": ["Generous free tier", "Seamless phone, social, and email auth", "SDK integration"],
         "disadvantages": ["Google Firebase lock-in"],
         "fit": "Quick mobile and web authentication setup.",
         "not_fit": "Requires Firebase project setup.",
         "recommended": False},

        {"category": "authentication", "name": "Clerk", "score": 87, "difficulty": "easy",
         "advantages": ["Modern developer-friendly React components", "Built-in user management UI", "Multi-session support"],
         "disadvantages": ["Monthly active user pricing"],
         "fit": "Stunning pre-built user profile and sign-in components for React/Next.js.",
         "not_fit": "Commercial subscription for high user counts.",
         "recommended": False},

        {"category": "authentication", "name": "Supabase Auth", "score": 86, "difficulty": "easy",
         "advantages": ["Row Level Security (RLS) integration", "JWT token generation", "Open-source backend"],
         "disadvantages": ["Tightly tied to Supabase PostgreSQL"],
         "fit": "Instant authentication linked directly to database policies.",
         "not_fit": "Requires Supabase stack.",
         "recommended": False},

        # 7. API / Communication
        {"category": "api_communication", "name": "REST API", "score": 94, "difficulty": "easy",
         "advantages": ["Universal HTTP standard", "Extremely wide client compatibility", "Simple caching mechanisms"],
         "disadvantages": ["Over-fetching / under-fetching data"],
         "fit": "Standard RESTful endpoints for straightforward CRUD operations and client communication.",
         "not_fit": "Can suffer from multiple round-trips for nested relations.",
         "recommended": True},

        {"category": "api_communication", "name": "GraphQL", "score": 82, "difficulty": "medium",
         "advantages": ["Single endpoint query syntax", "Exact payload field selection", "Strong schema types"],
         "disadvantages": ["Complex caching on client/server", "N+1 query complexity"],
         "fit": "Flexible queries for complex catalog structures.",
         "not_fit": "Higher implementation complexity for small teams.",
         "recommended": False},

        {"category": "api_communication", "name": "WebSockets", "score": 78, "difficulty": "medium",
         "advantages": ["Full-duplex real-time communication", "Low latency push updates"],
         "disadvantages": ["Requires persistent connection management", "Scalability challenges"],
         "fit": "Real-time order status updates and live notification streaming.",
         "not_fit": "Not necessary if polling or standard HTTP responses suffice.",
         "recommended": False},

        {"category": "api_communication", "name": "gRPC", "score": 70, "difficulty": "hard",
         "advantages": ["High performance Protobuf serialization", "HTTP/2 streaming", "Strict contract generation"],
         "disadvantages": ["Not natively browser-compatible without proxy", "Steep learning curve"],
         "fit": "Low latency inter-service microservice communication.",
         "not_fit": "Overkill for standard web browser SPA clients.",
         "recommended": False},

        {"category": "api_communication", "name": "Webhooks", "score": 85, "difficulty": "easy",
         "advantages": ["Event-driven server-to-server push notifications", "Lightweight payload delivery"],
         "disadvantages": ["Requires payload signature verification & retry handling"],
         "fit": "Handling asynchronous third-party payment provider notifications (Stripe/PayPal).",
         "not_fit": "Not a primary client API protocol.",
         "recommended": False},

        {"category": "api_communication", "name": "Server-Sent Events", "score": 83, "difficulty": "medium",
         "advantages": ["Simple unidirectional HTTP stream", "Native browser EventSource API support", "Automatic reconnect"],
         "disadvantages": ["Unidirectional (server to client only)"],
         "fit": "Streaming live AI response tokens or progress notifications.",
         "not_fit": "Two-way client interaction requires standard POST calls.",
         "recommended": False},

        {"category": "api_communication", "name": "tRPC", "score": 84, "difficulty": "medium",
         "advantages": ["End-to-end type safety without code generation", "Seamless TypeScript autocomplete"],
         "disadvantages": ["Requires full TypeScript stack (Node + React)"],
         "fit": "Full-stack TypeScript applications needing type-safe procedure calls.",
         "not_fit": "Not compatible with non-TypeScript backends like Python FastAPI.",
         "recommended": False},

        # 8. DevOps / CI/CD
        {"category": "devops", "name": "Docker", "score": 92, "difficulty": "medium",
         "advantages": ["Consistent containerized environments", "Reproducible builds across dev/prod", "Wide cloud support"],
         "disadvantages": ["Container image size management required"],
         "fit": "Packages backend and dependencies cleanly for immediate cloud deployment.",
         "not_fit": "Requires Docker learning curve for local dev.",
         "recommended": True},

        {"category": "devops", "name": "GitHub Actions", "score": 90, "difficulty": "easy",
         "advantages": ["Native integration with GitHub repos", "Free tier build minutes", "Rich action marketplace"],
         "disadvantages": ["Vendor lock-in to GitHub ecosystem"],
         "fit": "Automated build, test, and deployment workflows triggered on Git push.",
         "not_fit": "Requires GitHub host repository.",
         "recommended": False},

        {"category": "devops", "name": "Kubernetes", "score": 68, "difficulty": "hard",
         "advantages": ["Automated container orchestration", "Self-healing and auto-scaling"],
         "disadvantages": ["Extremely high operational complexity", "Resource intensive"],
         "fit": "Massive multi-cluster container orchestration.",
         "not_fit": "Excessive complexity for early stage MVP.",
         "recommended": False},

        {"category": "devops", "name": "GitLab CI/CD", "score": 80, "difficulty": "medium",
         "advantages": ["Built-in pipeline configuration", "Integrated container registry"],
         "disadvantages": ["Requires GitLab hosting"],
         "fit": "Integrated CI/CD for teams using GitLab.",
         "not_fit": "Not applicable if repository is hosted elsewhere.",
         "recommended": False},

        {"category": "devops", "name": "CircleCI", "score": 81, "difficulty": "medium",
         "advantages": ["Fast parallel test execution", "Orbs reusable pipeline modules"],
         "disadvantages": ["Separate SaaS platform setup"],
         "fit": "High-velocity automated testing pipelines.",
         "not_fit": "Requires separate account configuration.",
         "recommended": False},

        {"category": "devops", "name": "Jenkins", "score": 71, "difficulty": "hard",
         "advantages": ["Open-source self-hosted automation server", "Extensive plugin repository"],
         "disadvantages": ["High maintenance and security patching overhead"],
         "fit": "Custom self-hosted CI/CD infrastructure for air-gapped enterprise.",
         "not_fit": "Maintenance overhead for small agile teams.",
         "recommended": False},

        {"category": "devops", "name": "Terraform", "score": 85, "difficulty": "hard",
         "advantages": ["Declarative Infrastructure as Code (IaC)", "Multi-cloud provider support"],
         "disadvantages": ["State file management complexity"],
         "fit": "Automated cloud resource provisioning.",
         "not_fit": "Overhead for simple PaaS hosting.",
         "recommended": False},

        {"category": "devops", "name": "Ansible", "score": 79, "difficulty": "medium",
         "advantages": ["Agentless YAML configuration management", "Simple SSH execution"],
         "disadvantages": ["Procedural execution ordering"],
         "fit": "Server configuration and software installation automation.",
         "not_fit": "Less container-native than Docker/Kubernetes.",
         "recommended": False},

        # 9. Caching / Messaging
        {"category": "caching_messaging", "name": "Redis", "score": 91, "difficulty": "easy",
         "advantages": ["Ultra-fast in-memory store", "Supports cache, pub/sub, queues", "Simple key-value operations"],
         "disadvantages": ["In-memory data limits"],
         "fit": "In-memory session storage and fast query result caching.",
         "not_fit": "Not designed for primary persistent storage.",
         "recommended": True},

        {"category": "caching_messaging", "name": "RabbitMQ", "score": 80, "difficulty": "medium",
         "advantages": ["Flexible AMQP routing models", "Reliable message queuing and retries"],
         "disadvantages": ["Requires dedicated message broker management"],
         "fit": "Asynchronous background task processing like order emails.",
         "not_fit": "Additional broker infrastructure to maintain.",
         "recommended": False},

        {"category": "caching_messaging", "name": "Apache Kafka", "score": 72, "difficulty": "hard",
         "advantages": ["High throughput distributed event log", "Replayability of stream events"],
         "disadvantages": ["High cluster setup and maintenance overhead"],
         "fit": "Large-scale event streaming and telemetry data pipeline.",
         "not_fit": "Too complex for standard web app caching.",
         "recommended": False},

        {"category": "caching_messaging", "name": "Celery", "score": 85, "difficulty": "medium",
         "advantages": ["Native Python distributed task queue", "Seamless integration with FastAPI/Django"],
         "disadvantages": ["Requires Redis or RabbitMQ as broker"],
         "fit": "Background job queue execution for Python backends.",
         "not_fit": "Python-specific background task solution.",
         "recommended": False},

        {"category": "caching_messaging", "name": "Memcached", "score": 82, "difficulty": "easy",
         "advantages": ["Simple multithreaded key-value memory cache", "High throughput LRU eviction"],
         "disadvantages": ["No complex data structures or persistence"],
         "fit": "Pure high-speed database query result caching.",
         "not_fit": "Lacks pub/sub or data structures offered by Redis.",
         "recommended": False},

        {"category": "caching_messaging", "name": "Amazon SQS", "score": 81, "difficulty": "easy",
         "advantages": ["Fully managed AWS message queue", "Zero infrastructure management", "Infinite elasticity"],
         "disadvantages": ["AWS cloud lock-in"],
         "fit": "Decoupling cloud worker services with managed queues.",
         "not_fit": "AWS specific API.",
         "recommended": False},

        {"category": "caching_messaging", "name": "NATS", "score": 79, "difficulty": "medium",
         "advantages": ["Ultra-lightweight high performance messaging system", "Minimal memory footprint"],
         "disadvantages": ["Smaller enterprise ecosystem than Kafka"],
         "fit": "Low latency microservice event pub/sub.",
         "not_fit": "Niche adoption.",
         "recommended": False},

        {"category": "caching_messaging", "name": "BullMQ", "score": 84, "difficulty": "easy",
         "advantages": ["Fast Redis-based task queue for Node.js/TypeScript", "Job retries, delays, and progress"],
         "disadvantages": ["Node.js ecosystem specific"],
         "fit": "Node.js backend asynchronous job processing.",
         "not_fit": "Not usable directly in Python.",
         "recommended": False},

        # 10. Testing
        {"category": "testing", "name": "Pytest", "score": 93, "difficulty": "easy",
         "advantages": ["Concise test syntax", "Rich fixture system", "Extensive plugin ecosystem"],
         "disadvantages": ["Python specific"],
         "fit": "Comprehensive unit and integration testing for Python backend services.",
         "not_fit": "Does not test frontend UI components directly.",
         "recommended": True},

        {"category": "testing", "name": "Jest", "score": 88, "difficulty": "easy",
         "advantages": ["Zero-config JavaScript test runner", "Built-in snapshot testing and mocking"],
         "disadvantages": ["Slower execution on large codebases"],
         "fit": "Unit testing React components and frontend utility functions.",
         "not_fit": "Slower than newer runners like Vitest.",
         "recommended": False},

        {"category": "testing", "name": "Vitest", "score": 86, "difficulty": "easy",
         "advantages": ["Blazing fast Vite-native test runner", "Jest-compatible API"],
         "disadvantages": ["Tightly coupled to Vite tooling"],
         "fit": "Fast modern frontend unit and component testing.",
         "not_fit": "Requires Vite setup.",
         "recommended": False},

        {"category": "testing", "name": "Playwright", "score": 84, "difficulty": "medium",
         "advantages": ["Reliable end-to-end browser automation", "Cross-browser testing support (Chromium, Firefox, WebKit)"],
         "disadvantages": ["Longer test suite execution time"],
         "fit": "Automated E2E validation of critical checkout user flows.",
         "not_fit": "Heavyweight for unit level logic testing.",
         "recommended": False},

        {"category": "testing", "name": "Cypress", "score": 83, "difficulty": "medium",
         "advantages": ["Interactive time-travel E2E test runner", "Great developer experience"],
         "disadvantages": ["Runs inside single browser process"],
         "fit": "Visual E2E testing of web application UI components.",
         "not_fit": "Multi-tab browser testing constraints.",
         "recommended": False},

        {"category": "testing", "name": "Selenium", "score": 75, "difficulty": "hard",
         "advantages": ["Legacy industry standard E2E browser automation", "Multi-language bindings (Java, Python, C#)"],
         "disadvantages": ["Flaky test execution & slow setup"],
         "fit": "Legacy enterprise browser automation test suites.",
         "not_fit": "Flakier than modern runners like Playwright.",
         "recommended": False},

        {"category": "testing", "name": "Mocha", "score": 78, "difficulty": "easy",
         "advantages": ["Flexible JS test framework", "Pairable with Chai & Sinon"],
         "disadvantages": ["Requires configuring separate assertion libraries"],
         "fit": "Simple JavaScript unit testing.",
         "not_fit": "Requires configuring external matchers.",
         "recommended": False},

        {"category": "testing", "name": "JUnit", "score": 77, "difficulty": "easy",
         "advantages": ["Standard Java unit testing framework", "Deep IDE and build tool integration"],
         "disadvantages": ["Java ecosystem specific"],
         "fit": "Java Spring Boot backend unit test suites.",
         "not_fit": "Java specific.",
         "recommended": False},
    ]

    for opt in tech_options:
        tech = TechnologyOption(
            project_id=project.id,
            category=opt["category"],
            name=opt["name"],
            suitability_score=opt["score"],
            advantages=json.dumps(opt["advantages"]),
            disadvantages=json.dumps(opt["disadvantages"]),
            difficulty=opt["difficulty"],
            fit_reason=opt["fit"],
            not_fit_reason=opt["not_fit"],
            is_recommended=opt.get("recommended", False),
        )
        db.add(tech)

    db.commit()
    return project
