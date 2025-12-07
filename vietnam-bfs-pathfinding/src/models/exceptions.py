from typing import List, Optional


class ProvinceNotFoundError(Exception):

    def __init__(
        self,
        province_name: str,
        suggestions: Optional[List[str]] = None
    ) -> None:
        self.province_name = province_name
        self.suggestions = suggestions or []
        
        msg = f"Không tìm thấy tỉnh '{province_name}' trong hệ thống"
        if self.suggestions:
            msg += f". Gợi ý: {', '.join(self.suggestions)}"
        
        self.message = msg
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return self.message


class NoPathFoundError(Exception):
    def __init__(
        self,
        start: str,
        end: str,
        reason: Optional[str] = None
    ) -> None:
        self.start = start
        self.end = end
        self.reason = reason
        
        msg = f"Không tìm thấy đường đi từ '{start}' đến '{end}'"
        if reason:
            msg += f". Lý do: {reason}"
        
        self.message = msg
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return self.message


class InvalidInputError(Exception):
    def __init__(
        self,
        field: str,
        message: str,
        value: Optional[str] = None
    ) -> None:
        self.field = field
        self.value = value
        
        msg = f"Dữ liệu không hợp lệ ở trường '{field}': {message}"
        if value:
            msg += f" (giá trị: '{value}')"
        
        self.message = msg
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return self.message


class GraphNotBuiltError(Exception):
    
    def __init__(self, message: Optional[str] = None) -> None:

        self.message = message or (
            "Đồ thị chưa được xây dựng. "
            "Vui lòng gọi build_graph() trước khi sử dụng."
        )
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return self.message
