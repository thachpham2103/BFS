import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict

project_root = Path(__file__).parent.parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config.settings import get_settings
from data.data_loader import DataLoader
from models.province import ProvinceRegistry
from services.pathfinding_service import PathfindingService
from api.routes import path_routes, province_routes
from api.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_service: PathfindingService = None


def get_pathfinding_service() -> PathfindingService:

    global _service
    if _service is None:
        raise RuntimeError("Service not initialized")
    return _service


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting up Finding Distance API...")
    
    global _service
    
    try:
        # Load settings
        settings = get_settings()
        logger.info(f"Settings loaded: DEBUG={settings.debug}")
        
        # Load data
        logger.info("Loading province data...")
        loader = DataLoader()
        provinces_path = project_root / "data" / "provinces.json"
        adjacency_path = project_root / "data" / "adjacency.json"
        loader.load_data(
            provinces_path=str(provinces_path),
            adjacency_path=str(adjacency_path)
        )
        
        # Initialize registry
        logger.info("Initializing province registry...")
        registry = ProvinceRegistry()
        registry.initialize(
            loader.get_provinces(),
            loader.get_adjacency()
        )
        
        # Create service
        logger.info("Creating pathfinding service...")
        _service = PathfindingService(registry)
        
        logger.info(
            f"API started successfully with {registry.count()} provinces"
            f"\nURl:      localhost:{settings.api_port}/docs#/"
        )
        yield
        
    except Exception as e:
        logger.error(f"Failed to start API: {e}", exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Finding Distance API...")
        _service = None


app = FastAPI(
    title="Finding Distance API",
    description="API để tìm đường đi giữa các tỉnh thành Việt Nam bằng thuật toán BFS",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(path_routes.router, prefix="/api/v1")
app.include_router(province_routes.router, prefix="/api/v1")

app.dependency_overrides[path_routes.get_service] = get_pathfinding_service
app.dependency_overrides[province_routes.get_service] = get_pathfinding_service


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Kiểm tra trạng thái hệ thống",
    tags=["system"]
)
async def health_check() -> Dict:

    try:
        service = get_pathfinding_service()
        province_count = service.registry.count()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "total_provinces": province_count,
            "graph_status": "built"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Xử lý lỗi validation với thông báo thân thiện."""
    errors = exc.errors()
    messages = []
    
    for err in errors:
        field = err.get("loc", ["unknown"])[-1]
        err_type = err.get("type", "")
        
        if err_type == "string_too_short" or err_type == "missing":
            if field == "start":
                messages.append("Vui lòng nhập tỉnh bắt đầu")
            elif field == "end":
                messages.append("Vui lòng nhập tỉnh kết thúc")
            else:
                messages.append(f"Trường '{field}' không được để trống")
        elif err_type == "value_error":
            messages.append(err.get("msg", "Giá trị không hợp lệ"))
        else:
            messages.append(f"Trường '{field}': {err.get('msg', 'không hợp lệ')}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "; ".join(messages) if messages else "Dữ liệu đầu vào không hợp lệ"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Xử lý HTTPException với thông báo thân thiện."""
    error_type = "NotFound" if exc.status_code == 404 else "Error"
    if exc.status_code == 422:
        error_type = "ValidationError"
    
    message = exc.detail
    if exc.status_code == 404 and message == "Not Found":
        message = "Endpoint không tồn tại"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_type,
            "message": message
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "Lỗi hệ thống không xác định"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "api.main:app",
        # host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )
