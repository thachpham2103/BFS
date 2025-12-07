# KẾ HOẠCH TRIỂN KHAI DỰ ÁN FINDING DISTANCE
## Tìm đường đi ngắn nhất giữa các tỉnh thành Việt Nam sử dụng thuật toán BFS

---

## 📋 TỔNG QUAN DỰ ÁN

### Mục tiêu
Xây dựng ứng dụng tìm đường đi ngắn nhất giữa 2 tỉnh thành bất kỳ ở Việt Nam sử dụng thuật toán BFS (Breadth-First Search).

### Công nghệ
- **Ngôn ngữ**: Python 3.8+
- **Thuật toán**: BFS (Breadth-First Search)
- **Dữ liệu**: Vietnamese Provinces Database
- **Framework**: FastAPI (cho REST API)
- **Testing**: pytest, unittest (phat trien sau)
- **Documentation**: Swagger/OpenAPI

### Cấu trúc thư mục dự kiến
```
finding-distance/
├── README.md
├── require.md
├── plan.md (file này)
├── requirements.txt
├── .gitignore
├── .env.example
├── config/
│   └── settings.py
├── data/
│   ├── provinces.json
│   ├── adjacency.json
│   └── data_loader.py
├── src/
│   ├── __init__.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── graph_builder.py
│   │   └── province_graph.py
│   ├── algorithms/
│   │   ├── __init__.py
│   │   └── bfs.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── province.py
│   │   └── path_result.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── pathfinding_service.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       └── formatters.py
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── pathfinding.py
│   └── schemas/
│       ├── __init__.py
│       ├── request.py
│       └── response.py
├── tests/
│   ├── __init__.py
│   ├── test_bfs.py
│   ├── test_graph.py
│   ├── test_api.py
│   └── test_data/
│       └── sample_graph.json
├── scripts/
│   ├── create_adjacency_data.py
│   └── verify_data.py
├── cli/
│   └── main.py
└── docs/
    ├── api.md
    ├── algorithm.md
    └── deployment.md
```

---

## 🎯 CHUẨN MỰC VÀ QUY TẮC CODE

### 1. Code Quality Standards

#### Python Code Style
- **PEP 8**: Tuân thủ 100% PEP 8 guidelines
- **Line length**: Tối đa 100 ký tự/dòng
- **Naming conventions**:
  - Classes: `PascalCase` (VD: `ProvinceGraph`, `PathResult`)
  - Functions/Methods: `snake_case` (VD: `find_shortest_path`, `build_graph`)
  - Constants: `UPPER_SNAKE_CASE` (VD: `MAX_PROVINCES`, `DEFAULT_TIMEOUT`)
  - Private members: prefix `_` (VD: `_internal_method`)
- **Type Hints**: Bắt buộc cho tất cả functions/methods
  ```python
  def find_path(start: str, end: str) -> Optional[List[str]]:
      pass
  ```

#### Documentation Standards
- **Module docstring**: Mô tả mục đích, author, date
- **Class docstring**: Mô tả class, attributes, examples
- **Function docstring**: Google style
  ```python
  def find_shortest_path(start: str, end: str) -> PathResult:
      """Tìm đường đi ngắn nhất giữa 2 tỉnh.
      
      Args:
          start (str): Tên tỉnh xuất phát
          end (str): Tên tỉnh đích
          
      Returns:
          PathResult: Kết quả chứa đường đi và thông tin
          
      Raises:
          ProvinceNotFoundError: Khi tỉnh không tồn tại
          NoPathFoundError: Khi không tìm thấy đường đi
          
      Examples:
          >>> result = find_shortest_path("Hà Nội", "TP. Hồ Chí Minh")
          >>> print(result.path)
          ['Hà Nội', 'Hòa Bình', ..., 'TP. Hồ Chí Minh']
      """
      pass
  ```

#### Error Handling Rules
- **Custom Exceptions**: Tạo exception classes riêng
- **Never silent fail**: Luôn log errors
- **Graceful degradation**: Xử lý lỗi một cách an toàn
- **User-friendly messages**: Thông báo lỗi rõ ràng, tiếng Việt có dấu

#### Testing Standards
- **Coverage**: Minimum 85% code coverage
- **Test types**:
  - Unit tests: Test từng function/class riêng lẻ
  - Integration tests: Test tương tác giữa components
  - API tests: Test endpoints
- **Test naming**: `test_<function>_<scenario>_<expected_result>`
  ```python
  def test_bfs_valid_path_returns_shortest_route():
      pass
  
  def test_bfs_no_path_raises_exception():
      pass
  ```

### 2. API Standards

#### Request Format
```json
{
  "start_province": "Hà Nội",
  "end_province": "Thành phố Hồ Chí Minh",
  "options": {
    "include_distance": true,
    "include_coordinates": false
  }
}
```

