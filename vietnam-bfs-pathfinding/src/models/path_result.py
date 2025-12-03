from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from models.province import Province


@dataclass
class PathStep:

    from_province: Province
    to_province: Province
    step_number: int
    
    def __post_init__(self) -> None:
        if self.step_number < 1:
            raise ValueError("Step number must be >= 1")
    
    def to_dict(self) -> Dict:
        return {
            "step_number": self.step_number,
            "from": {
                "code": self.from_province.code,
                "name": self.from_province.name
            },
            "to": {
                "code": self.to_province.code,
                "name": self.to_province.name
            }
        }
    
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
        return {
            "path": [p.name for p in self.path],
            "path_codes": [p.code for p in self.path],
            "distance": self.distance,
            "start_province": {
                "code": self.start.code,
                "name": self.start.name,
                "full_name": self.start.full_name
            },
            "end_province": {
                "code": self.end.code,
                "name": self.end.name,
                "full_name": self.end.full_name
            },
            "execution_time_ms": self.execution_time * 1000,
            "timestamp": self.timestamp.isoformat()
        }
    
    def get_summary(self) -> str:
        summary = f"Đường đi từ {self.start.name} đến {self.end.name}:\n"
        summary += " → ".join(self.province_names)
        summary += f"\n\nTổng số tỉnh: {self.distance}"
        summary += f"\nThời gian tìm kiếm: {self.execution_time * 1000:.2f}ms"
        return summary
    
    def visualize(self, numbered: bool = True) -> str:
        lines = []
        lines.append(f"Đường đi từ {self.start.name} đến {self.end.name}")
        lines.append("=" * 60)
        
        for i, province in enumerate(self.path, 1):
            if numbered:
                lines.append(f"{i:2d}. {province.name}")
            else:
                arrow = "   → " if i > 1 else "   "
                lines.append(f"{arrow}{province.name}")
        
        lines.append("=" * 60)
        lines.append(f"Tổng số tỉnh: {self.distance}")
        lines.append(f"Thời gian: {self.execution_time * 1000:.2f}ms")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return f"Path from {self.start.name} to {self.end.name} ({self.distance} provinces)"
    
    def __repr__(self) -> str:
        return (
            f"PathResult(start={self.start.code}, end={self.end.code}, "
            f"distance={self.distance}, time={self.execution_time:.4f}s)"
        )
