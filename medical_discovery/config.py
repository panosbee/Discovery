"""
Configuration management for Medical Discovery Engine
Loads settings from environment variables with production-ready defaults
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Medical Discovery Engine"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server
    host: str = "localhost"
    port: int = 8000
    
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "medical_discovery"
    
    # DeepSeek API
    deepseek_api_key: str
    deepseek_api_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    deepseek_max_tokens: int = 4096
    deepseek_temperature: float = 0.7
    
    # Jina AI Embeddings
    jina_api_key: str
    jina_api_url: str = "https://api.jina.ai/v1"
    jina_embedding_model: str = "jina-embeddings-v2-base-en"
    
    # PubMed API
    pubmed_api_key: str
    pubmed_api_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    pubmed_email: str = "research@medresearch.ai"
    pubmed_tool: str = "MedicalDiscoveryEngine"
    pubmed_max_results: int = 100
    
    # Springer API
    springer_open_access_api_key: Optional[str] = None
    springer_meta_api_key: Optional[str] = None
    springer_api_url: str = "https://api.springernature.com"
    
    # Zenodo API
    zenodo_url: str = "https://zenodo.org"
    zenodo_token: str
    zenodo_api_url: str = "https://zenodo.org/api"
    community_slug: str = "medresearch-ai"
    
    # OAuth Credentials
    zenodo_oauth_client_id: Optional[str] = None
    zenodo_oauth_client_secret: Optional[str] = None
    zenodo_oauth_redirect_uri: Optional[str] = None
    
    # Security
    jwt_secret_key: str
    encryption_key: str
    access_token_expire_minutes: int = 1440
    
    # Vector Database
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "medical_documents"
    qdrant_vector_size: int = 768
    
    # Neo4j Graph Database
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # MinIO/S3 Storage
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "medical-discovery"
    minio_secure: bool = False
    
    # File Settings
    max_file_size: int = 52428800  # 50MB
    upload_directory: str = "uploads"
    
    # Email Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    email_from_name: str = "Medical Discovery Engine"
    email_from_address: str = "noreply@medresearch-ai.org"
    
    # Mailgun Configuration
    mailgun_api_key: Optional[str] = None
    mailgun_domain: Optional[str] = None
    
    # SMTP2GO Configuration
    smtp2go_api_key: Optional[str] = None
    smtp2go_base_url: str = "https://api.smtp2go.com/v3"
    
    # ORCID Integration
    orcid_client_id: Optional[str] = None
    orcid_client_secret: Optional[str] = None
    orcid_environment: str = "production"
    orcid_redirect_uri: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Agent Configuration
    max_hypothesis_runtime_minutes: int = 10
    max_concurrent_agents: int = 5
    agent_timeout_seconds: int = 300
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # Supported Medical Domains
    supported_domains: List[str] = [
        "cardiology",
        "oncology", 
        "neurology",
        "diabetes",
        "infectious_diseases",
        "genetics",
        "immunology",
        "nephrology",
        "pulmonology",
        "gastroenterology",
        "endocrinology",
        "hematology",
        "rheumatology",
        "psychiatry",
        "general_medicine"
    ]
    
    # Cross-Domain Sources
    cross_domain_sources: List[str] = [
        "clinical",
        "materials",
        "foodtech",
        "engineering",
        "nanomedicine",
        "bioinformatics",
        "chemistry",
        "physics"
    ]
    
    @property
    def mongodb_connection_string(self) -> str:
        """Get MongoDB connection string"""
        return f"{self.mongodb_url}/{self.mongodb_database}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
settings = Settings()
