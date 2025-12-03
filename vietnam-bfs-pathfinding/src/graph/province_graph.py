from typing import Dict, List, Optional, Set

from models.province import Province
from models.exceptions import GraphNotBuiltError


class ProvinceGraph:

    def __init__(self) -> None:
        self._adjacency_list: Dict[str, List[str]] = {}
        self._provinces: Dict[str, Province] = {}
        self._is_built: bool = False
    
    def add_province(self, province: Province) -> None:

        if province.code in self._provinces:
            raise ValueError(
                f"Province with code {province.code} already exists"
            )
        
        self._provinces[province.code] = province
        if province.code not in self._adjacency_list:
            self._adjacency_list[province.code] = []
    
    def add_edge(self, code1: str, code2: str) -> None:
        if code1 not in self._provinces:
            raise ValueError(f"Province {code1} not found in graph")
        if code2 not in self._provinces:
            raise ValueError(f"Province {code2} not found in graph")
        
        if code2 not in self._adjacency_list[code1]:
            self._adjacency_list[code1].append(code2)
        if code1 not in self._adjacency_list[code2]:
            self._adjacency_list[code2].append(code1)
    
    def get_neighbors(self, code: str) -> List[str]:

        if not self._is_built:
            raise GraphNotBuiltError()
        
        if code not in self._adjacency_list:
            raise ValueError(f"Province {code} not found in graph")
        
        return self._adjacency_list[code].copy()
    
    def get_province(self, code: str) -> Optional[Province]:
        return self._provinces.get(code)
    
    def has_province(self, code: str) -> bool:
        return code in self._provinces
    
    def mark_as_built(self) -> None:
        self._is_built = True
    
    def is_built(self) -> bool:
        return self._is_built
    
    def get_province_count(self) -> int:
        return len(self._provinces)
    
    def get_edge_count(self) -> int:
        total = sum(len(neighbors) for neighbors in self._adjacency_list.values())
        return total // 2
    
    def get_all_provinces(self) -> List[Province]:
        return list(self._provinces.values())
    
    def validate_connectivity(self) -> Dict[str, bool]:
        if not self._provinces:
            return {
                "is_connected": False,
                "reason": "Graph is empty"
            }
        
        start_code = next(iter(self._provinces.keys()))
        visited: Set[str] = set()
        queue: List[str] = [start_code]
        visited.add(start_code)
        
        while queue:
            current = queue.pop(0)
            for neighbor in self._adjacency_list.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        is_connected = len(visited) == len(self._provinces)
        
        return {
            "is_connected": is_connected,
            "visited_count": len(visited),
            "total_count": len(self._provinces),
            "unreachable": (
                list(set(self._provinces.keys()) - visited)
                if not is_connected else []
            )
        }
    
    def get_stats(self) -> Dict:
        if not self._provinces:
            return {
                "province_count": 0,
                "edge_count": 0,
                "is_built": self._is_built
            }
        
        neighbor_counts = [
            len(neighbors) for neighbors in self._adjacency_list.values()
        ]
        
        return {
            "province_count": len(self._provinces),
            "edge_count": self.get_edge_count(),
            "is_built": self._is_built,
            "avg_neighbors": sum(neighbor_counts) / len(neighbor_counts),
            "min_neighbors": min(neighbor_counts),
            "max_neighbors": max(neighbor_counts)
        }
    
    def __repr__(self) -> str:
        return (
            f"ProvinceGraph(provinces={len(self._provinces)}, "
            f"edges={self.get_edge_count()}, built={self._is_built})"
        )