#### Response Format - Success
```json
{
  "status": "success",
  "data": {
    "path": ["Hà Nội", "Hòa Bình", "Thanh Hóa", ...],
    "distance": 18,
    "start_province": {
      "code": "01",
      "name": "Hà Nội",
      "full_name": "Thành phố Hà Nội"
    },
    "end_province": {
      "code": "79",
      "name": "Thành phố Hồ Chí Minh",
      "full_name": "Thành phố Hồ Chí Minh"
    },
    "execution_time_ms": 15.4
  },
  "message": "Đã tìm thấy đường đi ngắn nhất",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Response Format - Error
```json
{
  "status": "error",
  "error": {
    "code": "PROVINCE_NOT_FOUND",
    "message": "Không tìm thấy tỉnh 'Hà Nội2' trong hệ thống",
    "details": {
      "provided_name": "Hà Nội2",
      "suggestions": ["Hà Nội", "Hà Nam", "Hà Giang"]
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Error Codes
- `PROVINCE_NOT_FOUND`: Tỉnh không tồn tại
- `NO_PATH_FOUND`: Không tìm thấy đường đi
- `INVALID_INPUT`: Dữ liệu đầu vào không hợp lệ
- `SAME_PROVINCE`: Tỉnh xuất phát và đích trùng nhau
- `INTERNAL_ERROR`: Lỗi hệ thống

#### HTTP Status Codes
- `200 OK`: Thành công
- `400 Bad Request`: Lỗi input từ client
- `404 Not Found`: Không tìm thấy resource
- `500 Internal Server Error`: Lỗi server

### 3. Data Standards

#### Province Data Model
```python
@dataclass
class Province:
    code: str           # "01"
    name: str           # "Hà Nội"
    full_name: str      # "Thành phố Hà Nội"
    code_name: str      # "ha_noi"
    neighbors: List[str] # ["02", "05", "06"]
```

#### Graph Representation
- **Adjacency List**: `Dict[str, List[str]]`
- **Key**: Province code hoặc name (chuẩn hóa)
- **Value**: List các tỉnh lân cận

---

## 📝 KẾ HOẠCH TRIỂN KHAI CHI TIẾT

---

## BƯỚC 1: THIẾT LẬP MÔI TRƯỜNG VÀ KHỞI TẠO DỰ ÁN

### Mục tiêu
Khởi tạo cấu trúc project, cài đặt dependencies, thiết lập môi trường phát triển.

### Prompt thực hiện

```
Bạn là một Python Senior Engineer. Nhiệm vụ của bạn là thiết lập môi trường dự án Finding Distance.

YÊU CẦU:
1. Tạo file requirements.txt với các thư viện:
   - fastapi==0.104.1
   - uvicorn[standard]==0.24.0
   - pydantic==2.5.0
   - pytest==7.4.3
   - pytest-cov==4.1.0
   - python-dotenv==1.0.0
   - aiofiles==23.2.1

2. Tạo file .gitignore cho Python project:
   - Bao gồm: __pycache__, *.pyc, .env, venv/, .pytest_cache/, .coverage
   - Thêm: .vscode/, .idea/, *.log

3. Tạo file .env.example với:
   - DEBUG=True
   - LOG_LEVEL=INFO
   - API_HOST=0.0.0.0
   - API_PORT=8000

4. Tạo file config/settings.py:
   - Load environment variables
   - Định nghĩa cấu hình: DEBUG, LOG_LEVEL, API settings
   - Sử dụng pydantic BaseSettings
   - Type hints đầy đủ

CHUẨN MỰC:
- Tuân thủ PEP 8
- Type hints cho tất cả variables và functions
- Docstrings đầy đủ
- Comments giải thích các config quan trọng

OUTPUT:
- Tạo các file: requirements.txt, .gitignore, .env.example, config/settings.py
```

### Checklist hoàn thành
- [ ] File requirements.txt được tạo với đầy đủ dependencies
- [ ] File .gitignore bao gồm tất cả patterns cần thiết
- [ ] File .env.example có tất cả config variables
- [ ] config/settings.py hoạt động và load được env vars
- [ ] Chạy `pip install -r requirements.txt` thành công
- [ ] Không có lỗi khi import settings

---

## BƯỚC 2: TẠO DỮ LIỆU TỈNH LÂN CẬN (ADJACENCY DATA)

### Mục tiêu
Xây dựng dữ liệu về các tỉnh giáp ranh nhau từ nguồn vietnamese-provinces-database.

### Prompt thực hiện

```
Bạn là một Data Engineer chuyên xử lý dữ liệu địa lý Việt Nam.

BỐI CẢNH:
- Dữ liệu từ vietnamese-provinces-database chỉ có danh sách 63 tỉnh thành
- Cần tạo dữ liệu về các tỉnh giáp ranh (adjacency data) để xây dựng graph
- Dữ liệu adjacency phải chính xác về mặt địa lý

NHIỆM VỤ:
1. Nghiên cứu và tạo file data/adjacency.json với cấu trúc:
   {
     "01": ["02", "05", "06", "11", "12", "13"],  // Hà Nội giáp với...
     "02": ["01", "03", "04"],                    // Hà Giang giáp với...
     ...
   }

2. Tạo script scripts/create_adjacency_data.py:
   - Function để validate adjacency data (kiểm tra tính đối xứng: nếu A giáp B thì B phải giáp A)
   - Function để load provinces từ vietnamese-provinces-database
   - Function để merge dữ liệu
   - Xử lý trường hợp đặc biệt (hải đảo, vùng không liên tục)

3. Tạo file data/data_loader.py:
   - Class DataLoader để load provinces và adjacency data
   - Cache data sau khi load lần đầu
   - Validate data integrity
   - Handle exceptions gracefully

NGUỒN DỮ LIỆU ADJACENCY (Tra cứu từ bản đồ Việt Nam):
Bạn cần research và điền chính xác dựa trên bản đồ hành chính Việt Nam.
Một số ví dụ:
- Hà Nội (01) giáp: Vĩnh Phúc (26), Bắc Ninh (27), Hưng Yên (33), Hà Nam (35), Hòa Bình (17)
- Hồ Chí Minh (79) giáp: Bình Dương (74), Đồng Nai (75), Long An (80), Tây Ninh (72)
- (Cần hoàn thiện tất cả 63 tỉnh)

CHUẨN MỰC:
- Dữ liệu phải chính xác 100% với thực tế địa lý
- Code phải validate tính đối xứng của adjacency
- Sử dụng province code (01, 02...) làm key
- Type hints đầy đủ
- Unit tests cho validation logic
- Comments giải thích nguồn dữ liệu

YÊU CẦU ĐẶC BIỆT:
- Xử lý trường hợp tỉnh không có đường bộ liên tục (VD: Côn Đảo thuộc Bà Rịa - Vũng Tàu)
- Document các trường hợp đặc biệt
- Provide function để query: "Tỉnh X giáp với những tỉnh nào?"

OUTPUT:
- data/adjacency.json (dữ liệu đầy đủ 63 tỉnh)
- data/provinces.json (copy từ vietnamese-provinces-database, simplified)
- data/data_loader.py (module load và validate data)
- scripts/create_adjacency_data.py (script tạo và validate)
- tests/test_data/sample_adjacency.json (data cho testing)
```

### Checklist hoàn thành
- [ ] File adjacency.json có đầy đủ 63 tỉnh
- [ ] Dữ liệu adjacency chính xác với bản đồ Việt Nam
- [ ] Validation script chạy thành công, không có lỗi đối xứng
- [ ] DataLoader load được data và cache đúng
- [ ] Unit tests pass với coverage > 85%
- [ ] Document các trường hợp đặc biệt

---

## BƯỚC 3: XÂY DỰNG MODELS VÀ DATA STRUCTURES

### Mục tiêu
Tạo các data models để represent provinces, paths, và graph structure.

### Prompt thực hiện

```
Bạn là một Python Software Architect chuyên về data modeling.

NHIỆM VỤ:
Tạo các model classes trong src/models/ với yêu cầu sau:

1. File src/models/province.py:
   - Class Province:
     * Attributes: code, name, full_name, code_name, neighbors
     * Method: to_dict(), from_dict(data)
     * Property: neighbor_count
     * Validation: code format (2 digits), name không empty
   
   - Class ProvinceRegistry:
     * Singleton pattern
     * Store all provinces
     * Methods: get_by_code(), get_by_name(), get_all(), search()
     * Support fuzzy search (tìm "ha noi" -> "Hà Nội")

2. File src/models/path_result.py:
   - Class PathResult:
     * Attributes: path (List[Province]), distance, execution_time, start, end
     * Method: to_dict(), get_summary(), visualize()
     * Property: province_names (List[str])
   
   - Class PathStep:
     * Represent một bước trong path
     * Attributes: from_province, to_province, step_number

3. File src/models/exceptions.py:
   - Custom exceptions:
     * ProvinceNotFoundError(province_name, suggestions)
     * NoPathFoundError(start, end, reason)
     * InvalidInputError(field, message)
     * GraphNotBuiltError()

CHUẨN MỰC:
- Sử dụng @dataclass hoặc Pydantic BaseModel
- Type hints đầy đủ cho tất cả attributes và methods
- Validation logic trong __post_init__ hoặc validators
- Immutable khi có thể (frozen=True cho dataclass)
- Rich comparison methods (__eq__, __hash__) khi cần
- __repr__ và __str__ clear và useful
- Docstrings đầy đủ theo Google style
- Unit tests đầy đủ cho mỗi class

YÊU CẦU ĐẶC BIỆT:
- Province name normalization (lowercase, no diacritics) cho search
- PathResult phải serialize được thành JSON
- Custom exceptions phải có helpful error messages tiếng Việt
- ProvinceRegistry phải thread-safe

TESTING REQUIREMENTS:
- Test valid và invalid data
- Test edge cases (empty, None, special characters)
- Test serialization/deserialization
- Test singleton behavior của ProvinceRegistry

OUTPUT:
- src/models/__init__.py
- src/models/province.py
- src/models/path_result.py
- src/models/exceptions.py
- tests/test_models.py (comprehensive tests)
```

### Checklist hoàn thành
- [ ] Province class đầy đủ attributes và methods
- [ ] ProvinceRegistry implement singleton đúng
- [ ] PathResult có thể serialize thành JSON
- [ ] Custom exceptions với messages rõ ràng
- [ ] Fuzzy search hoạt động tốt
- [ ] All tests pass với coverage > 90%
- [ ] Type hints đầy đủ, mypy check pass

---

## BƯỚC 4: TRIỂN KHAI THUẬT TOÁN BFS

### Mục tiêu
Implement thuật toán BFS để tìm đường đi ngắn nhất giữa 2 tỉnh.

### Prompt thực hiện

```
Bạn là một Algorithm Engineer chuyên về Graph Theory và thuật toán tìm kiếm.

BỐI CẢNH:
- Cần implement BFS (Breadth-First Search) để tìm shortest path
- Graph là undirected (vô hướng)
- Graph là unweighted (không trọng số)
- Đảm bảo BFS tìm được đường đi ngắn nhất (số tỉnh ít nhất)

NHIỆM VỤ:

1. File src/algorithms/bfs.py - Class BFSPathfinder:
   
   Method: find_shortest_path(start: Province, end: Province) -> PathResult
   - Input: 2 Province objects
   - Output: PathResult object
   - Algorithm: Standard BFS với queue
   - Tracking: parent dictionary để reconstruct path
   - Optimization: Early termination khi tìm thấy đích
   
   Method: find_all_paths(start: Province, max_distance: int) -> Dict[Province, PathResult]
   - Tìm tất cả đường đi từ start trong vòng max_distance bước
   - Useful cho visualization và analysis
   
   Method: get_statistics() -> Dict
   - Nodes visited, queue size max, execution time
   - Useful cho performance analysis

2. Pseudo-code BFS cần implement:
   ```
   function BFS(start, end):
       queue = [start]
       visited = {start}
       parent = {start: None}
       
       while queue not empty:
           current = queue.dequeue()
           
           if current == end:
               return reconstruct_path(parent, start, end)
           
           for neighbor in current.neighbors:
               if neighbor not in visited:
                   visited.add(neighbor)
                   parent[neighbor] = current
                   queue.enqueue(neighbor)
       
       raise NoPathFoundError()
   ```

3. File src/graph/province_graph.py - Class ProvinceGraph:
   - Build graph từ adjacency data
   - Store graph as adjacency list
   - Methods: get_neighbors(province), get_degree(province)
   - Validate graph connectivity
   - Detect disconnected components

4. File src/graph/graph_builder.py - Class GraphBuilder:
   - Factory pattern để build graph
   - Load data từ DataLoader
   - Validate data integrity
   - Build ProvinceGraph object

CHUẨN MỰC:
- Time complexity: O(V + E) where V=vertices, E=edges
- Space complexity: O(V) for visited set and queue
- Code phải clean, readable, well-commented
- Type hints đầy đủ
- Docstrings chi tiết với complexity analysis
- Handle all edge cases:
  * start == end (return immediate)
  * start or end không tồn tại (raise exception)
  * No path exists (raise NoPathFoundError)
  * Empty graph (raise GraphNotBuiltError)

YÊU CẦU TESTING:
- Test với graph nhỏ (3-5 nodes) - verify correctness
- Test với graph thật (63 provinces) - verify performance
- Test edge cases: same start/end, no path, invalid input
- Test performance: không quá 100ms cho bất kỳ query nào
- Benchmark với different graph sizes

PERFORMANCE REQUIREMENTS:
- Find path giữa 2 tỉnh bất kỳ: < 50ms
- Build graph từ data: < 200ms
- Memory usage: < 50MB

OUTPUT:
- src/algorithms/__init__.py
- src/algorithms/bfs.py (BFSPathfinder class)
- src/graph/__init__.py
- src/graph/province_graph.py
- src/graph/graph_builder.py
- tests/test_bfs.py (comprehensive BFS tests)
- tests/test_graph.py (graph building and validation tests)
- docs/algorithm.md (document thuật toán, complexity analysis)
```

### Checklist hoàn thành
- [ ] BFS implementation chính xác, tìm được shortest path
- [ ] Xử lý đúng tất cả edge cases
- [ ] Performance đạt yêu cầu (< 50ms)
- [ ] Graph builder hoạt động đúng
- [ ] Tests pass với coverage > 90%
- [ ] Algorithm documentation đầy đủ
- [ ] Memory usage trong giới hạn

---

## BƯỚC 5: XÂY DỰNG SERVICE LAYER

### Mục tiêu
Tạo service layer để orchestrate business logic, kết nối giữa API và algorithms.

### Prompt thực hiện

```
Bạn là một Backend Engineer chuyên về Service-Oriented Architecture.

NHIỆM VỤ:
Xây dựng service layer trong src/services/ để xử lý business logic.

1. File src/services/pathfinding_service.py - Class PathfindingService:

   Method: find_path(start_name: str, end_name: str, options: Dict) -> PathResult
   - Normalize input (loại bỏ dấu, lowercase)
   - Lookup provinces từ ProvinceRegistry
   - Gọi BFSPathfinder
   - Format result theo options
   - Log execution time và statistics
   - Handle exceptions gracefully
   
   Method: get_province_info(province_name: str) -> Province
   - Search và return province info
   - Suggest similar names nếu không tìm thấy
   
   Method: get_all_provinces() -> List[Province]
   - Return danh sách tất cả provinces
   - Optional: sort, filter, pagination
   
   Method: validate_provinces(start: str, end: str) -> Tuple[Province, Province]
   - Validate cả 2 provinces exist
   - Return Province objects
   - Raise exceptions with helpful messages

2. File src/utils/validators.py - Validation utilities:
   - Function: normalize_province_name(name: str) -> str
   - Function: is_valid_province_code(code: str) -> bool
   - Function: validate_options(options: Dict) -> Dict
   - Function: sanitize_input(text: str) -> str

3. File src/utils/formatters.py - Formatting utilities:
   - Function: format_path_result(result: PathResult, options: Dict) -> Dict
   - Function: format_error(exception: Exception) -> Dict
   - Function: format_province_list(provinces: List[Province]) -> List[Dict]

CHUẨN MỰC:
- Single Responsibility Principle: Mỗi method làm 1 việc
- Dependency Injection: Inject dependencies vào constructor
- Error handling: Try-catch với logging
- Validation: Validate inputs trước khi xử lý
- Logging: Log INFO cho success, ERROR cho failures
- Type hints và docstrings đầy đủ

BUSINESS RULES:
1. Province name matching:
   - Case-insensitive
   - Ignore diacritics (Hà Nội = ha noi = Ha Noi)
   - Support both short name và full name
   - Fuzzy matching với threshold 0.8

2. Options handling:
   - include_distance: boolean (default True)
   - include_coordinates: boolean (default False)
   - include_execution_time: boolean (default True)
   - max_results: int (default unlimited)

3. Error messages:
   - Tiếng Việt có dấu
   - Clear và actionable
   - Include suggestions when possible

LOGGING REQUIREMENTS:
- Log level INFO: Successful operations
- Log level WARNING: Invalid input, suggestions used
- Log level ERROR: Exceptions, failures
- Include: timestamp, operation, input, output, duration

TESTING REQUIREMENTS:
- Unit tests: Mock dependencies (graph, registry)
- Integration tests: Real data, end-to-end
- Test validation logic thoroughly
- Test error handling và logging
- Test performance: service calls < 100ms

OUTPUT:
- src/services/__init__.py
- src/services/pathfinding_service.py
- src/utils/__init__.py
- src/utils/validators.py
- src/utils/formatters.py
- tests/test_service.py
- tests/test_validators.py
- tests/test_formatters.py
```

### Checklist hoàn thành
- [ ] PathfindingService implement đầy đủ methods
- [ ] Validation logic hoạt động đúng
- [ ] Normalization và fuzzy matching chính xác
- [ ] Error handling và logging đầy đủ
- [ ] Formatters output đúng format
- [ ] Tests pass với coverage > 85%
- [ ] Integration tests thành công

---

## BƯỚC 6: XÂY DỰNG REST API VỚI FASTAPI

### Mục tiêu
Tạo REST API endpoints để expose pathfinding service qua HTTP.

### Prompt thực hiện

```
Bạn là một API Developer chuyên về FastAPI và RESTful design.

NHIỆM VỤ:
Xây dựng REST API với FastAPI trong thư mục api/.

1. File api/main.py - FastAPI application:
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   
   app = FastAPI(
       title="Finding Distance API",
       description="Tìm đường đi ngắn nhất giữa các tỉnh thành Việt Nam",
       version="1.0.0"
   )
   
   # CORS middleware
   # Exception handlers
   # Startup/shutdown events
   # Include routers
   ```

2. File api/schemas/request.py - Request schemas:
   - PathfindingRequest:
     * start_province: str (required, min_length=2)
     * end_province: str (required, min_length=2)
     * options: Optional[PathfindingOptions]
   
   - PathfindingOptions:
     * include_distance: bool = True
     * include_coordinates: bool = False
     * include_execution_time: bool = True

3. File api/schemas/response.py - Response schemas:
   - PathfindingResponse:
     * status: Literal["success", "error"]
     * data: Optional[PathData]
     * error: Optional[ErrorData]
     * timestamp: datetime
   
   - PathData:
     * path: List[str]
     * distance: int
     * start_province: ProvinceInfo
     * end_province: ProvinceInfo
     * execution_time_ms: float
   
   - ErrorData:
     * code: str
     * message: str
     * details: Optional[Dict]

4. File api/routes/pathfinding.py - Route handlers:
   
   POST /api/v1/path/find
   - Body: PathfindingRequest
   - Response: PathfindingResponse
   - Gọi PathfindingService.find_path()
   
   GET /api/v1/provinces
   - Query params: search, limit, offset
   - Response: List[ProvinceInfo]
   - Gọi PathfindingService.get_all_provinces()
   
   GET /api/v1/provinces/{province_code}
   - Path param: province_code
   - Response: ProvinceInfo with neighbors
   
   GET /api/v1/health
   - Health check endpoint
   - Return: status, version, uptime

API DESIGN PRINCIPLES:
- RESTful conventions
- Consistent naming: snake_case for JSON
- Versioning: /api/v1/
- Proper HTTP methods: GET for read, POST for operations
- HTTP status codes theo chuẩn
- Request validation với Pydantic
- Response models for documentation

ERROR HANDLING:
- HTTPException cho client errors (4xx)
- Custom exception handler cho app exceptions
- Validation errors: 422 Unprocessable Entity
- Not found errors: 404 Not Found
- Server errors: 500 Internal Server Error
- Consistent error response format

MIDDLEWARE:
- CORS: Allow frontend access
- Logging: Log all requests/responses
- Error handling: Catch và format exceptions
- Performance monitoring: Track response times

DOCUMENTATION:
- OpenAPI/Swagger auto-generated
- Clear descriptions cho mỗi endpoint
- Request/Response examples
- Error response examples

SECURITY:
- Input validation và sanitization
- Rate limiting (optional)
- CORS configuration
- No sensitive data in responses

TESTING:
- TestClient từ FastAPI
- Test all endpoints
- Test validation errors
- Test error handling
- Test CORS headers

PERFORMANCE:
- Response time < 100ms cho path finding
- < 50ms cho province lookup
- Async/await where beneficial

OUTPUT:
- api/__init__.py
- api/main.py
- api/schemas/__init__.py
- api/schemas/request.py
- api/schemas/response.py
- api/routes/__init__.py
- api/routes/pathfinding.py
- tests/test_api.py (API integration tests)
- docs/api.md (API documentation)
```

### Checklist hoàn thành
- [ ] FastAPI app chạy được với uvicorn
- [ ] Tất cả endpoints hoạt động đúng
- [ ] Request/response validation chính xác
- [ ] Error handling đầy đủ và consistent
- [ ] Swagger UI accessible và đầy đủ docs
- [ ] CORS configured đúng
- [ ] API tests pass với coverage > 85%
- [ ] Performance đáp ứng yêu cầu

---

## BƯỚC 7: XÂY DỰNG COMMAND LINE INTERFACE (CLI)

### Mục tiêu
Tạo CLI tool để sử dụng pathfinding từ terminal.

### Prompt thực hiện

```
Bạn là một CLI Developer chuyên về command-line tools và user experience.

NHIỆM VỤ:
Xây dựng CLI trong thư mục cli/.

1. File cli/main.py - CLI application với Click hoặc Typer:

   Command: find
   ```bash
   python -m cli.main find --start "Hà Nội" --end "TP. Hồ Chí Minh"
   ```
   - Options:
     * --start/-s: Tỉnh xuất phát (required)
     * --end/-e: Tỉnh đích (required)
     * --verbose/-v: Hiển thị chi tiết
     * --json: Output JSON format
   - Output: Pretty-print path với colors
   
   Command: list
   ```bash
   python -m cli.main list [--search "ha"] [--limit 10]
   ```
   - List all provinces hoặc search
   - Table format với: Code, Name, Full Name, Neighbors count
   
   Command: info
   ```bash
   python -m cli.main info --province "Hà Nội"
   ```
   - Show province details
   - List all neighbors
   
   Command: verify
   ```bash
   python -m cli.main verify
   ```
   - Verify data integrity
   - Check graph connectivity
   - Report statistics

2. CLI FEATURES:
   - Colorful output (sử dụng rich hoặc colorama)
   - Progress indicators cho long operations
   - Interactive mode với prompts
   - Auto-completion cho province names
   - Help messages rõ ràng

3. OUTPUT FORMATTING:
   
   Success output example:
   ```
   🗺️  TÌM ĐƯỜNG TỪ HÀ NỘI ĐẾN THÀNH PHỐ HỒ CHÍ MINH
   ══════════════════════════════════════════════════
   
   Đường đi ngắn nhất (18 tỉnh):
   
   1. Hà Nội
   2. Hòa Bình
   3. Thanh Hóa
   ...
   18. Thành phố Hồ Chí Minh
   
   ⏱️  Thời gian thực hiện: 15.4ms
   ✅  Hoàn thành
   ```
   
   Error output example:
   ```
   ❌ LỖI: Không tìm thấy tỉnh 'Ha Noi2'
   
   💡 Gợi ý:
      - Hà Nội
      - Hà Nam
      - Hà Giang
   ```

REQUIREMENTS:
- Library: Click hoặc Typer
- Colors: Rich library for rich text và tables
- Arguments validation
- Help text chi tiết cho mỗi command
- Exit codes: 0 success, 1 error

CLI DESIGN PRINCIPLES:
- UNIX philosophy: Do one thing well
- Intuitive naming
- Consistent flags
- Helpful error messages
- Non-interactive mode for scripting
- Interactive mode for users

TESTING:
- Use Click/Typer testing utilities
- Test all commands
- Test argument validation
- Test output formatting
- Mock service layer

DOCUMENTATION:
- README section for CLI usage
- Help text for each command
- Examples for common use cases

OUTPUT:
- cli/__init__.py
- cli/main.py
- cli/formatters.py (output formatting utilities)
- requirements.txt (thêm click/typer, rich)
- tests/test_cli.py
- docs/cli_usage.md
```

### Checklist hoàn thành
- [ ] CLI commands hoạt động đúng
- [ ] Help text rõ ràng và hữu ích
- [ ] Output formatting đẹp với colors
- [ ] Error messages clear và actionable
- [ ] All CLI tests pass
- [ ] Documentation đầy đủ

---

## BƯỚC 8: VIẾT TESTS VÀ ĐẠT CODE COVERAGE

### Mục tiêu
Đảm bảo code quality với comprehensive test suite và coverage > 85%.

### Prompt thực hiện

```
Bạn là một QA Engineer chuyên về Test-Driven Development và quality assurance.

NHIỆM VỤ:
Viết comprehensive test suite cho toàn bộ dự án.

1. TESTING STRUCTURE:
   tests/
   ├── __init__.py
   ├── conftest.py (pytest fixtures)
   ├── test_models.py
   ├── test_bfs.py
   ├── test_graph.py
   ├── test_service.py
   ├── test_validators.py
   ├── test_formatters.py
   ├── test_api.py
   ├── test_cli.py
   └── test_integration.py

2. File tests/conftest.py - Shared fixtures:
   - @pytest.fixture sample_provinces
   - @pytest.fixture sample_adjacency
   - @pytest.fixture sample_graph
   - @pytest.fixture pathfinding_service
   - @pytest.fixture test_client (FastAPI)

3. UNIT TESTS - Từng component riêng lẻ:
   
   tests/test_models.py:
   - Test Province creation và validation
   - Test ProvinceRegistry singleton
   - Test PathResult serialization
   - Test custom exceptions
   
   tests/test_bfs.py:
   - Test BFS với simple graphs
   - Test edge cases: same start/end, no path
   - Test performance với large graphs
   - Test correctness: verify shortest path
   
   tests/test_graph.py:
   - Test graph building từ adjacency data
   - Test graph validation
   - Test neighbor queries
   
   tests/test_service.py:
   - Test PathfindingService methods
   - Mock dependencies
   - Test error handling
   
   tests/test_validators.py:
   - Test normalization
   - Test validation logic
   - Test edge cases

4. INTEGRATION TESTS:
   
   tests/test_integration.py:
   - Test end-to-end flow: input -> output
   - Test với real data
   - Test API -> Service -> Algorithm -> Data
   - Không mock dependencies

5. API TESTS:
   
   tests/test_api.py:
   - Test all endpoints
   - Test request validation
   - Test response format
   - Test error responses
   - Test status codes

6. COVERAGE REQUIREMENTS:
   - Overall: > 85%
   - Critical paths (BFS, Service): > 95%
   - Models: > 90%
   - Utilities: > 80%
   
   Run coverage:
   ```bash
   pytest --cov=src --cov=api --cov-report=html --cov-report=term
   ```

7. TEST CATEGORIES:
   - Positive tests: Valid inputs, expected behavior
   - Negative tests: Invalid inputs, error handling
   - Edge cases: Empty, None, boundaries
   - Performance tests: Timing requirements
   - Integration tests: Component interaction

TESTING BEST PRACTICES:
- AAA pattern: Arrange, Act, Assert
- One assert per test (when possible)
- Clear test names: test_<what>_<condition>_<expected>
- Use parametrize for similar tests
- Mock external dependencies
- Don't test implementation details
- Test behavior, not code

FIXTURES DESIGN:
- Small, focused fixtures
- Reusable across tests
- Clear naming
- Proper scope (function, module, session)

ASSERTIONS:
- Use specific assertions: assertEqual, assertRaises
- Provide helpful messages
- Test both positive và negative cases

MOCKING:
- Mock external services
- Mock file I/O
- Mock time-dependent code
- Don't over-mock

PERFORMANCE TESTING:
```python
def test_bfs_performance_large_graph():
    start = time.time()
    result = pathfinder.find_path(start_province, end_province)
    duration = time.time() - start
    assert duration < 0.05  # < 50ms
```

OUTPUT:
- Đầy đủ test files theo structure trên
- pytest.ini configuration
- .coveragerc configuration
- tests/test_data/ với sample data
- Đạt coverage > 85%
- All tests pass
```

### Checklist hoàn thành
- [ ] All test files written
- [ ] Unit tests cover critical logic
- [ ] Integration tests pass
- [ ] API tests comprehensive
- [ ] Code coverage > 85%
- [ ] All tests pass
- [ ] No flaky tests
- [ ] Performance tests pass

---

## BƯỚC 9: DOCUMENTATION VÀ CODE QUALITY

### Mục tiêu
Viết documentation đầy đủ và đảm bảo code quality với linting tools.

### Prompt thực hiện

```
Bạn là một Technical Writer và Code Quality Expert.

NHIỆM VỤ:

1. DOCUMENTATION FILES:

   docs/api.md:
   - API endpoints documentation
   - Request/Response examples
   - Error codes và handling
   - Authentication (nếu có)
   - Rate limiting
   
   docs/algorithm.md:
   - BFS algorithm explanation
   - Complexity analysis
   - Why BFS cho unweighted graph
   - Alternative algorithms considered
   - Performance benchmarks
   
   docs/deployment.md:
   - Setup instructions
   - Environment variables
   - Docker deployment (optional)
   - Production considerations
   
   README.md (update):
   - Project overview
   - Features
   - Installation
   - Usage examples (CLI và API)
   - API documentation link
   - Contributing guidelines
   - License

2. CODE QUALITY TOOLS:

   Setup pre-commit hooks (.pre-commit-config.yaml):
   - black: Code formatting
   - isort: Import sorting
   - flake8: Linting
   - mypy: Type checking
   - pytest: Run tests
   
   pyproject.toml:
   - Black configuration
   - isort configuration
   - pytest configuration
   
   .flake8:
   - Max line length: 100
   - Ignore rules if needed
   - Exclude patterns
   
   mypy.ini:
   - Strict type checking
   - Ignore missing imports for 3rd party

3. CODE FORMATTING:
   ```bash
   # Format all code
   black src/ api/ cli/ tests/
   
   # Sort imports
   isort src/ api/ cli/ tests/
   
   # Lint
   flake8 src/ api/ cli/
   
   # Type check
   mypy src/ api/ cli/
   ```

4. DOCSTRINGS:
   - Every module: Module-level docstring
   - Every class: Class docstring với examples
   - Every public function: Function docstring
   - Google style docstrings
   
   Example:
   ```python
   def find_shortest_path(start: str, end: str) -> PathResult:
       """Tìm đường đi ngắn nhất giữa 2 tỉnh.
       
       Sử dụng thuật toán BFS để tìm đường đi với số lượng
       tỉnh trung gian ít nhất.
       
       Args:
           start: Tên tỉnh xuất phát
           end: Tên tỉnh đích
           
       Returns:
           PathResult chứa đường đi và metadata
           
       Raises:
           ProvinceNotFoundError: Khi tỉnh không tồn tại
           NoPathFoundError: Khi không có đường đi
           
       Examples:
           >>> result = find_shortest_path("Hà Nội", "TP.HCM")
           >>> print(len(result.path))
           18
       """
   ```

5. INLINE COMMENTS:
   - Complex logic: Explain WHY not WHAT
   - Algorithms: Cite sources
   - Workarounds: Explain reason
   - TODOs: Include ticket number

6. CODE REVIEW CHECKLIST:
   - [ ] No hardcoded values (use constants/config)
   - [ ] No print statements (use logging)
   - [ ] Error handling present
   - [ ] Type hints complete
   - [ ] Docstrings present
   - [ ] Tests written
   - [ ] No dead code
   - [ ] DRY principle followed
   - [ ] SOLID principles applied

7. QUALITY METRICS:
   - Complexity: McCabe < 10
   - Line length: < 100
   - Function length: < 50 lines
   - File length: < 500 lines
   - Test coverage: > 85%

OUTPUT:
- docs/api.md
- docs/algorithm.md  
- docs/deployment.md
- README.md (updated)
- .pre-commit-config.yaml
- pyproject.toml
- .flake8
- mypy.ini
- CONTRIBUTING.md
- All code passes linting
- All docstrings complete
```

### Checklist hoàn thành
- [ ] All documentation files complete
- [ ] README comprehensive và clear
- [ ] API docs với examples
- [ ] Algorithm docs với analysis
- [ ] Code quality tools configured
- [ ] All code passes black, isort, flake8
- [ ] Type checking passes with mypy
- [ ] Docstrings đầy đủ và accurate
- [ ] Comments helpful và relevant

---

## BƯỚC 10: INTEGRATION, TESTING VÀ DEPLOYMENT

### Mục tiêu
Tích hợp tất cả components, chạy full test suite, và chuẩn bị deployment.

### Prompt thực hiện

```
Bạn là một DevOps Engineer và Integration Specialist.

NHIỆM VỤ:

1. INTEGRATION CHECKLIST:
   - [ ] Data loading works correctly
   - [ ] Graph builds successfully
   - [ ] BFS algorithm integrated với graph
   - [ ] Service layer orchestrates correctly
   - [ ] API endpoints call service correctly
   - [ ] CLI commands work end-to-end
   - [ ] Error handling flows properly

2. END-TO-END TESTING:
   
   Test scenario 1: API Request
   ```
   Request: POST /api/v1/path/find
   Body: {"start_province": "Hà Nội", "end_province": "TP.HCM"}
   Expected: 200 OK với path result
   ```
   
   Test scenario 2: CLI Command
   ```
   Command: python -m cli.main find -s "Hà Nội" -e "TP.HCM"
   Expected: Console output với path
   ```
   
   Test scenario 3: Invalid Input
   ```
   Request: POST /api/v1/path/find
   Body: {"start_province": "Invalid", "end_province": "TP.HCM"}
   Expected: 404 với error message và suggestions
   ```

3. PERFORMANCE TESTING:
   
   scripts/benchmark.py:
   - Test all 63x63 province combinations
   - Measure average, min, max response time
   - Check memory usage
   - Generate performance report
   
   Requirements:
   - Average: < 30ms
   - Max: < 100ms
   - Memory: < 100MB

4. DEPLOYMENT PREPARATION:

   File: scripts/setup.sh (Linux/Mac)
   ```bash
   #!/bin/bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python scripts/verify_data.py
   python scripts/benchmark.py
   ```
   
   File: scripts/setup.ps1 (Windows)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python scripts/verify_data.py
   ```
   
   File: scripts/run_api.sh
   ```bash
   #!/bin/bash
   source venv/bin/activate
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. DOCKER SUPPORT (Optional):

   Dockerfile:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
   
   docker-compose.yml:
   ```yaml
   version: '3.8'
   services:
     api:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DEBUG=False
   ```

6. CI/CD (Optional):

   .github/workflows/test.yml:
   - Run tests on push
   - Check code coverage
   - Run linting
   - Build Docker image

7. PRODUCTION CHECKLIST:
   - [ ] Environment variables configured
   - [ ] Logging configured properly
   - [ ] Error monitoring setup
   - [ ] API rate limiting (nếu cần)
   - [ ] CORS configured correctly
   - [ ] HTTPS enabled (nếu deploy)
   - [ ] Health check endpoint works
   - [ ] Documentation accessible

8. MONITORING & LOGGING:
   
   Setup structured logging:
   - Use Python logging module
   - Log levels: DEBUG, INFO, WARNING, ERROR
   - Log format: timestamp, level, message, context
   - Log to file và console
   - Rotate log files

9. VERIFICATION SCRIPT:

   scripts/verify_installation.py:
   - Check Python version
   - Check all dependencies installed
   - Load data successfully
   - Build graph successfully
   - Run sample pathfinding
   - Test API startup
   - Print verification report

OUTPUT:
- scripts/setup.sh
- scripts/setup.ps1
- scripts/run_api.sh
- scripts/benchmark.py
- scripts/verify_installation.py
- Dockerfile (optional)
- docker-compose.yml (optional)
- .github/workflows/test.yml (optional)
- docs/deployment.md (updated)
- All integration tests pass
- Performance benchmarks pass
```

### Checklist hoàn thành
- [ ] All components integrated
- [ ] End-to-end tests pass
- [ ] Performance benchmarks meet requirements
- [ ] Setup scripts work on target OS
- [ ] API runs successfully
- [ ] CLI works correctly
- [ ] Verification script passes
- [ ] Documentation complete
- [ ] Ready for deployment

---

## 📊 TIÊU CHÍ ĐÁNH GIÁ HOÀN THÀNH

### Functionality (40%)
- [ ] BFS algorithm hoạt động chính xác
- [ ] Tìm được đường đi ngắn nhất giữa mọi cặp tỉnh
- [ ] API endpoints hoạt động đúng
- [ ] CLI commands hoạt động đúng
- [ ] Error handling đầy đủ

### Code Quality (25%)
- [ ] Tuân thủ PEP 8
- [ ] Type hints đầy đủ
- [ ] Docstrings đầy đủ
- [ ] No code smells
- [ ] SOLID principles applied

### Testing (20%)
- [ ] Code coverage > 85%
- [ ] Unit tests comprehensive
- [ ] Integration tests pass
- [ ] Performance tests pass
- [ ] No flaky tests

### Documentation (10%)
- [ ] README clear và complete
- [ ] API documentation đầy đủ
- [ ] Algorithm explained
- [ ] Setup instructions clear
- [ ] Examples helpful

### Performance (5%)
- [ ] Path finding < 50ms
- [ ] API response < 100ms
- [ ] Memory usage < 100MB
- [ ] No memory leaks
- [ ] Scalable

---

## 🚀 NEXT STEPS AFTER COMPLETION

### Enhancements (Optional)
1. **Trọng số đường đi**: Thêm distance thực tế (km) giữa các tỉnh
2. **Multiple paths**: Tìm nhiều đường đi thay vì chỉ 1
3. **Visualization**: Web UI với bản đồ interactive
4. **Caching**: Redis cache cho frequent queries
5. **Database**: PostgreSQL thay vì JSON files
6. **Authentication**: API keys cho production use
7. **Analytics**: Track popular routes
8. **Mobile app**: React Native hoặc Flutter

### Algorithms to explore
- Dijkstra: Cho weighted graph
- A*: Với heuristic (straight-line distance)
- Bellman-Ford: Cho negative weights
- Floyd-Warshall: All-pairs shortest path

---

## 📝 GHI CHÚ QUAN TRỌNG

1. **Data Accuracy**: Dữ liệu adjacency PHẢI chính xác với thực tế địa lý
2. **Performance**: Luôn benchmark sau mỗi thay đổi
3. **Testing**: Write tests trước khi code (TDD approach)
4. **Documentation**: Update docs khi code thay đổi
5. **Git**: Commit thường xuyên với clear messages
6. **Code Review**: Review code trước khi merge
7. **Security**: Validate và sanitize mọi input
8. **Logging**: Log đầy đủ để debug
9. **Error Messages**: Clear, actionable, Vietnamese
10. **User Experience**: Think about người dùng cuối

---

## ✅ COMPLETION TIMELINE

- **Bước 1**: 1 giờ
- **Bước 2**: 3-4 giờ (research adjacency data)
- **Bước 3**: 2 giờ
- **Bước 4**: 3 giờ
- **Bước 5**: 2 giờ
- **Bước 6**: 2-3 giờ
- **Bước 7**: 1-2 giờ
- **Bước 8**: 3-4 giờ
- **Bước 9**: 2 giờ
- **Bước 10**: 2 giờ

**Total**: ~20-25 giờ làm việc

---

**Good luck và code thật tốt! 🚀**