import logging
from typing import Dict, List

from fastapi import APIRouter, HTTPException, status, Depends, Query

from api.schemas import (
    ProvinceSchema,
    ProvinceDetailSchema,
    ErrorResponse
)
from services.pathfinding_service import PathfindingService
from models.exceptions import ProvinceNotFoundError, InvalidInputError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/provinces", tags=["Provinces"])


def get_service() -> PathfindingService:
    """Dependency injection cho PathfindingService.
    
    Vai trò: Tạo/lấy instance service cho các endpoint, cần được config trong main.py.
    """
    raise NotImplementedError("Service dependency not configured")


@router.get(
    "",
    response_model=List[ProvinceSchema],
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách tất cả tỉnh",
    description="Lấy danh sách tất cả các tỉnh thành trong hệ thống",
)
async def get_all_provinces(
    service: PathfindingService = Depends(get_service)
) -> List[Dict]:
    """API endpoint lấy danh sách tất cả tỉnh.
    
    Vai trò: Cung cấp dữ liệu cho dropdown/select trong frontend.
    """
    try:
        logger.info("Getting all provinces")
        provinces = service.get_all_provinces()
        logger.info(f"Returned {len(provinces)} provinces")
        return provinces
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Lỗi hệ thống không xác định"
            }
        )


@router.get(
    "/{province_id}",
    response_model=ProvinceDetailSchema,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin tỉnh",
    description="Lấy thông tin chi tiết của một tỉnh (bao gồm các tỉnh lân cận)",
    responses={
        404: {"model": ErrorResponse}
    }
)
async def get_province(
    province_id: str,
    service: PathfindingService = Depends(get_service)
) -> Dict:
    """API endpoint lấy thông tin chi tiết một tỉnh.
    
    Vai trò: Trả về thông tin tỉnh và danh sách tỉnh lân cận.
    """
    try:
        logger.info(f"Getting province info: {province_id}")
        info = service.get_province_info(province_id)
        logger.info(f"Found province: {info['name']}")
        return info
        
    except ProvinceNotFoundError as e:
        logger.warning(f"Province not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ProvinceNotFoundError",
                "message": f"Không tìm thấy tỉnh '{province_id}'. Vui lòng nhập mã tỉnh (ví dụ: 01 hoặc 1) hoặc tên tỉnh (ví dụ: Hà Nội).",
                "original_error": str(e),
                "suggestions": e.suggestions
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

