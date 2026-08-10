"""ProjectForge AI — Technology Advisor Agent.

Agent 2 of 6: Analyzes requirements, uses Tavily for current web research,
and generates 4 technology alternatives per category with unbiased
suitability scoring.
"""
import logging
from backend.app.llm.factory import LLMFactory
from backend.app.schemas.agent import (
    ProjectRequirements, TechnologyRecommendations, TechCategory, TechAlternative
)
from backend.app.tools.tavily_search import tavily_tool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Technology Advisor Agent for ProjectForge AI.

Your job is to analyze project requirements and recommend EXACTLY 4 technology
alternatives for each of the 10 technology categories.

CRITICAL RULES:
1. You must NOT be biased toward any single technology.
2. Recommendations must change based on actual project requirements.
3. Every alternative must have an honest suitability score (0-100).
4. Scores must reflect the ACTUAL fit for THIS specific project.
5. You must provide real advantages AND disadvantages for each option.
6. The recommended option should genuinely be the best fit, not a default choice.
7. You MUST output EXACTLY 4 alternatives per category.
8. DO NOT confuse hosting platforms (Vercel, Render, AWS) with frontend/backend frameworks. Keep categories strictly separate.

SCORING FACTORS (weight each based on the project):
- Project requirements alignment
- Team size suitability
- Deadline feasibility (can the team deliver with this tech in time?)
- Budget considerations
- Team skill level (beginner teams need simpler tech)
- Complexity management
- Scalability needs
- Maintainability
- Ecosystem and community support
- Deployment requirements

CATEGORIES AND EXPECTED OPTIONS:
- frontend: React, Next.js, Vue.js, Angular, Svelte, SolidJS, Nuxt.js, Remix, Astro
- backend: FastAPI, Node.js + Express, Django, Flask, NestJS, Spring Boot, ASP.NET Core, Laravel, Ruby on Rails
- database: PostgreSQL, MySQL, MongoDB, SQLite, MariaDB, Oracle Database, Microsoft SQL Server, CockroachDB
- ai_ml: TensorFlow, PyTorch, scikit-learn, OpenAI, Google Gemini, Hugging Face, Keras, XGBoost, LangChain
- authentication: JWT, OAuth 2.0, OpenID Connect, Auth0, Firebase Auth, Session-based Auth, Clerk, Supabase Auth
- deployment: Vercel, AWS, Azure, Google Cloud, Render, DigitalOcean, Netlify, Cloudflare, Railway
- api_communication: REST API, GraphQL, WebSockets, gRPC, Webhooks, Server-Sent Events, tRPC
- devops: GitHub Actions, Docker, Kubernetes, Jenkins, GitLab CI/CD, CircleCI, Terraform, Ansible
- caching_messaging: Redis, RabbitMQ, Apache Kafka, Celery, Memcached, Amazon SQS, NATS, BullMQ
- testing: Pytest, Jest, Vitest, Cypress, Playwright, Selenium, Mocha, JUnit

REQUIRED CATEGORIES:
- frontend, backend, database

OPTIONAL CATEGORIES:
- ai_ml, authentication, deployment, api_communication, devops, caching_messaging, testing

For each alternative provide:
- name: Technology name
- suitability_score: 0-100 based on actual project fit
- advantages: List of advantages FOR THIS PROJECT
- disadvantages: List of disadvantages FOR THIS PROJECT
- difficulty: easy/medium/hard
- fit_reason: Why this technology fits this project
- not_fit_reason: Why it might not be the best choice
- is_recommended: true for the single top recommendation in each category

