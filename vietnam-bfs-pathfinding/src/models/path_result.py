from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING

from models.province import Province

if TYPE_CHECKING:
    from models.road_segment import RoadSegment


@dataclass
class PathStep:

    from_province: Province
    to_province: Province
    step_number: int
    distance_km: Optional[float] = None
    road_type: Optional[str] = None
    road_name: Optional[str] = None
    
    def __post_init__(self) -> None:
        if self.step_number < 1:
            raise ValueError("Step number must be >= 1")
    
    def to_dict(self) -> Dict:
        result = {
            "step_number": self.step_number,
            "from": {
                "code": self.from_province.code,
                "name": self.from_province.name,
                "coordinates": {
                    "latitude": self.from_province.latitude,
                    "longitude": self.from_province.longitude
                }
            },
            "to": {
                "code": self.to_province.code,
                "name": self.to_province.name,
                "coordinates": {
                    "latitude": self.to_province.latitude,
                    "longitude": self.to_province.longitude
                }
            }
        }
        
        if self.distance_km is not None:
            result["distance_km"] = round(self.distance_km, 2)
        if self.road_type:
            result["road_type"] = self.road_type
        if self.road_name:
            result["road_name"] = self.road_name
            
        return result
    
    def __str__(self) -> str:
        return (
            f"Step {self.step_number}: "
            f"{self.from_province.name} → {self.to_province.name}"
        )


@dataclass
class PathResult:
    path: List[Province]
    start: Province
    end: Province
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    road_segments: List['RoadSegment'] = field(default_factory=list)
    total_distance_km: float = 0.0
    road_type: Optional[str] = None
    # Khoảng cách thực tế theo đường đi (từ OSRM API)
    real_distance_km: Optional[float] = None
    
    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("Path cannot be empty")
        
        if self.path[0] != self.start:
            raise ValueError("First province in path must be start province")
        
        if self.path[-1] != self.end:
            raise ValueError("Last province in path must be end province")
        
        if self.execution_time < 0:
            raise ValueError("Execution time cannot be negative")
    
    @property
    def distance(self) -> int:

        return len(self.path)
    
    @property
    def province_names(self) -> List[str]:
        return [p.name for p in self.path]
    
    @property
    def province_codes(self) -> List[str]:

        return [p.code for p in self.path]
    
    def get_steps(self) -> List[PathStep]:
        steps = []
        for i in range(len(self.path) - 1):
            step = PathStep(
                from_province=self.path[i],
                to_province=self.path[i + 1],
                step_number=i + 1
            )
            steps.append(step)
        return steps
    
    def to_dict(self) -> Dict:
        result = {
            "path": [p.name for p in self.path],
            "path_codes": [p.code for p in self.path],
            "path_coordinates": [
                {
                    "code": p.code,
                    "name": p.name,
                    "latitude": p.latitude,
                    "longitude": p.longitude
                }
                for p in self.path
            ],
            "distance": self.distance,
            "total_distance_km": round(self.total_distance_km, 2),
            "road_type": self.road_type,
            "start_province": {
                "code": self.start.code,
                "name": self.start.name,
                "full_name": self.start.full_name,
                "coordinates": {
                    "latitude": self.start.latitude,
                    "longitude": self.start.longitude
                }
            },
            "end_province": {
                "code": self.end.code,
                "name": self.end.name,
                "full_name": self.end.full_name,
                "coordinates": {
                    "latitude": self.end.latitude,
                    "longitude": self.end.longitude
                }
            },
            "execution_time_ms": self.execution_time * 1000,
            "timestamp": self.timestamp.isoformat()
        }
        
        # Thêm thông tin khoảng cách thực tế nếu có
        if self.real_distance_km is not None:
            result["real_distance_km"] = round(self.real_distance_km, 2)
        
        return result
    
