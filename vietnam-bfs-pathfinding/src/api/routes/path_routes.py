import logging
from typing import Dict

from fastapi import APIRouter, HTTPException, status, Depends

from api.schemas import (
    PathRequest,
    PathResponse,
    ReachableRequest,
    ReachableProvinceSchema,
    ConnectivityRequest,
    ConnectivityResponse,
    ErrorResponse
)
from services.pathfinding_service import PathfindingService
from models.exceptions import (
    ProvinceNotFoundError,
    NoPathFoundError,
    InvalidInputError
)

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/path", tags=["Pathfinding"])


def get_service() -> PathfindingService:
    """Dependency injection cho PathfindingService.
    
    Vai trò: Tạo/lấy instance service cho các endpoint, cần được config trong main.py.
    """
    raise NotImplementedError("Service dependency not configured")


@router.post(
    "/find",
    response_model=PathResponse,
    status_code=status.HTTP_200_OK,
    summary="Tìm đường đi ngắn nhất",
    description="Tìm đường đi ngắn nhất giữa hai tỉnh sử dụng thuật toán BFS",
    responses={
        200: {
            "description": "Tìm thấy đường đi",
            "model": PathResponse
        },
        404: {
            "description": "Không tìm thấy tỉnh hoặc đường đi",
            "model": ErrorResponse
        },
        422: {
            "description": "Dữ liệu đầu vào không hợp lệ",
            "model": ErrorResponse
        }
    }
)
async def find_path(
    request: PathRequest,
    service: PathfindingService = Depends(get_service)
) -> Dict:
    """API endpoint tìm đường đi ngắn nhất giữa hai tỉnh.
    
    Vai trò: Xử lý request tìm đường, convert exception thành HTTP response phù hợp.
    """
    try:
        logger.info(f"Finding path: {request.start} -> {request.end}")
        
        result = service.find_path(
            request.start,
            request.end,
            fuzzy_match=request.fuzzy_match
        )
        
        response = result.to_dict()
        
        logger.info(
            f"Path found: {result.distance} provinces, "
            f"{result.execution_time * 1000:.2f}ms"
        )
        
        return response
        
    except ProvinceNotFoundError as e:
        logger.warning(f"Province not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ProvinceNotFoundError",
                "message": str(e),
                "suggestions": e.suggestions
            }
        )
    except NoPathFoundError as e:
        logger.warning(f"No path found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NoPathFoundError",
                "message": str(e)
            }
        )
    except InvalidInputError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "InvalidInputError",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Lỗi hệ thống không xác định"
            }
        )


@router.post(
    "/reachable",
    response_model=Dict[str, ReachableProvinceSchema],
    status_code=status.HTTP_200_OK,
    summary="Tìm các tỉnh có thể đến được",
    description="Tìm tất cả các tỉnh có thể đến được từ một tỉnh trong khoảng cách cho trước",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
async def get_reachable_provinces(
    request: ReachableRequest,
    service: PathfindingService = Depends(get_service)
) -> Dict:
    """API endpoint lấy danh sách tỉnh tiếp cận được.
    
    Vai trò: Trả về các tỉnh trong phạm vi khoảng cách cho trước từ điểm xuất phát.
    """
    try:
        logger.info(
            f"Finding reachable provinces from {request.start} "
            f"(max_distance: {request.max_distance})"
        )
        
        result = service.get_reachable_provinces(
            request.start,
            max_distance=request.max_distance
        )
        
        logger.info(f"Found {len(result)} reachable provinces")
        
        return result
        
    except ProvinceNotFoundError as e:
        logger.warning(f"Province not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ProvinceNotFoundError",
                "message": str(e),
                "suggestions": e.suggestions
            }
        )
    except InvalidInputError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "InvalidInputError",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Lỗi hệ thống không xác định"
            }
        )


@router.post(
    "/connectivity",
    response_model=ConnectivityResponse,
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra kết nối",
    description="Kiểm tra xem hai tỉnh có liên thông với nhau không",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
async def check_connectivity(
    request: ConnectivityRequest,
    service: PathfindingService = Depends(get_service)
) -> Dict:
    """API endpoint kiểm tra kết nối giữa hai tỉnh.
    
    Vai trò: Kiểm tra nhanh sự tồn tại đường đi mà không tính toán đường đi cụ thể.
    """
    try:
        logger.info(
            f"Checking connectivity: {request.province1} <-> {request.province2}"
        )
        
        # Get province info
        p1_info = service.get_province_info(request.province1)
        p2_info = service.get_province_info(request.province2)
        
        connected = service.check_connectivity(
            request.province1,
            request.province2
        )
        
        logger.info(f"Connectivity: {connected}")
        
        return {
            "province1": {
                "code": p1_info["code"],
                "name": p1_info["name"]
            },
            "province2": {
                "code": p2_info["code"],
                "name": p2_info["name"]
            },
            "connected": connected
        }
        
    except ProvinceNotFoundError as e:
        logger.warning(f"Province not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ProvinceNotFoundError",
                "message": str(e),
                "suggestions": e.suggestions
            }
        )
    except InvalidInputError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "InvalidInputError",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Lỗi hệ thống không xác định"
            }
        )
