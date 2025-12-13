from typing import Dict, List, Optional, Set

from models.province import Province
from models.exceptions import GraphNotBuiltError


class ProvinceGraph:
    """
    Đồ thị các tỉnh thành Việt Nam.
    
    Sử dụng adjacency list để lưu trữ quan hệ kề giữa các tỉnh.
    Mỗi tỉnh là một đỉnh, mỗi cạnh thể hiện 2 tỉnh giáp nhau.
    """

    def __init__(self) -> None:
        # Danh sách kề: {mã_tỉnh: [danh_sách_mã_tỉnh_kề]}
        self._adjacency_list: Dict[str, List[str]] = {}
        # Lưu thông tin tỉnh: {mã_tỉnh: Province}
        self._provinces: Dict[str, Province] = {}
        # Đánh dấu đồ thị đã được xây dựng xong chưa
        self._is_built: bool = False
    
    def add_province(self, province: Province) -> None:
        """Thêm một tỉnh (đỉnh) vào đồ thị"""
        if province.code in self._provinces:
            raise ValueError(
                f"Province with code {province.code} already exists"
            )
        
        self._provinces[province.code] = province
        if province.code not in self._adjacency_list:
            self._adjacency_list[province.code] = []
    
    def add_edge(self, code1: str, code2: str) -> None:
        """Thêm cạnh (quan hệ giáp ranh) giữa 2 tỉnh - cạnh vô hướng"""
        if code1 not in self._provinces:
            raise ValueError(f"Province {code1} not found in graph")
        if code2 not in self._provinces:
            raise ValueError(f"Province {code2} not found in graph")
        
        if code2 not in self._adjacency_list[code1]:
            self._adjacency_list[code1].append(code2)
        if code1 not in self._adjacency_list[code2]:
            self._adjacency_list[code2].append(code1)
    
    def get_neighbors(self, code: str) -> List[str]:
        """Lấy danh sách mã các tỉnh kề với tỉnh có mã code"""
        if not self._is_built:
            raise GraphNotBuiltError()
        
        if code not in self._adjacency_list:
            raise ValueError(f"Province {code} not found in graph")
        
        return self._adjacency_list[code].copy()
    
    def get_province(self, code: str) -> Optional[Province]:
        return self._provinces.get(code)
    
    def has_province(self, code: str) -> bool:
        """Kiểm tra tỉnh có trong đồ thị không"""
        return code in self._provinces
    
    def mark_as_built(self) -> None:
        self._is_built = True
    
    def is_built(self) -> bool:
        return self._is_built
    
    def get_edge_count(self) -> int:
        """Đếm số cạnh (chia 2 vì mỗi cạnh được lưu 2 lần trong adjacency list)"""
        total = sum(len(neighbors) for neighbors in self._adjacency_list.values())
        return total // 2

