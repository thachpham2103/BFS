"""Thuật toán tìm đường đi bằng BFS cho ứng dụng Tìm khoảng cách.
Độ phức tạp thời gian: O(V + E) với V = số đỉnh, E = số cạnh
Độ phức tạp bộ nhớ: O(V)
"""

import time
from collections import deque
from typing import Dict, List, Optional, Set

from graph.province_graph import ProvinceGraph
from models.province import Province
from models.path_result import PathResult
from models.exceptions import GraphNotBuiltError, NoPathFoundError


class BFSPathfinder:

    def __init__(self, graph: ProvinceGraph) -> None:
        if not graph.is_built():
            raise GraphNotBuiltError()
        
        self.graph = graph
    
    def find_path(
        self,
        start_code: str,
        end_code: str
    ) -> PathResult:
        """Tìm đường đi ngắn nhất (theo số cạnh) giữa hai tỉnh.

        Args:
            start_code: Mã tỉnh bắt đầu.
            end_code: Mã tỉnh kết thúc.

        Returns:
            PathResult: Kết quả bao gồm danh sách tỉnh trên đường đi,
                        tỉnh bắt đầu, tỉnh kết thúc và thời gian thực thi.
        """
        start_time = time.perf_counter()
        
        start_province = self.graph.get_province(start_code)
        if not start_province:
            raise ValueError(f"Tỉnh bắt đầu {start_code} không có trong đồ thị")
        
        end_province = self.graph.get_province(end_code)
        if not end_province:
            raise ValueError(f"Tỉnh kết thúc {end_code} không có trong đồ thị")
        
        if start_code == end_code:
            execution_time = time.perf_counter() - start_time
            return PathResult(
                path=[start_province],
                start=start_province,
                end=end_province,
                execution_time=execution_time
            )
        
        path = self._bfs(start_code, end_code)
        
        if not path:
            raise NoPathFoundError(
                start=start_province.name,
                end=end_province.name,
                reason="Hai tỉnh không liên thông với nhau"
            )
        
        province_path = [
            self.graph.get_province(code) for code in path
        ]
        
        execution_time = time.perf_counter() - start_time
        
        return PathResult(
            path=province_path,
            start=start_province,
            end=end_province,
            execution_time=execution_time
        )
    
    def _bfs(self, start: str, end: str) -> Optional[List[str]]:
        queue: deque = deque([start])
        visited: Set[str] = {start}
        parent: Dict[str, Optional[str]] = {start: None}
        
        while queue:
            current = queue.popleft()

            if current == end:
                return self._reconstruct_path(parent, start, end)
            
            for neighbor in self.graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        return None
    
    def _reconstruct_path(
        self,
        parent: Dict[str, Optional[str]],
        start: str,
        end: str
    ) -> List[str]:

        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        return path
    
    def find_all_paths_from(
        self,
        start_code: str,
        max_distance: Optional[int] = None
    ) -> Dict[str, int]:

        if not self.graph.has_province(start_code):
            raise ValueError(f"Tỉnh {start_code} không có trong đồ thị")
        
        queue: deque = deque([(start_code, 0)])
        visited: Set[str] = {start_code}
        distances: Dict[str, int] = {start_code: 0}
        
        while queue:
            current, distance = queue.popleft()
            
            if max_distance and distance >= max_distance:
                continue
            
            for neighbor in self.graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_distance = distance + 1
                    distances[neighbor] = new_distance
                    queue.append((neighbor, new_distance))
        
        return distances
    
    def is_connected(self, code1: str, code2: str) -> bool:

        if not self.graph.has_province(code1):
            raise ValueError(f"Tỉnh {code1} không có trong đồ thị")
        if not self.graph.has_province(code2):
            raise ValueError(f"Tỉnh {code2} không có trong đồ thị")
        
        if code1 == code2:
            return True
        
        visited: Set[str] = {code1}
        queue: deque = deque([code1])
        
        while queue:
            current = queue.popleft()
            
            if current == code2:
                return True
            
            for neighbor in self.graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return False
    
    def get_graph_stats(self) -> Dict:
        return self.graph.get_stats()
    
    def __repr__(self) -> str:
        return f"BFSPathfinder(graph={self.graph})"