Mark exactly ONE alternative as is_recommended=true per category.
Provide EXACTLY 4 alternatives per category.
"""


def run_technology_advisor(requirements: ProjectRequirements) -> TechnologyRecommendations:
    """Run the Technology Advisor Agent.

    Uses Tavily for current web research when available,
    then generates technology recommendations via LLM with fallback catalog safety.

    Args:
        requirements: Structured project requirements.

    Returns:
        TechnologyRecommendations with 4 alternatives per category.
    """
    from backend.app.schemas.agent import ensure_project_requirements
    requirements = ensure_project_requirements(requirements)

    logger.info("Technology Advisor Agent: Starting analysis")

    web_research = ""
    try:
        web_research = _perform_web_research(requirements)
    except Exception as e:
        logger.warning(f"Technology Advisor: Web research skipped/failed: {e}")

    try:
        llm = LLMFactory.get_provider_for_agent("technology_advisor")
        requirements_text = _format_requirements(requirements)

        prompt = f"""Analyze these project requirements and recommend technology alternatives.

PROJECT REQUIREMENTS:
{requirements_text}

{web_research}

For each relevant technology category, provide EXACTLY 4 alternatives with honest
suitability scores based on the ACTUAL project requirements above.

Remember:
- A small project with beginners should favor simpler technologies
- A large enterprise project should favor robust, scalable technologies
- Consider the team size, deadline, and budget constraints
- If the project doesn't need AI/ML, skip the ai_ml category entirely
- Be honest about disadvantages — every technology has them

