from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ProvinceSchema(BaseModel):
    """Province information schema."""
    
    code: str = Field(..., description="Mã tỉnh (2 chữ số)")
    name: str = Field(..., description="Tên tỉnh")
    full_name: str = Field(..., description="Tên đầy đủ")
    code_name: Optional[str] = Field(None, description="Tên không dấu")
    neighbor_count: Optional[int] = Field(None, description="Số lượng tỉnh lân cận")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "01",
                "name": "Hà Nội",
                "full_name": "Thành phố Hà Nội",
                "code_name": "ha_noi",
                "neighbor_count": 4
            }
        }
    }


class NeighborSchema(BaseModel):

    code: str = Field(..., description="Mã tỉnh")
    name: str = Field(..., description="Tên tỉnh")


class ProvinceDetailSchema(ProvinceSchema):

    neighbors: List[NeighborSchema] = Field(
        default_factory=list,
        description="Danh sách tỉnh lân cận"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "01",
                "name": "Hà Nội",
                "full_name": "Thành phố Hà Nội",
                "code_name": "ha_noi",
                "neighbor_count": 4,
                "neighbors": [
                    {"code": "24", "name": "Bắc Ninh"},
                    {"code": "25", "name": "Phú Thọ"}
                ]
            }
        }
    }


class PathRequest(BaseModel):

    start: str = Field(
        ...,
        description="Tỉnh bắt đầu (mã hoặc tên)",
        min_length=1
    )
    end: str = Field(
        ...,
        description="Tỉnh kết thúc (mã hoặc tên)",
        min_length=1
    )
    fuzzy_match: bool = Field(
        default=True,
        description="Cho phép tìm kiếm gần đúng"
    )
    
    @field_validator('start', 'end')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Không được để trống")
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "start": "Hà Nội",
                "end": "Hồ Chí Minh",
                "fuzzy_match": True
            }
        }
    }


class PathStepSchema(BaseModel):

    step_number: int = Field(..., description="Số thứ tự bước")
    from_province: dict = Field(..., description="Tỉnh xuất phát")
    to_province: dict = Field(..., description="Tỉnh đích")


class PathResponse(BaseModel):

    path: List[str] = Field(..., description="Danh sách tên tỉnh trong đường đi")
    path_codes: List[str] = Field(..., description="Danh sách mã tỉnh trong đường đi")
    distance: int = Field(..., description="Số lượng tỉnh trong đường đi")
    start_province: dict = Field(..., description="Thông tin tỉnh bắt đầu")
    end_province: dict = Field(..., description="Thông tin tỉnh kết thúc")
    execution_time_ms: float = Field(..., description="Thời gian tìm kiếm (ms)")
    timestamp: datetime = Field(..., description="Thời điểm tìm kiếm")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "path": ["Hà Nội", "Phú Thọ", "Thanh Hóa"],
                "path_codes": ["01", "25", "38"],
                "distance": 3,
                "start_province": {
                    "code": "01",
                    "name": "Hà Nội",
                    "full_name": "Thành phố Hà Nội"
                },
                "end_province": {
                    "code": "38",
                    "name": "Thanh Hóa",
                    "full_name": "Tỉnh Thanh Hóa"
                },
                "execution_time_ms": 0.15,
                "timestamp": "2025-01-01T10:00:00"
            }
        }
    }


class SearchRequest(BaseModel):

    query: str = Field(
        ...,
        description="Từ khóa tìm kiếm",
        min_length=1
    )
    limit: Optional[int] = Field(
        default=None,
        description="Số lượng kết quả tối đa",
        ge=1,
        le=100
    )
    
    @field_validator('query')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Từ khóa tìm kiếm không được để trống")
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Hồ",
                "limit": 10
            }
        }
    }


class ReachableRequest(BaseModel):

    start: str = Field(
        ...,
        description="Tỉnh bắt đầu (mã hoặc tên)",
        min_length=1
    )
    max_distance: Optional[int] = Field(
        default=None,
        description="Khoảng cách tối đa",
        ge=1
    )
    
    @field_validator('start')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tỉnh bắt đầu không được để trống")
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "start": "Hà Nội",
                "max_distance": 3
            }
        }
    }


class ReachableProvinceSchema(BaseModel):

    code: str = Field(..., description="Mã tỉnh")
    name: str = Field(..., description="Tên tỉnh")
    full_name: str = Field(..., description="Tên đầy đủ")
    distance: int = Field(..., description="Khoảng cách (số tỉnh)")


class ConnectivityRequest(BaseModel):

    province1: str = Field(
        ...,
        description="Tỉnh thứ nhất (mã hoặc tên)",
        min_length=1
    )
    province2: str = Field(
        ...,
        description="Tỉnh thứ hai (mã hoặc tên)",
        min_length=1
    )
    
    @field_validator('province1', 'province2')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Tỉnh không được để trống")
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "province1": "Hà Nội",
                "province2": "Hồ Chí Minh"
            }
        }
    }


class ConnectivityResponse(BaseModel):

    province1: dict = Field(..., description="Thông tin tỉnh thứ nhất")
    province2: dict = Field(..., description="Thông tin tỉnh thứ hai")
    connected: bool = Field(..., description="Có liên thông không")


class StatisticsResponse(BaseModel):

    total_provinces: int = Field(..., description="Tổng số tỉnh")
    total_edges: int = Field(..., description="Tổng số kết nối")
    avg_neighbors: float = Field(..., description="Số lượng tỉnh lân cận trung bình")
    min_neighbors: int = Field(..., description="Số lượng tỉnh lân cận tối thiểu")
    max_neighbors: int = Field(..., description="Số lượng tỉnh lân cận tối đa")
    is_connected: bool = Field(..., description="Đồ thị có liên thông không")
    graph_built: bool = Field(..., description="Đồ thị đã được xây dựng chưa")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_provinces": 34,
                "total_edges": 68,
                "avg_neighbors": 4.0,
                "min_neighbors": 2,
                "max_neighbors": 6,
                "is_connected": True,
                "graph_built": True
            }
        }
    }


class ValidationResponse(BaseModel):

    valid: bool = Field(..., description="Input có hợp lệ không")
    province: Optional[dict] = Field(None, description="Thông tin tỉnh nếu tìm thấy")
    matched_by: Optional[str] = Field(None, description="Phương thức tìm thấy")
    original_input: Optional[str] = Field(None, description="Input gốc")
    error: Optional[str] = Field(None, description="Thông báo lỗi")
    suggestions: Optional[List[str]] = Field(None, description="Gợi ý tỉnh")


class ErrorResponse(BaseModel):

    error: str = Field(..., description="Loại lỗi")
    message: str = Field(..., description="Thông báo lỗi")
    detail: Optional[str] = Field(None, description="Chi tiết lỗi")
    suggestions: Optional[List[str]] = Field(None, description="Gợi ý")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "ProvinceNotFoundError",
                "message": "Không tìm thấy tỉnh 'Sài Gòn' trong hệ thống",
                "suggestions": ["Hồ Chí Minh", "TP. Hồ Chí Minh"]
            }
        }
    }


class HealthResponse(BaseModel):

    status: str = Field(..., description="Trạng thái hệ thống")
    version: str = Field(..., description="Phiên bản API")
    total_provinces: int = Field(..., description="Tổng số tỉnh")
    graph_status: str = Field(..., description="Trạng thái đồ thị")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "total_provinces": 34,
                "graph_status": "built"
            }
        }
    }
