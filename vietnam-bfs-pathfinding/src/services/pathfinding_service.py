import logging
from typing import Dict, List, Optional, Union

from algorithms.bfs import BFSPathfinder
from graph.graph_builder import GraphBuilder
from graph.province_graph import ProvinceGraph
from models.province import Province, ProvinceRegistry
from models.path_result import PathResult
from models.road_segment import RoadSegment, RoadType
from models.exceptions import (
    ProvinceNotFoundError,
    NoPathFoundError,
    InvalidInputError,
    GraphNotBuiltError
)
from services.distance_service import DistanceCalculator
from services.routing_service import RoutingService

logger = logging.getLogger(__name__)


class PathfindingService:

    def __init__(
        self,
        registry: ProvinceRegistry,
        graph: Optional[ProvinceGraph] = None
    ) -> None:

        if not registry.is_initialized():
            raise RuntimeError("ProvinceRegistry must be initialized")
        
        self.registry = registry
        
        if graph is None:
            logger.info("Building graph from registry")
            self.graph = GraphBuilder.build_from_registry(registry)
        else:
            if not graph.is_built():
                raise GraphNotBuiltError()
            self.graph = graph
        
        self.pathfinder = BFSPathfinder(self.graph)
        self.distance_calculator = DistanceCalculator()
        self.routing_service = RoutingService()
        
        logger.info(
            f"PathfindingService initialized with {self.registry.count()} provinces"
        )
    
    def find_path(
        self,
        start: Union[str, Province],
        end: Union[str, Province],
        fuzzy_match: bool = True,
        road_type: str = "national"
    ) -> PathResult:

        if not start or not end:
            raise InvalidInputError(
                "start/end",
                "Điểm bắt đầu và điểm kết thúc không được để trống"
            )
        
        start_province = self._resolve_province(start, fuzzy_match, "start")
        end_province = self._resolve_province(end, fuzzy_match, "end")
        
        logger.info(
            f"Finding path: {start_province.name} ({start_province.code}) -> "
            f"{end_province.name} ({end_province.code}), road_type={road_type}"
        )
        
        try:
            result = self.pathfinder.find_path(
                start_province.code,
                end_province.code
            )
            
            try:
                road_type_enum = RoadType(road_type.lower())
            except ValueError:
                logger.warning(f"Invalid road_type: {road_type}, using NATIONAL")
                road_type_enum = RoadType.NATIONAL
            
            road_segments = []
            total_distance = 0.0
            
            for i in range(len(result.path) - 1):
                from_prov = result.path[i]
                to_prov = result.path[i + 1]
                
                try:
                    segment = self.distance_calculator.create_road_segment(
                        from_prov,
                        to_prov,
                        road_type_enum
                    )
                    road_segments.append(segment)
                    total_distance += segment.distance_km
                    
                    logger.debug(
                        f"Segment {i+1}: {from_prov.name} -> {to_prov.name}, "
                        f"{segment.distance_km:.2f}km"
                    )
                except ValueError as e:
                    logger.warning(f"Could not calculate distance: {e}")
            
            result.road_segments = road_segments
            result.total_distance_km = total_distance
            result.road_type = road_type
            
            # Tính khoảng cách thực tế bằng OSRM API
            try:
                route_result = self.routing_service.get_route_through_waypoints(
                    result.path
                )
                if route_result.success:
                    result.real_distance_km = route_result.distance_km
                    logger.info(
                        f"Real distance (OSRM): {route_result.distance_km:.2f}km"
                    )
                else:
                    logger.warning(
                        f"Could not get real distance: {route_result.error_message}"
                    )
            except Exception as e:
                logger.warning(f"Error getting real distance from OSRM: {e}")
            
            logger.info(
                f"Path found: {result.distance} provinces, "
                f"{total_distance:.2f}km, "
                f"{result.execution_time * 1000:.2f}ms"
            )
            
            return result
            
        except NoPathFoundError as e:
            logger.warning(f"No path found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            raise
    
    def _resolve_province(
        self,
        identifier: Union[str, Province],
        fuzzy_match: bool,
        field_name: str
    ) -> Province:
        if isinstance(identifier, Province):
            return identifier
        
        if not isinstance(identifier, str):
            raise InvalidInputError(
                field_name,
                "Mã hoặc tên tỉnh phải là chuỗi ký tự",
                str(identifier)
            )
        
        identifier = identifier.strip()
        
        if not identifier:
            raise InvalidInputError(
                field_name,
                "Mã hoặc tên tỉnh không được để trống"
            )
        
        province = self.registry.get_by_code(identifier)
        if province:
            return province
        
        province = self.registry.get_by_name(identifier, fuzzy=fuzzy_match)
        if province:
            return province
        
        suggestions = self._get_suggestions(identifier)
        raise ProvinceNotFoundError(identifier, suggestions)
    
    def _get_suggestions(self, query: str, limit: int = 5) -> List[str]:

        results = self.registry.search(query, limit=limit)
        return [p.name for p in results]
    
    def find_multiple_paths(
        self,
        pairs: List[tuple]
    ) -> List[PathResult]:
        results = []
        
        for start, end in pairs:
            try:
                result = self.find_path(start, end)
                results.append(result)
            except (ProvinceNotFoundError, NoPathFoundError) as e:
                logger.warning(f"Failed to find path {start}->{end}: {e}")
                continue
        
        return results

    def find_reachable(
        self,
        start: Union[str, Province],
        max_distance: Optional[int] = None,
        fuzzy_match: bool = True
    ) -> Dict[str, tuple]:
        """Tìm tất cả các tỉnh có thể đến được từ tỉnh bắt đầu.
        
        Args:
            start: Tỉnh bắt đầu (mã, tên hoặc đối tượng Province)
            max_distance: Khoảng cách tối đa (số bước). None = không giới hạn
            fuzzy_match: Cho phép tìm kiếm gần đúng tên tỉnh
            
        Returns:
            Dict với key là mã tỉnh, value là tuple (Province, distance)
        """
        start_province = self._resolve_province(start, fuzzy_match, field_name="start")
        
        logger.info(
            f"Finding reachable provinces from {start_province.name} "
            f"(max_distance: {max_distance})"
        )
        
        distances = self.pathfinder.find_all_paths_from(
            start_province.code,
            max_distance=max_distance
        )
        
        results = {}
        for code, distance in distances.items():
            province = self.registry.get_by_code(code)
            if province:
                results[code] = (province, distance)
        
        logger.info(f"Found {len(results)} reachable provinces")
        return results

    def check_connectivity(
        self,
        province1: Union[str, Province],
        province2: Union[str, Province],
        fuzzy_match: bool = True
    ) -> bool:

        p1 = self._resolve_province(province1, fuzzy_match=fuzzy_match, field_name="province1")
        p2 = self._resolve_province(province2, fuzzy_match=fuzzy_match, field_name="province2")
        
        return self.pathfinder.is_connected(p1.code, p2.code)
    
    def get_province_info(
        self,
        identifier: Union[str, Province]
    ) -> Dict:
        province = self._resolve_province(
            identifier,
            fuzzy_match=True,
            field_name="province"
        )
        
        neighbor_codes = self.graph.get_neighbors(province.code)
        neighbors = []
        for code in neighbor_codes:
            neighbor = self.registry.get_by_code(code)
            if neighbor:
                neighbors.append({
                    "code": neighbor.code,
                    "name": neighbor.name
                })
        
        return {
            "code": province.code,
            "name": province.name,
            "full_name": province.full_name,
            "code_name": province.code_name,
            "neighbor_count": len(neighbors),
            "neighbors": neighbors
        }
    
    def get_all_provinces(self) -> List[Dict]:
        provinces = self.registry.get_all()
        
        return [
            {
                "code": p.code,
                "name": p.name,
                "full_name": p.full_name,
                "code_name": p.code_name,
                "neighbor_count": p.neighbor_count
            }
            for p in sorted(provinces, key=lambda x: x.code)
        ]
    
    def __repr__(self) -> str:
        return (
            f"PathfindingService("
            f"provinces={self.registry.count()}, "
            f"graph={self.graph})"
        )
