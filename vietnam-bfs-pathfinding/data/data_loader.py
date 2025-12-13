import json
import os
from typing import Dict, List


class DataLoader:
    """Load dữ liệu từ 2 file json"""
    
    def __init__(self) -> None:
        self._provinces = None
        self._adjacency = None
        self._data_loaded = False
    
    def load_data(
        self,
        provinces_path: str,
        adjacency_path: str
    ) -> None:
        if not os.path.exists(provinces_path):
            raise FileNotFoundError(f"Provinces file not found: {provinces_path}")
        
        with open(provinces_path, 'r', encoding='utf-8') as f:
            self._provinces = json.load(f)
        
        if not os.path.exists(adjacency_path):
            raise FileNotFoundError(f"Adjacency file not found: {adjacency_path}")
        
        with open(adjacency_path, 'r', encoding='utf-8') as f:
            self._adjacency = json.load(f)
        
        self._validate_data()
        self._data_loaded = True
    
    def _validate_data(self) -> None:
        if not self._provinces:
            raise ValueError("Provinces data is empty")
        
        if not self._adjacency:
            raise ValueError("Adjacency data is empty")
        
        province_codes = {p["code"] for p in self._provinces}
        
        for code in self._adjacency.keys():
            if code not in province_codes:
                raise ValueError(f"Invalid province code in adjacency data: {code}")
        
        for code, neighbors in self._adjacency.items():
            for neighbor in neighbors:
                if neighbor not in province_codes:
                    raise ValueError(f"Invalid neighbor code {neighbor} for province {code}")
    
    def get_provinces(self) -> List[Dict]:
        if not self._data_loaded:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        return self._provinces.copy()
    
    def get_adjacency(self) -> Dict[str, List[str]]:
        if not self._data_loaded:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        return self._adjacency.copy()

    def get_stats(self) -> Dict:
        if not self._data_loaded:
            raise RuntimeError("Data not loaded. Call load_data() first.")
        
        return {
            "total_provinces": len(self._provinces),
            "total_adjacency_entries": len(self._adjacency),
            "data_loaded": self._data_loaded
        }
