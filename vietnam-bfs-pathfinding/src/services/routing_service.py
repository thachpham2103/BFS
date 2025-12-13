"""
Tính khoảng cách đường đi thực tế sử dụng OSRM API

OSRM (Open Source Routing Machine) là dịch vụ routing miễn phí
sử dụng dữ liệu OpenStreetMap, cho kết quả chính xác như Google Maps.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

import httpx

from models.province import Province

logger = logging.getLogger(__name__)


@dataclass
class RouteResult:
    """Kết quả tính toán đường đi thực tế"""
    distance_km: float
    success: bool = True
    error_message: Optional[str] = None


class RoutingService:
    """
    Service tính khoảng cách đường đi thực tế sử dụng OSRM API
    
    OSRM Public Server: https://router.project-osrm.org
    - Miễn phí, không cần API key
    - Sử dụng dữ liệu OpenStreetMap
    """
    
    OSRM_BASE_URL = "https://router.project-osrm.org"
    REQUEST_TIMEOUT = 30.0
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or self.OSRM_BASE_URL
    
    def get_route_distance(
        self,
        start_province: Province,
        end_province: Province
    ) -> RouteResult:
        """Tính khoảng cách đường đi thực tế giữa 2 tỉnh"""
        if not all([
            start_province.latitude, start_province.longitude,
            end_province.latitude, end_province.longitude
        ]):
            return RouteResult(
                distance_km=0.0,
                success=False,
                error_message="Thiếu tọa độ"
            )
        
        try:
            coordinates = (
                f"{start_province.longitude},{start_province.latitude};"
                f"{end_province.longitude},{end_province.latitude}"
            )
            
            url = f"{self.base_url}/route/v1/driving/{coordinates}"
            params = {"overview": "false", "steps": "false"}
            
            with httpx.Client(timeout=self.REQUEST_TIMEOUT) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data.get("code") != "Ok" or not data.get("routes"):
                return RouteResult(
                    distance_km=0.0,
                    success=False,
                    error_message="Không tìm thấy đường đi"
                )
            
            route = data["routes"][0]
            return RouteResult(
                distance_km=route.get("distance", 0) / 1000.0,
                success=True
            )
            
        except Exception as e:
            logger.error(f"OSRM error: {e}")
            return RouteResult(
                distance_km=0.0,
                success=False,
                error_message=str(e)
            )
    
    def get_route_through_waypoints(
        self,
        provinces: List[Province]
    ) -> RouteResult:
        """Tính khoảng cách qua nhiều tỉnh (waypoints)"""
        if len(provinces) < 2:
            return RouteResult(
                distance_km=0.0,
                success=False,
                error_message="Cần ít nhất 2 tỉnh"
            )
        
        for p in provinces:
            if not p.latitude or not p.longitude:
                return RouteResult(
                    distance_km=0.0,
                    success=False,
                    error_message=f"Thiếu tọa độ cho tỉnh {p.name}"
                )
        
        try:
            coords_list = [f"{p.longitude},{p.latitude}" for p in provinces]
            coordinates = ";".join(coords_list)
            
            url = f"{self.base_url}/route/v1/driving/{coordinates}"
            params = {"overview": "false", "steps": "false"}
            
            with httpx.Client(timeout=self.REQUEST_TIMEOUT) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data.get("code") != "Ok" or not data.get("routes"):
                return RouteResult(
                    distance_km=0.0,
                    success=False,
                    error_message="Không tìm thấy đường đi"
                )
            
            route = data["routes"][0]
            distance_km = route.get("distance", 0) / 1000.0
            return RouteResult(
                distance_km,
                success=True
            )
            
        except Exception as e:
            logger.error(f"OSRM error: {e}")
            return RouteResult(
                distance_km=0.0,
                success=False,
                error_message=str(e)
            )
