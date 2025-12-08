import logging
import math
from typing import Dict, Optional, Tuple
from functools import lru_cache

from models.province import Province
from models.road_segment import RoadSegment, RoadType

logger = logging.getLogger(__name__)


class DistanceCalculator:
    """Tính toán khoảng cách giữa các tỉnh
    
    Hỗ trợ :
    - Haversine: Khoảng cách đường chim bay bằng tọa độ của tỉnh trong provinces.json
    - Road estimation: Ước lượng đường bộ (đường chim bay * hệ số điều chỉnh)
    """
    
    # Hệ số điều chỉnh để ước lượng đường bộ từ đường chim bay
    # Đường bộ thường dài hơn 20-50% so với đường chim bay
    ROAD_ADJUSTMENT_FACTORS = {
        RoadType.DEFAULT: 1.0,     # Khoảng cách thực (không điều chỉnh)
        RoadType.HIGHWAY: 1.2,     # Cao tốc: đường thẳng hơn
        RoadType.NATIONAL: 1.35,   # Quốc lộ: có đường vòng
        RoadType.PROVINCIAL: 1.5,  # Tỉnh lộ: nhiều đường vòng
        RoadType.UNKNOWN: 1.35     # Mặc định như quốc lộ
    }
    
    EARTH_RADIUS_KM = 6371.0
    
    def __init__(self):
        pass
    
    @staticmethod
    @lru_cache(maxsize=10000)
    def haversine_distance(
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """Tính khoảng cách đường chim bay bằng công thức Haversine
        
        Args:
            lat1, lon1: Tọa độ điểm 1
            lat2, lon2: Tọa độ điểm 2
            
        Returns:
            Khoảng cách theo km
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        
        return DistanceCalculator.EARTH_RADIUS_KM * c
    
    def estimate_road_distance(
        self,
        province1: Province,
        province2: Province,
        road_type: RoadType = RoadType.UNKNOWN
    ) -> float:
        """Ước lượng khoảng cách đường bộ
        
        Sử dụng khoảng cách đường chim bay * hệ số điều chỉnh
        
        Args:
            province1: Tỉnh 1
            province2: Tỉnh 2
            road_type: Loại đường (ảnh hưởng đến hệ số điều chỉnh)
            
        Returns:
            Khoảng cách ước lượng (km)
            
        Raises:
            ValueError: Nếu thiếu tọa độ
        """
        if not all([
            province1.latitude, province1.longitude,
            province2.latitude, province2.longitude
        ]):
            raise ValueError(
                f"Missing coordinates for distance calculation: "
                f"{province1.name} or {province2.name}"
            )
        
        # Tính khoảng cách đường chim bay
        straight_distance = self.haversine_distance(
            province1.latitude, province1.longitude,
            province2.latitude, province2.longitude
        )
        
        # Áp dụng hệ số điều chỉnh
        adjustment_factor = self.ROAD_ADJUSTMENT_FACTORS.get(
            road_type,
            self.ROAD_ADJUSTMENT_FACTORS[RoadType.UNKNOWN]
        )
        
        road_distance = straight_distance * adjustment_factor
        
        logger.debug(
            f"Distance {province1.name} -> {province2.name}: "
            f"{straight_distance:.1f}km (straight) -> "
            f"{road_distance:.1f}km (road, factor={adjustment_factor})"
        )
        
        return road_distance
    
    def create_road_segment(
        self,
        from_province: Province,
        to_province: Province,
        road_type: RoadType = RoadType.UNKNOWN,
        road_name: Optional[str] = None
    ) -> RoadSegment:
        """Tạo RoadSegment với khoảng cách được tính toán
        
        Args:
            from_province: Tỉnh xuất phát
            to_province: Tỉnh đến
            road_type: Loại đường
            road_name: Tên đường (optional)
            
        Returns:
            RoadSegment object
        """
        distance = self.estimate_road_distance(
            from_province,
            to_province,
            road_type
        )
        
        return RoadSegment(
            from_province=from_province,
            to_province=to_province,
            distance_km=distance,
            road_type=road_type,
            road_name=road_name
        )
    



class DistanceCache:

    def __init__(self):
        self._cache: Dict[Tuple[str, str, RoadType], float] = {}
    
    def get(
        self,
        code1: str,
        code2: str,
        road_type: RoadType = RoadType.UNKNOWN
    ) -> Optional[float]:
        """Lấy khoảng cách từ cache"""
        # Try both directions
        key1 = (code1, code2, road_type)
        key2 = (code2, code1, road_type)
        
        return self._cache.get(key1) or self._cache.get(key2)
    
    def set(
        self,
        code1: str,
        code2: str,
        distance: float,
        road_type: RoadType = RoadType.UNKNOWN
    ) -> None:
        """Lưu khoảng cách vào cache"""
        key = (code1, code2, road_type)
        self._cache[key] = distance
    
    def clear(self) -> None:
        """Xóa cache"""
        self._cache.clear()
    
    def size(self) -> int:
        """Số lượng entry trong cache"""
        return len(self._cache)
