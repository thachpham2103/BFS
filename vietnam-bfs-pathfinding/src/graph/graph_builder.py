from graph.province_graph import ProvinceGraph
from models.province import Province, ProvinceRegistry


class GraphBuilder:
    """
    Xây dựng đồ thị ProvinceGraph từ ProvinceRegistry.
    
    Quy trình:
    1. Thêm tất cả các tỉnh làm đỉnh
    2. Thêm các cạnh dựa trên quan hệ neighbors của mỗi tỉnh
    """

    @staticmethod
    def build_from_registry(registry: ProvinceRegistry) -> ProvinceGraph:
        """Xây dựng đồ thị từ registry chứa thông tin các tỉnh"""
        if not registry.is_initialized():
            raise RuntimeError("ProvinceRegistry not initialized")
        
        graph = ProvinceGraph()
        
        # Bước 1: Thêm tất cả tỉnh làm đỉnh
        for province in registry.get_all():
            graph.add_province(province)

        # Bước 2: Thêm các cạnh (tránh trùng lặp bằng set)
        added_edges = set()
        
        for province in registry.get_all():
            for neighbor_code in province.neighbors:
                # Tạo key duy nhất cho cạnh (sắp xếp để A-B và B-A có cùng key)
                edge_key = tuple(sorted([province.code, neighbor_code]))
                
                if edge_key not in added_edges:
                    graph.add_edge(province.code, neighbor_code)
                    added_edges.add(edge_key)
        
        graph.mark_as_built()
        
        return graph
