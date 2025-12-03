import json
import os
from typing import Dict, List, Optional
from threading import Lock


class DataLoader:
    _instance: Optional['DataLoader'] = None
    _lock: Lock = Lock()
    
    def __new__(cls) -> 'DataLoader':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._provinces = None
                    cls._instance._adjacency = None
                    cls._instance._data_loaded = False
        return cls._instance
    
    def __init__(self) -> None:
        pass
    
    def load_data(
        self,
        provinces_path: str,
        adjacency_path: str,
        force_reload: bool = False
    ) -> None:
        if self._data_loaded and not force_reload:
            return
        
        with self._lock:
            if self._data_loaded and not force_reload:
                return
            
            if not os.path.exists(provinces_path):
                raise FileNotFoundError(
                    f"Provinces file not found: {provinces_path}"
                )
            
            with open(provinces_path, 'r', encoding='utf-8') as f:
                self._provinces = json.load(f)
            
            # Load adjacency
            if not os.path.exists(adjacency_path):
                raise FileNotFoundError(
                    f"Adjacency file not found: {adjacency_path}"
                )
            
            with open(adjacency_path, 'r', encoding='utf-8') as f:
                self._adjacency = json.load(f)
            
            # Validate data
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
                raise ValueError(
                    f"Invalid province code in adjacency data: {code}"
                )
        
        for code, neighbors in self._adjacency.items():
            for neighbor in neighbors:
                if neighbor not in province_codes:
                    raise ValueError(
                        f"Invalid neighbor code {neighbor} for province {code}"
                    )
    
    def get_provinces(self) -> List[Dict]:

        if not self._data_loaded:
            raise RuntimeError(
                "Data not loaded. Call load_data() first."
            )
        return self._provinces.copy()
    
    def get_adjacency(self) -> Dict[str, List[str]]:

        if not self._data_loaded:
            raise RuntimeError(
                "Data not loaded. Call load_data() first."
            )
        return self._adjacency.copy()
    
    def get_province_by_code(self, code: str) -> Optional[Dict]:

        if not self._data_loaded:
            raise RuntimeError(
                "Data not loaded. Call load_data() first."
            )
        
        for province in self._provinces:
            if province["code"] == code:
                return province.copy()
        return None
    
    def get_neighbors(self, province_code: str) -> List[str]:

        if not self._data_loaded:
            raise RuntimeError(
                "Data not loaded. Call load_data() first."
            )
        
        if province_code not in self._adjacency:
            raise KeyError(f"Province code not found: {province_code}")
        
        return self._adjacency[province_code].copy()
    
    def is_loaded(self) -> bool:

        return self._data_loaded
    
    def get_stats(self) -> Dict:

        if not self._data_loaded:
            raise RuntimeError(
                "Data not loaded. Call load_data() first."
            )
        
        return {
            "total_provinces": len(self._provinces),
            "total_adjacency_entries": len(self._adjacency),
            "data_loaded": self._data_loaded
        }
