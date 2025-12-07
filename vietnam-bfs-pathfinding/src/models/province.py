import re
import unicodedata
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional


def normalize_text(text: str) -> str:
    text = unicodedata.normalize('NFD', text)
    text = ''.join(
        char for char in text
        if unicodedata.category(char) != 'Mn'
    )
    return text.lower().strip()


@dataclass(frozen=True)
class Province:

    code: str
    name: str
    full_name: str
    code_name: str
    name_en: str = ""
    full_name_en: str = ""
    neighbors: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        if not re.match(r'^\d{2}$', self.code):
            raise ValueError(f"Invalid province code format: {self.code}")
        
        if not self.name.strip():
            raise ValueError("Province name cannot be empty")
        
        if not self.full_name.strip():
            raise ValueError("Province full_name cannot be empty")
    
    @property
    def neighbor_count(self) -> int:
        return len(self.neighbors)
    
    @property
    def normalized_name(self) -> str:
        return normalize_text(self.name)
    
    @property
    def normalized_full_name(self) -> str:
        return normalize_text(self.full_name)
    
    def to_dict(self) -> Dict:
        return {
            "code": self.code,
            "name": self.name,
            "full_name": self.full_name,
            "code_name": self.code_name,
            "name_en": self.name_en,
            "full_name_en": self.full_name_en,
            "neighbors": list(self.neighbors),
            "neighbor_count": self.neighbor_count
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Province':
        return Province(
            code=data["code"],
            name=data["name"],
            full_name=data["full_name"],
            code_name=data["code_name"],
            name_en=data.get("name_en", ""),
            full_name_en=data.get("full_name_en", ""),
            neighbors=data.get("neighbors", [])
        )
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
    
    def __repr__(self) -> str:
        return (
            f"Province(code='{self.code}', name='{self.name}', "
            f"neighbors={self.neighbor_count})"
        )


class ProvinceRegistry:

    _instance: Optional['ProvinceRegistry'] = None
    _lock: Lock = Lock()
    
    def __new__(cls) -> 'ProvinceRegistry':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._provinces = {}
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        pass
    
    def initialize(
        self,
        provinces_data: List[Dict],
        adjacency_data: Dict[str, List[str]]
    ) -> None:
        if self._initialized:
            raise ValueError("ProvinceRegistry already initialized")
        
        with self._lock:
            if self._initialized:
                raise ValueError("ProvinceRegistry already initialized")
            
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
                self._provinces[code] = province
            
            self._initialized = True
    
    def get_by_code(self, code: str) -> Optional[Province]:
        if not self._initialized:
            raise RuntimeError("ProvinceRegistry not initialized")
        
        if code.isdigit():
            code = code.zfill(2)
        
        return self._provinces.get(code)
    
    def get_by_name(self, name: str, fuzzy: bool = True) -> Optional[Province]:
        if not self._initialized:
            raise RuntimeError("ProvinceRegistry not initialized")
        
        normalized_query = normalize_text(name)
        
        for province in self._provinces.values():
            if (province.normalized_name == normalized_query or
                province.normalized_full_name == normalized_query):
                return province
        
        if fuzzy:
            for province in self._provinces.values():
                if (normalized_query in province.normalized_name or
                    normalized_query in province.normalized_full_name):
                    return province
        
        return None
    
    def get_all(self) -> List[Province]:
        if not self._initialized:
            raise RuntimeError("ProvinceRegistry not initialized")
        return list(self._provinces.values())
    
    def search(
        self,
        query: str,
        limit: Optional[int] = None
    ) -> List[Province]:
        if not self._initialized:
            raise RuntimeError("ProvinceRegistry not initialized")
        
        normalized_query = normalize_text(query)
        results = []
        
        for province in self._provinces.values():
            if (normalized_query in province.normalized_name or
                normalized_query in province.normalized_full_name):
                results.append(province)
                if limit and len(results) >= limit:
                    break
        
        return results
    
    def is_initialized(self) -> bool:
        return self._initialized
    
    def count(self) -> int:
        if not self._initialized:
            raise RuntimeError("ProvinceRegistry not initialized")
        return len(self._provinces)
    
    def reset(self) -> None:
        with self._lock:
            self._provinces.clear()
            self._initialized = False
