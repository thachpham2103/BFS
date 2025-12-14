import logging
from typing import Dict, Any, Coroutine

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
router = APIRouter(prefix="/path", tags=["pathfinding"])


def get_service() -> PathfindingService:
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
    try:
        logger.info(
            f"Finding path: {request.start} -> {request.end}, "
            f"road_type={request.road_type}"
        )
        
        result = service.find_path(
            request.start,
            request.end,
            fuzzy_match=request.fuzzy_match,
            road_type=request.road_type
        )
        
        response = result.to_dict()
        
        logger.info(
            f"Path found: {result.distance} provinces, "
            f"{result.total_distance_km:.2f}km, "
            f"{result.execution_time * 1000:.2f}ms"
        )
        
        return response
        
    except ProvinceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except NoPathFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidInputError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
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
async def find_reachable(
    request: ReachableRequest,
    service: PathfindingService = Depends(get_service)
) -> Dict:
    try:
        results = service.find_reachable(
            start=request.start,
            max_distance=request.max_distance,
            fuzzy_match=request.fuzzy_match
        )
        return {
            code: ReachableProvinceSchema(
                code=p.code,
                name=p.name,
                full_name=p.full_name,
                distance=d
            )
            for code, (p, d) in results.items()
        }
    
    except ProvinceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidInputError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidInputError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
