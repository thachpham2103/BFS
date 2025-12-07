import logging
from typing import Dict, List, Optional, Union

from algorithms.bfs import BFSPathfinder
from graph.graph_builder import GraphBuilder
from graph.province_graph import ProvinceGraph
from models.province import Province, ProvinceRegistry
from models.path_result import PathResult
from models.exceptions import (
    ProvinceNotFoundError,
    NoPathFoundError,
    InvalidInputError,
    GraphNotBuiltError
)

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
        
        logger.info(
            f"PathfindingService initialized with {self.registry.count()} provinces"
        )
    
    def find_path(
        self,
        start: Union[str, Province],
        end: Union[str, Province],
        fuzzy_match: bool = True
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
            f"{end_province.name} ({end_province.code})"
        )
        
        try:
            result = self.pathfinder.find_path(
                start_province.code,
                end_province.code
            )
            
            logger.info(
                f"Path found: {result.distance} provinces, "
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
    
    def get_reachable_provinces(
        self,
        start: Union[str, Province],
        max_distance: Optional[int] = None
    ) -> Dict[str, Dict]:
        start_province = self._resolve_province(start, fuzzy_match=True, field_name="start")
        
        logger.info(
            f"Finding reachable provinces from {start_province.name} "
            f"(max_distance: {max_distance})"
        )
        
        distances = self.pathfinder.find_all_paths_from(
            start_province.code,
            max_distance
        )
        
        result = {}
        for code, distance in distances.items():
            province = self.registry.get_by_code(code)
            if province:
                result[code] = {
                    "code": code,
                    "name": province.name,
                    "full_name": province.full_name,
                    "distance": distance
                }
        
        logger.info(f"Found {len(result)} reachable provinces")
        
        return result
    
    def check_connectivity(
        self,
        province1: Union[str, Province],
        province2: Union[str, Province]
    ) -> bool:
        p1 = self._resolve_province(province1, fuzzy_match=True, field_name="province1")
        p2 = self._resolve_province(province2, fuzzy_match=True, field_name="province2")
        
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