Generate comprehensive technology recommendations now.
"""

        result = llm.generate_structured(
            prompt=prompt,
            output_schema=TechnologyRecommendations,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.5,
        )

        result.web_research_used = web_research != ""
        if not tavily_tool.api_key:
            result.web_research_note = (
                "Live web research was not available (TAVILY_API_KEY not set). "
                "Recommendations are based on the AI's existing knowledge."
            )

        logger.info(f"Technology Advisor Agent: Generated {len(result.categories)} categories via AI")
        return result

    except Exception as e:
        logger.warning(
            f"Technology Advisor Agent: AI provider unavailable or failed ({e}). "
            "Using standard 10-category technology catalog fallback."
        )
        return get_fallback_technology_recommendations(requirements)


def get_fallback_technology_recommendations(requirements: ProjectRequirements) -> TechnologyRecommendations:
    """Provide a reliable 10-category technology catalog fallback when all AI providers fail."""
    categories_data = [
        {
            "category": "frontend",
            "recommendation": "React",
            "recommendation_reason": "High performance, component reusability, and rich ecosystem suitable for modern web applications.",
            "alternatives": [
                {
                    "name": "React",
                    "suitability_score": 92,
                    "advantages": ["Large ecosystem and community", "Rich component libraries", "High performance virtual DOM"],
                    "disadvantages": ["Requires state management decisions"],
                    "difficulty": "medium",
                    "fit_reason": "Great fit for dynamic interactive applications",
                    "not_fit_reason": "Slight learning curve for state management",
                    "is_recommended": True
                },
                {
                    "name": "Next.js",
                    "suitability_score": 89,
                    "advantages": ["Full-stack React framework", "Built-in SSR & SSG", "API routes"],
                    "disadvantages": ["Server architecture complexity"],
                    "difficulty": "medium",
                    "fit_reason": "Ideal if SEO and server rendering are required",
                    "not_fit_reason": "More opinionated than plain React",
                    "is_recommended": False
                },
                {
                    "name": "Vue.js",
                    "suitability_score": 85,
                    "advantages": ["Gentle learning curve", "Flexible template system", "Great documentation"],
                    "disadvantages": ["Smaller ecosystem than React"],
                    "difficulty": "easy",
                    "fit_reason": "Easy for fast team onboarding",
                    "not_fit_reason": "Fewer ready-made enterprise UI kits",
                    "is_recommended": False
                },
                {
                    "name": "Angular",
                    "suitability_score": 75,
                    "advantages": ["Batteries-included framework", "Strong TypeScript integration"],
                    "disadvantages": ["Steep learning curve", "Heavy boilerplate"],
                    "difficulty": "hard",
                    "fit_reason": "Enterprise-grade structure",
                    "not_fit_reason": "Overkill for simple projects",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "backend",
            "recommendation": "FastAPI",
            "recommendation_reason": "High performance, automatic OpenAPI documentation, and async support with Python productivity.",
            "alternatives": [
                {
                    "name": "FastAPI",
                    "suitability_score": 94,
                    "advantages": ["High performance Python framework", "Auto-generated OpenAPI docs", "Native Pydantic data validation"],
                    "disadvantages": ["Younger ecosystem than Django"],
                    "difficulty": "medium",
                    "fit_reason": "Fast development velocity and automatic REST documentation",
                    "not_fit_reason": "Requires choosing ORM separately",
                    "is_recommended": True
                },
                {
                    "name": "Node.js + Express",
                    "suitability_score": 88,
                    "advantages": ["Single language (JS/TS) for frontend and backend", "Massive npm ecosystem"],
                    "disadvantages": ["Unopinionated structure requires architecture discipline"],
                    "difficulty": "easy",
                    "fit_reason": "High throughput async I/O",
                    "not_fit_reason": "Callback/async code structure complexity",
                    "is_recommended": False
                },
                {
                    "name": "Django",
                    "suitability_score": 86,
                    "advantages": ["Built-in admin panel and ORM", "Batteries-included security"],
                    "disadvantages": ["Monolithic structure can feel heavy"],
                    "difficulty": "medium",
                    "fit_reason": "Rapid MVP development with built-in admin",
                    "not_fit_reason": "Slower than FastAPI for pure microservices",
                    "is_recommended": False
                },
                {
                    "name": "Flask",
                    "suitability_score": 78,
                    "advantages": ["Minimal lightweight framework", "Maximum flexibility"],
                    "disadvantages": ["Lacks async performance of FastAPI"],
                    "difficulty": "easy",
                    "fit_reason": "Minimalist API prototype",
                    "not_fit_reason": "Requires adding extensions manually",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "database",
            "recommendation": "PostgreSQL",
            "recommendation_reason": "Reliable relational database with JSON support, robust ACID compliance, and high scalability.",
            "alternatives": [
                {
                    "name": "PostgreSQL",
                    "suitability_score": 95,
                    "advantages": ["Rock-solid ACID compliance", "Rich JSONB support", "Extensive extension ecosystem"],
                    "disadvantages": ["Requires memory tuning for high scale"],
                    "difficulty": "medium",
                    "fit_reason": "Best all-around relational database for modern applications",
                    "not_fit_reason": "Complex setup for distributed multi-region write clusters",
                    "is_recommended": True
                },
                {
                    "name": "MySQL",
                    "suitability_score": 85,
                    "advantages": ["Widely supported and battle-tested", "Easy setup"],
                    "disadvantages": ["Fewer advanced JSON/indexing options than Postgres"],
                    "difficulty": "easy",
                    "fit_reason": "Standard web application database",
                    "not_fit_reason": "Less flexible JSON queries",
                    "is_recommended": False
                },
                {
                    "name": "MongoDB",
                    "suitability_score": 78,
                    "advantages": ["Flexible schema document model", "Easy horizontal scaling"],
                    "disadvantages": ["No native relational foreign key integrity"],
                    "difficulty": "easy",
                    "fit_reason": "Unstructured data or rapid schema evolution",
                    "not_fit_reason": "Complex relational transactions",
                    "is_recommended": False
                },
                {
                    "name": "SQLite",
                    "suitability_score": 70,
                    "advantages": ["Zero-configuration embedded file database", "Instant local testing"],
                    "disadvantages": ["Single-writer concurrency lock limit"],
                    "difficulty": "easy",
                    "fit_reason": "Local dev or light workload",
                    "not_fit_reason": "Not intended for multi-server production writes",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "ai_ml",
            "recommendation": "Google Gemini",
            "recommendation_reason": "Fast multi-modal generative AI capabilities with cheap/free tier options and structured JSON outputs.",
            "alternatives": [
                {
                    "name": "Google Gemini",
                    "suitability_score": 90,
                    "advantages": ["Fast multimodal processing", "Generous free tier", "Strong structured output support"],
                    "disadvantages": ["API rate limits on free tier"],
                    "difficulty": "easy",
                    "fit_reason": "Excellent for smart agent automation and structured extraction",
                    "not_fit_reason": "Quota limits require fallback key management",
                    "is_recommended": True
                },
                {
                    "name": "OpenAI",
                    "suitability_score": 88,
                    "advantages": ["Industry standard LLMs (GPT-4o)", "Wide SDK ecosystem"],
                    "disadvantages": ["Higher pay-per-token costs"],
                    "difficulty": "easy",
                    "fit_reason": "High reasoning quality",
                    "not_fit_reason": "Cost considerations",
                    "is_recommended": False
                },
                {
                    "name": "PyTorch",
                    "suitability_score": 80,
                    "advantages": ["Full custom model training and fine-tuning control"],
                    "disadvantages": ["Requires GPU infrastructure and ML engineering expertise"],
                    "difficulty": "hard",
                    "fit_reason": "Custom deep learning models",
                    "not_fit_reason": "Requires high development effort",
                    "is_recommended": False
                },
                {
                    "name": "Scikit-learn",
                    "suitability_score": 75,
                    "advantages": ["Lightweight classical ML library in Python"],
                    "disadvantages": ["Not designed for generative LLM tasks"],
                    "difficulty": "easy",
                    "fit_reason": "Tabular data prediction/classification",
                    "not_fit_reason": "Does not provide natural language generation",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "authentication",
            "recommendation": "JWT",
            "recommendation_reason": "Stateless, standard authorization token format easily validated across backend services.",
            "alternatives": [
                {
                    "name": "JWT",
                    "suitability_score": 92,
                    "advantages": ["Stateless authentication", "Standardized payload format", "High performance verification"],
                    "disadvantages": ["Token revocation requires blacklist or short expiry"],
                    "difficulty": "medium",
                    "fit_reason": "Seamless integration with REST APIs and single page apps",
                    "not_fit_reason": "Requires careful secret management",
                    "is_recommended": True
                },
                {
                    "name": "OAuth 2.0",
                    "suitability_score": 88,
                    "advantages": ["Allows third-party social logins (Google, GitHub)", "Industry security standard"],
                    "disadvantages": ["More complex flow configuration"],
                    "difficulty": "medium",
                    "fit_reason": "Social sign-in integration",
                    "not_fit_reason": "Overkill for simple username/password auth",
                    "is_recommended": False
                },
                {
                    "name": "Auth0",
                    "suitability_score": 82,
                    "advantages": ["Managed user auth service", "Out-of-the-box MFA and security features"],
                    "disadvantages": ["Third-party vendor lock-in and pricing tiers"],
                    "difficulty": "easy",
                    "fit_reason": "Fast time-to-market without building custom auth",
                    "not_fit_reason": "Cost at scale",
                    "is_recommended": False
                },
                {
                    "name": "Firebase Auth",
                    "suitability_score": 80,
                    "advantages": ["Easy integration with Google ecosystem"],
                    "disadvantages": ["Tightly coupled to GCP/Firebase"],
                    "difficulty": "easy",
                    "fit_reason": "Quick prototype with Firebase",
                    "not_fit_reason": "Vendor lock-in",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "deployment",
            "recommendation": "Docker",
            "recommendation_reason": "Containerized application packaging ensuring consistent behavior across local, staging, and production environments.",
            "alternatives": [
                {
                    "name": "Docker",
                    "suitability_score": 95,
                    "advantages": ["Consistent environment across dev and prod", "Portable container packaging"],
                    "disadvantages": ["Requires Docker build knowledge"],
                    "difficulty": "medium",
                    "fit_reason": "Containerized production deployment anywhere",
                    "not_fit_reason": "Slight overhead for very small static sites",
                    "is_recommended": True
                },
                {
                    "name": "Vercel",
                    "suitability_score": 88,
                    "advantages": ["Instant zero-config frontend deployment", "Global CDN"],
                    "disadvantages": ["Limited long-running backend process support"],
                    "difficulty": "easy",
                    "fit_reason": "Best for Next.js / React frontend hosting",
                    "not_fit_reason": "Not for heavy backend worker queues",
                    "is_recommended": False
                },
                {
                    "name": "Render",
                    "suitability_score": 85,
                    "advantages": ["Easy web service and Postgres database hosting"],
                    "disadvantages": ["Free tier instance sleep delay"],
                    "difficulty": "easy",
                    "fit_reason": "Simple PaaS alternative to Heroku",
                    "not_fit_reason": "Less control than raw VPS",
                    "is_recommended": False
                },
                {
                    "name": "AWS",
                    "suitability_score": 80,
                    "advantages": ["Full suite of cloud services and unlimited scale"],
                    "disadvantages": ["Complex IAM and pricing structures"],
                    "difficulty": "hard",
                    "fit_reason": "Enterprise scalability requirement",
                    "not_fit_reason": "High operational complexity for small teams",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "api_communication",
            "recommendation": "REST API",
            "recommendation_reason": "Simple, ubiquitous HTTP protocol standard with wide tool and library compatibility.",
            "alternatives": [
                {
                    "name": "REST API",
                    "suitability_score": 94,
                    "advantages": ["Standardized HTTP methods", "Stateless and easily cached", "Universal tool support"],
                    "disadvantages": ["Potential over-fetching or under-fetching of data"],
                    "difficulty": "easy",
                    "fit_reason": "Universal standard for frontend-backend interaction",
                    "not_fit_reason": "Complex nested query requirements",
                    "is_recommended": True
                },
                {
                    "name": "GraphQL",
                    "suitability_score": 82,
                    "advantages": ["Client specifies exact fields needed", "Single endpoint for data fetching"],
                    "disadvantages": ["Backend query complexity and caching challenges"],
                    "difficulty": "medium",
                    "fit_reason": "Complex frontends needing flexible data shaping",
                    "not_fit_reason": "Added setup complexity for basic CRUD",
                    "is_recommended": False
                },
                {
                    "name": "WebSockets",
                    "suitability_score": 80,
                    "advantages": ["Full-duplex real-time bidirectional communication"],
                    "disadvantages": ["Stateful connection management requirements"],
                    "difficulty": "medium",
                    "fit_reason": "Real-time chat or live notifications",
                    "not_fit_reason": "Not suitable for standard static data requests",
                    "is_recommended": False
                },
                {
                    "name": "gRPC",
                    "suitability_score": 75,
                    "advantages": ["High performance binary serialization (Protocol Buffers)"],
                    "disadvantages": ["Browser client support limitations"],
                    "difficulty": "hard",
                    "fit_reason": "Internal microservice-to-microservice communication",
                    "not_fit_reason": "Public browser APIs",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "devops",
            "recommendation": "GitHub Actions",
            "recommendation_reason": "Integrated CI/CD workflows directly within code repositories for automated testing and deployment.",
            "alternatives": [
                {
                    "name": "GitHub Actions",
                    "suitability_score": 93,
                    "advantages": ["Native integration with GitHub repos", "Vast marketplace of pre-built actions"],
                    "disadvantages": ["Free minutes cap on private repos"],
                    "difficulty": "easy",
                    "fit_reason": "Automated build, test, and release pipelines",
                    "not_fit_reason": "Non-GitHub hosted repositories",
                    "is_recommended": True
                },
                {
                    "name": "Docker",
                    "suitability_score": 90,
                    "advantages": ["Standard containerization technology"],
                    "disadvantages": ["Requires setup"],
                    "difficulty": "medium",
                    "fit_reason": "Consistent execution runtime",
                    "not_fit_reason": "None",
                    "is_recommended": False
                },
                {
                    "name": "Kubernetes",
                    "suitability_score": 70,
                    "advantages": ["Container orchestration at massive scale"],
                    "disadvantages": ["Extremely high operational complexity"],
                    "difficulty": "hard",
                    "fit_reason": "Large multi-service cluster management",
                    "not_fit_reason": "Unnecessary complexity for single apps",
                    "is_recommended": False
                },
                {
                    "name": "Terraform",
                    "suitability_score": 78,
                    "advantages": ["Infrastructure as Code (IaC) for cloud provisioning"],
                    "disadvantages": ["Requires learning HCL language"],
                    "difficulty": "medium",
                    "fit_reason": "Multi-cloud infrastructure automation",
                    "not_fit_reason": "Simple PaaS deployments",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "caching_messaging",
            "recommendation": "Redis",
            "recommendation_reason": "In-memory data store for ultra-fast caching, session management, and rate limiting.",
            "alternatives": [
                {
                    "name": "Redis",
                    "suitability_score": 95,
                    "advantages": ["Sub-millisecond latency", "Rich data structures", "Widespread backend support"],
                    "disadvantages": ["In-memory storage cost limits dataset size"],
                    "difficulty": "easy",
                    "fit_reason": "High performance session storage and cache layer",
                    "not_fit_reason": "Primary persistent data storage",
                    "is_recommended": True
                },
                {
                    "name": "Celery",
                    "suitability_score": 85,
                    "advantages": ["Distributed Python task queue integration"],
                    "disadvantages": ["Requires Redis or RabbitMQ broker"],
                    "difficulty": "medium",
                    "fit_reason": "Background asynchronous job processing",
                    "not_fit_reason": "Non-Python services",
                    "is_recommended": False
                },
                {
                    "name": "RabbitMQ",
                    "suitability_score": 80,
                    "advantages": ["Complex message routing topology support"],
                    "disadvantages": ["More complex operational administration than Redis"],
                    "difficulty": "medium",
                    "fit_reason": "Reliable enterprise message queuing",
                    "not_fit_reason": "Simple key-value caching",
                    "is_recommended": False
                },
                {
                    "name": "Memcached",
                    "suitability_score": 75,
                    "advantages": ["Simple multithreaded key-value memory cache"],
                    "disadvantages": ["Lacks advanced data types or persistence"],
                    "difficulty": "easy",
                    "fit_reason": "Basic string caching",
                    "not_fit_reason": "Data persistence needs",
                    "is_recommended": False
                }
            ]
        },
        {
            "category": "testing",
            "recommendation": "Pytest",
            "recommendation_reason": "Powerful, clean Python testing framework with simple fixture management and auto-discovery.",
            "alternatives": [
                {
                    "name": "Pytest",
                    "suitability_score": 94,
                    "advantages": ["Simple assert statements", "Rich fixture ecosystem", "Fast parallel execution"],
                    "disadvantages": ["Python specific"],
                    "difficulty": "easy",
                    "fit_reason": "Backend test suite automation",
                    "not_fit_reason": "Frontend DOM unit testing",
                    "is_recommended": True
                },
                {
                    "name": "Jest",
                    "suitability_score": 88,
                    "advantages": ["Standard JavaScript/React testing runner"],
                    "disadvantages": ["Can be slower in large monorepos"],
                    "difficulty": "easy",
                    "fit_reason": "Frontend React component unit testing",
                    "not_fit_reason": "Python backend testing",
                    "is_recommended": False
                },
                {
                    "name": "Vitest",
                    "suitability_score": 86,
                    "advantages": ["Blazing fast Vite-native test runner"],
                    "disadvantages": ["Newer ecosystem than Jest"],
                    "difficulty": "easy",
                    "fit_reason": "Vite-based frontend testing",
                    "not_fit_reason": "Legacy Webpack setups",
                    "is_recommended": False
                },
                {
                    "name": "Playwright",
                    "suitability_score": 84,
                    "advantages": ["Reliable end-to-end browser automation"],
                    "disadvantages": ["Longer execution time for full E2E runs"],
                    "difficulty": "medium",
                    "fit_reason": "End-to-end browser integration testing",
                    "not_fit_reason": "Fast unit tests",
                    "is_recommended": False
                }
            ]
        }
    ]

    formatted_categories = []
    for cat_data in categories_data:
        alts = [TechAlternative(**alt) for alt in cat_data["alternatives"]]
        formatted_categories.append(
            TechCategory(
                category=cat_data["category"],
                recommendation=cat_data["recommendation"],
                recommendation_reason=cat_data["recommendation_reason"],
                alternatives=alts
            )
        )

    return TechnologyRecommendations(
        categories=formatted_categories,
        overall_analysis="Standard curated 10-category technology recommendations catalog.",
        web_research_used=False,
        web_research_note="Standard curated catalog used as AI service was temporarily busy/unavailable."
    )


def _perform_web_research(requirements: ProjectRequirements) -> str:
    """Perform Tavily web research for current technology information.

    Queries latest stable versions, official documentation, compatibility, and suitability.
    Never raises exceptions — returns formatted research text or empty string if unavailable.
    """
    if not tavily_tool.api_key:
        logger.info("Technology Advisor: Tavily not configured (TAVILY_API_KEY not set), skipping web research")
        return ""

    research_parts = []
    project_context = f"{requirements.project_name} {requirements.project_description}"

    search_queries = [
        f"latest stable version official documentation best web framework {requirements.complexity} complexity 2024 2025",
        f"official documentation tech stack suitability compatibility {requirements.project_name[:30]}",
    ]

    if requirements.preferred_technologies:
        prefs = " ".join(requirements.preferred_technologies[:3])
        search_queries.append(f"{prefs} latest stable version official documentation compatibility suitability 2024 2025")
    elif any(kw in project_context.lower() for kw in ["ecommerce", "e-commerce", "shop", "store"]):
        search_queries.append("ecommerce tech stack latest versions official documentation suitability 2024 2025")
    elif any(kw in project_context.lower() for kw in ["ai", "ml", "machine learning"]):
        search_queries.append("AI ML stack latest stable versions official documentation 2024 2025")

    for query in search_queries[:3]:
        try:
            results = tavily_tool.search(query, max_results=3)
            if results.available and results.results:
                for r in results.results:
                    if r.title or r.content:
                        research_parts.append(f"- {r.title} ({r.url}): {r.content[:300]}")
        except Exception as e:
            logger.warning(f"Technology Advisor: Individual Tavily query '{query}' failed: {e}")
            continue

    if research_parts:
        return (
            "CURRENT WEB RESEARCH (from Tavily - Official Docs & Recent Updates):\n"
            + "\n".join(research_parts)
            + "\n\nUse this current web research information to inform your recommendations, "
            "focusing on latest stable versions, official documentation, compatibility, and suitability.\n"
        )

    return ""


def _format_requirements(requirements: ProjectRequirements) -> str:
    """Format requirements into a readable text block."""
    parts = [
        f"Project: {requirements.project_name}",
        f"Description: {requirements.project_description}",
        f"Team Size: {requirements.team_size} people",
        f"Deadline: {requirements.deadline_days} days",
        f"Skill Level: {requirements.skill_level}",
        f"Complexity: {requirements.complexity}",
    ]

    if requirements.budget is not None:
        parts.append(f"Budget: ${requirements.budget}")

    if requirements.goals:
        parts.append(f"Goals: {', '.join(requirements.goals)}")

    if requirements.features:
        parts.append(f"Features: {', '.join(requirements.features)}")

    if requirements.preferred_technologies:
        parts.append(f"Preferred Technologies: {', '.join(requirements.preferred_technologies)}")

    if requirements.constraints:
        parts.append(f"Constraints: {', '.join(requirements.constraints)}")

    if requirements.special_requirements:
        parts.append(f"Special Requirements: {', '.join(requirements.special_requirements)}")

    return "\n".join(parts)
