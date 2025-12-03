from typing import Dict, List

from graph.province_graph import ProvinceGraph
from models.province import Province, ProvinceRegistry


class GraphBuilder:

    @staticmethod
    def build_from_registry(registry: ProvinceRegistry) -> ProvinceGraph:
        if not registry.is_initialized():
            raise RuntimeError("ProvinceRegistry not initialized")
        
        graph = ProvinceGraph()
        
        for province in registry.get_all():
            graph.add_province(province)

        added_edges = set()
        
        for province in registry.get_all():
            for neighbor_code in province.neighbors:
                edge_key = tuple(sorted([province.code, neighbor_code]))
                
                if edge_key not in added_edges:
                    graph.add_edge(province.code, neighbor_code)
                    added_edges.add(edge_key)
        
        graph.mark_as_built()
        
        return graph
    
    @staticmethod
    def build_from_data(
        provinces_data: List[Dict],
        adjacency_data: Dict[str, List[str]]
    ) -> ProvinceGraph:
        graph = ProvinceGraph()
        
        for prov_data in provinces_data:
            code = prov_data["code"]
            neighbors = adjacency_data.get(code, [])
            
            province = Province(
                code=code,
                name=prov_data["name"],
                full_name=prov_data["full_name"],
                code_name=prov_data["code_name"],
                name_en=prov_data.get("name_en", ""),
                full_name_en=prov_data.get("full_name_en", ""),
                neighbors=neighbors
            )
            graph.add_province(province)
        
        added_edges = set()
        
        for code, neighbors in adjacency_data.items():
            if not graph.has_province(code):
                raise ValueError(f"Province {code} in adjacency but not in provinces")
            
            for neighbor_code in neighbors:
                if not graph.has_province(neighbor_code):
                    raise ValueError(
                        f"Neighbor {neighbor_code} not found in provinces"
                    )
                
                edge_key = tuple(sorted([code, neighbor_code]))
                
                if edge_key not in added_edges:
                    graph.add_edge(code, neighbor_code)
                    added_edges.add(edge_key)
        
        graph.mark_as_built()
        
        return graph
    
    @staticmethod
    def validate_graph(graph: ProvinceGraph) -> Dict:
        results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not graph.is_built():
            results["is_valid"] = False
            results["errors"].append("Graph not marked as built")
            return results
        
        if graph.get_province_count() == 0:
            results["is_valid"] = False
            results["errors"].append("Graph is empty")
            return results
        
        connectivity = graph.validate_connectivity()
        if not connectivity["is_connected"]:
            results["warnings"].append(
                f"Graph not fully connected: "
                f"{connectivity['visited_count']}/{connectivity['total_count']} "
                f"provinces reachable"
            )
            results["warnings"].append(
                f"Unreachable provinces: {connectivity['unreachable']}"
            )
        
        for province in graph.get_all_provinces():
            neighbors = graph.get_neighbors(province.code)
            if len(neighbors) == 0:
                results["warnings"].append(
                    f"Province {province.name} ({province.code}) has no neighbors"
                )
        
        return results
