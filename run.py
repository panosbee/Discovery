"""
Run Medical Discovery Engine API Server
"""
import uvicorn
from medical_discovery.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "medical_discovery.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
