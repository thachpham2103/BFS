"""
Tính khoảng cách đường đi thực tế sử dụng OpenRouteService API

OpenRouteService (ORS) là dịch vụ routing miễn phí
sử dụng dữ liệu OpenStreetMap, cho kết quả chính xác.

OSRM (Open Source Routing Machine) là dịch vụ routing miễn phí
sử dụng dữ liệu OpenStreetMap, cho kết quả chính xác như Google Maps.
"""

import logging
import time
from typing import List, Optional
from dataclasses import dataclass

import httpx

from models.province import Province
from config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class RouteResult:
    """Kết quả tính toán đường đi thực tế"""
    distance_km: float
    success: bool = True
    error_message: Optional[str] = None


class RoutingService:
    """
    Service tính khoảng cách đường đi thực tế sử dụng OpenRouteService API
    
    OpenRouteService: https://openrouteservice.org
    - Free tier: 2,000 requests/ngày
    - Sử dụng dữ liệu OpenStreetMap
    - Cần API key (miễn phí)
    """
    
    ORS_BASE_URL = "https://api.openrouteservice.org/v2"
    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 2
    RETRY_DELAY = 1.0
    
    DEFAULT_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImEzYjgwZmQwYmQxMjRkM2VhMjVmNzFkMmZiZWE2YTVjIiwiaCI6Im11cm11cjY0In0="
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self.DEFAULT_API_KEY
        self.base_url = self.ORS_BASE_URL
    
    def _get_headers(self) -> dict:
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_route_distance(
        self,
        start_province: Province,
        end_province: Province
    ) -> RouteResult:
        return self.get_route_through_waypoints([start_province, end_province])
    
    def get_route_through_waypoints(
        self,
        provinces: List[Province]
    ) -> RouteResult:
        """Tính khoảng cách qua nhiều tỉnh (waypoints)
        
        Sử dụng OpenRouteService Directions API
        Docs: https://openrouteservice.org/dev/#/api-docs/v2/directions
        """
        if not self.api_key:
            return RouteResult(
                distance_km=0.0,
                success=False,
                error_message="API key không được cấu hình"
            )
        
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
        
        coordinates = [[p.longitude, p.latitude] for p in provinces]
        
        url = f"{self.base_url}/directions/driving-car"
        payload = {
            "coordinates": coordinates,
            "instructions": False,
            "geometry": False
        }
        
        last_error = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                if attempt > 0:
                    logger.info(f"ORS retry attempt {attempt}/{self.MAX_RETRIES}")
                    time.sleep(self.RETRY_DELAY)
                
                with httpx.Client(timeout=self.REQUEST_TIMEOUT) as client:
                    response = client.post(
                        url,
                        headers=self._get_headers(),
                        json=payload
                    )
                    
                    # Xử lý lỗi HTTP
                    if response.status_code == 401:
                        return RouteResult(
                            distance_km=0.0,
                            success=False,
                            error_message="API key không hợp lệ"
                        )
                    elif response.status_code == 403:
                        return RouteResult(
                            distance_km=0.0,
                            success=False,
                            error_message="API key hết quota hoặc bị chặn"
                        )
                    elif response.status_code == 404:
                        return RouteResult(
                            distance_km=0.0,
                            success=False,
                            error_message="Không tìm thấy đường đi"
                        )
                    
                    response.raise_for_status()
                    data = response.json()
                
                if "routes" not in data or not data["routes"]:
                    return RouteResult(
                        distance_km=0.0,
                        success=False,
                        error_message="Không tìm thấy đường đi"
                    )
                
                route = data["routes"][0]
                summary = route.get("summary", {})
                
                distance_km = summary.get("distance", 0) / 1000.0
                
                logger.info(
                    f"ORS route found: {distance_km:.2f}km "
                    f"({len(provinces)} waypoints)"
                )
                
                return RouteResult(
                    distance_km=round(distance_km, 2),
                    success=True
                )
                
            except httpx.TimeoutException as e:
                last_error = f"Request timeout sau {self.REQUEST_TIMEOUT}s"
                logger.warning(f"ORS timeout (attempt {attempt + 1}): {e}")
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP error: {e.response.status_code}"
                logger.error(f"ORS HTTP error (attempt {attempt + 1}): {e}")
                break
            except Exception as e:
                last_error = str(e)
                logger.error(f"ORS error (attempt {attempt + 1}): {e}")
                break
        
        return RouteResult(
            distance_km=0.0,
            success=False,
            error_message=last_error
        )
