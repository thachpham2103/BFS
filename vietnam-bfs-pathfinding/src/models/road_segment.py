from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

from models.province import Province


class RoadType(str, Enum):
    """Loại đường đi giữa các tỉnh"""
    DEFAULT = "default"  # Khoảng cách thực giữa 2 tọa độ (không hệ số)
    HIGHWAY = "highway"  # Cao tốc
    NATIONAL = "national"  # Quốc lộ
    PROVINCIAL = "provincial"  # Tỉnh lộ
    UNKNOWN = "unknown"  # Chưa xác định


@dataclass
class RoadSegment:
    """Đại diện cho một đoạn đường giữa hai tỉnh liền kề
    
    Attributes:
        from_province: Tỉnh xuất phát
        to_province: Tỉnh đến
        distance_km: Khoảng cách đường bộ (km)
        road_type: Loại đường (cao tốc, quốc lộ, tỉnh lộ)
        road_name: Tên đường (vd: QL1A, CT Hà Nội - Hải Phòng)
    """
    from_province: Province
    to_province: Province
    distance_km: float
    road_type: RoadType = RoadType.UNKNOWN
    road_name: Optional[str] = None
    
    def __post_init__(self) -> None:
        if self.distance_km < 0:
            raise ValueError("Distance must be non-negative")
    
    @property
    def start_coordinates(self) -> Optional[Tuple[float, float]]:
        """Trả về tọa độ điểm bắt đầu (latitude, longitude)"""
        if self.from_province.latitude and self.from_province.longitude:
            return (self.from_province.latitude, self.from_province.longitude)
        return None
    
    @property
    def end_coordinates(self) -> Optional[Tuple[float, float]]:
        """Trả về tọa độ điểm kết thúc (latitude, longitude)"""
        if self.to_province.latitude and self.to_province.longitude:
            return (self.to_province.latitude, self.to_province.longitude)
        return None
    
    def to_dict(self) -> Dict:
        """Convert sang dict để serialize JSON"""
        return {
            "from": {
                "code": self.from_province.code,
                "name": self.from_province.name,
                "coordinates": {
                    "latitude": self.from_province.latitude,
                    "longitude": self.from_province.longitude
                }
            },
            "to": {
                "code": self.to_province.code,
                "name": self.to_province.name,
                "coordinates": {
                    "latitude": self.to_province.latitude,
                    "longitude": self.to_province.longitude
                }
            },
            "distance_km": round(self.distance_km, 2),
            "road_type": self.road_type.value,
            "road_name": self.road_name
        }
    
    def __str__(self) -> str:
        road_info = f" ({self.road_name})" if self.road_name else ""
        return (
            f"{self.from_province.name} → {self.to_province.name}: "
            f"{self.distance_km:.1f}km [{self.road_type.value}]{road_info}"
        )
