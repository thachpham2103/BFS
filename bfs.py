# -*- coding: utf-8 -*-
import requests
from collections import deque
import json
from openrouteservice import Client, exceptions

# ======================================================================
# CAI DAT API KEY DA DUOC CAP NHAT
# ======================================================================
API_KEY_ORS = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImFkN2YzNzJhYWU5MTRmZDQ5MTFjNDU4YzBmNjMzNTg2IiwiaCI6Im11cm11cjY0In0=" 
ORS_CLIENT = Client(key=API_KEY_ORS) # Tao doi tuong Client ORS

# ======================================================================
# DU LIEU TỌA ĐỘ CỐ ĐỊNH (ĐÃ ĐIỀU CHỈNH LẠI CÁC TỈNH MIỀN TRUNG)
# ======================================================================
# Sử dụng tọa độ cố định (Lon, Lat) cho các tỉnh trọng điểm
HARDCODED_COORDS = {
    # Miền Bắc & TP Lớn
    "Ha Noi": (105.8412, 21.0278), 
    "TP.HCM": (106.6297, 10.8231), 
    "Hai Phong": (106.6881, 20.8587),
    "Da Nang": (108.2199, 16.0544),
    "Can Tho": (105.7865, 10.0336),
    
    # **TỌA ĐỘ ĐÃ ĐƯỢC CHỈNH SỬA LẠI ĐỂ GẦN QL1A HƠN**
    "Thanh Hoa": (105.7876, 19.8152),
    "Nghe An": (105.7001, 18.7001), # Đã chỉnh
    "Ha Tinh": (106.1082, 18.3370), # Đã chỉnh
    "Quang Binh": (106.6062, 17.4878), 
    "Quang Tri": (107.0853, 16.8049), 
    "Thua Thien Hue": (107.5855, 16.4673),
}


# ======================================================================
# DU LIEU GIAP RANH CHO 63 TINH THANH (KHÔNG DẤU)
# ======================================================================
ADJACENCY_LIST = {
    # 1. TÂY BẮC
    "Dien Bien": ["Lai Chau", "Son La"],
    "Lai Chau": ["Dien Bien", "Son La", "Lao Cai"],
    "Son La": ["Dien Bien", "Lai Chau", "Yen Bai", "Phu Tho", "Hoa Binh"],
    "Hoa Binh": ["Son La", "Phu Tho", "Ha Noi", "Ha Nam", "Ninh Binh", "Thanh Hoa"],
    
    # 2. ĐÔNG BẮC
    "Ha Giang": ["Lao Cai", "Tuyen Quang", "Cao Bang"],
    "Cao Bang": ["Ha Giang", "Tuyen Quang", "Bac Kan", "Lang Son"],
    "Lao Cai": ["Son La", "Yen Bai", "Ha Giang", "Lai Chau"],
    "Bac Kan": ["Cao Bang", "Tuyen Quang", "Thai Nguyen", "Lang Son"],
    "Tuyen Quang": ["Ha Giang", "Cao Bang", "Bac Kan", "Thai Nguyen", "Phu Tho", "Yen Bai"],
    "Yen Bai": ["Lao Cai", "Ha Giang", "Tuyen Quang", "Phu Tho", "Son La"],
    "Thai Nguyen": ["Bac Kan", "Tuyen Quang", "Phu Tho", "Vinh Phuc", "Ha Noi", "Bac Giang", "Lang Son"],
    "Phu Tho": ["Yen Bai", "Tuyen Quang", "Thai Nguyen", "Vinh Phuc", "Ha Noi", "Hoa Binh"],
    "Vinh Phuc": ["Phu Tho", "Thai Nguyen", "Ha Noi"],
    "Bac Giang": ["Lang Son", "Thai Nguyen", "Ha Noi", "Bac Ninh", "Hai Duong", "Quang Ninh"],
    "Bac Ninh": ["Thai Nguyen", "Ha Noi", "Bac Giang", "Hai Duong"],
    "Lang Son": ["Cao Bang", "Bac Kan", "Thai Nguyen", "Bac Giang", "Quang Ninh"],

    # 3. ĐỒNG BẰNG SÔNG HỒNG
    "Ha Noi": ["Vinh Phuc", "Thai Nguyen", "Bac Giang", "Bac Ninh", "Hai Duong", "Hung Yen", "Ha Nam", "Hoa Binh", "Phu Tho"],
    "Hai Duong": ["Bac Ninh", "Hung Yen", "Hai Phong", "Quang Ninh", "Bac Giang"],
    "Hung Yen": ["Ha Noi", "Hai Duong", "Thai Binh", "Ha Nam"],
    "Hai Phong": ["Hai Duong", "Thai Binh", "Quang Ninh"],
    "Thai Binh": ["Hai Phong", "Hung Yen", "Nam Dinh"],
    "Nam Dinh": ["Ha Nam", "Ninh Binh", "Thai Binh"],
    "Ha Nam": ["Ha Noi", "Hung Yen", "Nam Dinh", "Ninh Binh", "Hoa Binh"],
    "Ninh Binh": ["Ha Nam", "Nam Dinh", "Thanh Hoa"],

    # 4. BẮC TRUNG BỘ
    "Thanh Hoa": ["Ninh Binh", "Hoa Binh", "Nghe An"],
    "Nghe An": ["Thanh Hoa", "Ha Tinh"],
    "Ha Tinh": ["Nghe An", "Quang Binh"],
    "Quang Binh": ["Ha Tinh", "Quang Tri"],
    "Quang Tri": ["Quang Binh", "Thua Thien Hue"],
    "Thua Thien Hue": ["Quang Tri", "Da Nang", "Quang Nam"],

    # 5. NAM TRUNG BỘ
    "Da Nang": ["Thua Thien Hue", "Quang Nam"],
    "Quang Nam": ["Da Nang", "Thua Thien Hue", "Quang Ngai", "Kon Tum", "Gia Lai"],
    "Quang Ngai": ["Quang Nam", "Binh Dinh", "Kon Tum", "Gia Lai"],
    "Binh Dinh": ["Quang Ngai", "Phu Yen", "Gia Lai"],
    "Phu Yen": ["Binh Dinh", "Khanh Hoa", "Gia Lai", "Dak Lak"],
    "Khanh Hoa": ["Phu Yen", "Ninh Thuan", "Dak Lak", "Lam Dong"],
    "Ninh Thuan": ["Khanh Hoa", "Binh Thuan", "Lam Dong"],
    "Binh Thuan": ["Ninh Thuan", "Lam Dong", "Dong Nai", "Ba Ria - Vung Tau"],

    # 6. TÂY NGUYÊN
    "Kon Tum": ["Quang Nam", "Quang Ngai", "Gia Lai"],
    "Gia Lai": ["Kon Tum", "Quang Ngai", "Binh Dinh", "Phu Yen", "Dak Lak"],
    "Dak Lak": ["Gia Lai", "Phu Yen", "Khanh Hoa", "Lam Dong", "Dak Nong"],
    "Dak Nong": ["Dak Lak", "Lam Dong", "Binh Phuoc"],
    "Lam Dong": ["Dak Lak", "Dak Nong", "Khanh Hoa", "Ninh Thuan", "Binh Thuan", "Dong Nai", "Binh Phuoc"],

    # 7. ĐÔNG NAM BỘ
    "Binh Phuoc": ["Dak Nong", "Lam Dong", "Dong Nai", "Binh Duong", "Tay Ninh"],
    "Tay Ninh": ["Binh Phuoc", "Binh Duong", "Long An"],
    "Binh Duong": ["Binh Phuoc", "Tay Ninh", "Long An", "TP.HCM", "Dong Nai"],
    "Dong Nai": ["Lam Dong", "Binh Thuan", "Ba Ria - Vung Tau", "TP.HCM", "Binh Duong", "Binh Phuoc"],
    "TP.HCM": ["Binh Duong", "Dong Nai", "Long An", "Tien Giang"],
    "Ba Ria - Vung Tau": ["Binh Thuan", "Dong Nai", "TP.HCM"],

    # 8. ĐỒNG BẰNG SÔNG CỬU LONG
    "Long An": ["TP.HCM", "Binh Duong", "Tay Ninh", "Dong Thap", "Tien Giang"],
    "Tien Giang": ["TP.HCM", "Long An", "Dong Thap", "Vinh Long", "Ben Tre"],
    "Dong Thap": ["Long An", "Tien Giang", "Vinh Long", "An Giang", "Can Tho"],
    "Ben Tre": ["Tien Giang", "Vinh Long"],
    "Vinh Long": ["Tien Giang", "Ben Tre", "Tra Vinh", "Soc Trang", "Can Tho", "Dong Thap"],
    "Tra Vinh": ["Ben Tre", "Vinh Long", "Soc Trang"],
    "An Giang": ["Dong Thap", "Can Tho", "Kien Giang"],
    "Can Tho": ["Dong Thap", "Vinh Long", "Hau Giang", "Kien Giang", "An Giang"],
    "Hau Giang": ["Can Tho", "Vinh Long", "Soc Trang", "Kien Giang"],
    "Soc Trang": ["Tra Vinh", "Vinh Long", "Hau Giang", "Bac Lieu"],
    "Kien Giang": ["An Giang", "Can Tho", "Hau Giang", "Ca Mau", "Bac Lieu"],
    "Bac Lieu": ["Soc Trang", "Kien Giang", "Ca Mau"],
    "Ca Mau": ["Kien Giang", "Bac Lieu"]
}

# ======================================================================
# CHUC NANG 1: GOI OPENROUTESERVICE API (FIX DỨT ĐIỂM BẰNG TỌA ĐỘ CỐ ĐỊNH)
# ======================================================================

def get_route_details_ors(origin_name, destination_name):
    """
    Sử dụng Tọa độ cố định nếu có, nếu không sẽ Geocoding dự phòng.
    """
    
    def geocode_city_reliable(city_name):
        # 1. ƯU TIÊN SỬ DỤNG TỌA ĐỘ CỐ ĐỊNH (FIX DỨT ĐIỂM)
        if city_name in HARDCODED_COORDS:
            return HARDCODED_COORDS[city_name]
        
        # 2. DỰ PHÒNG: NẾU KHÔNG CÓ TỌA ĐỘ CỐ ĐỊNH, TIẾN HÀNH GEOCoding an toàn
        try:
            search_query = f"Thành phố {city_name}"
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': search_query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'vn', 
                'viewbox': '102,8,110,24', 
                'bounded': 1 
            }
            headers = {
                'User-Agent': 'VietRoutesFinderApp/1.0' 
            }
            response = requests.get(nominatim_url, params=params, headers=headers)
            data = response.json()
            
            if data and len(data) > 0:
                lon = float(data[0]['lon'])
                lat = float(data[0]['lat'])
                return (lon, lat)
            return None
        except Exception:
            return None

    origin_coords = geocode_city_reliable(origin_name)
    destination_coords = geocode_city_reliable(destination_name)
    
    if not origin_coords or not destination_coords:
         return {"status": "ERROR", "error": f"Khong tim thay toa do cho {origin_name} hoac {destination_name}."}

    try:
        # Routing (Tính toán đường đi bằng ORS)
        route = ORS_CLIENT.directions(
            coordinates=[origin_coords, destination_coords],
            profile='driving-car', # **BUỘC ĐỊNH TUYẾN ĐƯỜNG BỘ**
            preference='shortest',
            radiuses=[1000, 1000] 
        )
        
        summary = route['routes'][0]['summary']
        distance_m = summary['distance']
        duration_s = summary['duration']
        
        distance_text = f"{distance_m / 1000:.2f} km"
        duration_text = f"{int(duration_s // 3600)} gio {int((duration_s % 3600) // 60)} phut"

        return {
            "distance_m": distance_m,
            "distance_text": distance_text,
            "duration_s": duration_s,
            "duration_text": duration_text,
            "status": "OK"
        }

    except exceptions.ApiError as e:
        return {"status": "API ERROR", "error": f"Loi ORS API: {e}"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# ======================================================================
# CHUC NANG 2: THUAT TOAN BFS (GIU NGUYEN)
# ======================================================================

def bfs_shortest_path_cities(start_city, end_city, graph):
    """
    Tim duong di ngan nhat (it buoc nhay nhat) giua hai tinh bang BFS.
    """
    if start_city == end_city:
        return [start_city]
    if start_city not in graph or end_city not in graph:
        return None

    queue = deque([[start_city]]) 
    visited = {start_city}

    while queue:
        path = queue.popleft()
        current_city = path[-1]

        for neighbor in graph.get(current_city, []):
            if neighbor not in visited:
                new_path = list(path)
                new_path.append(neighbor)
                
                if neighbor == end_city:
                    return new_path
                
                visited.add(neighbor)
                queue.append(new_path)
    
    return None

# ======================================================================
# CHUC NANG 3: THUC THI CHINH
# ======================================================================

def find_shortest_city_route(start, end):
    """
    Thuc thi tim duong va lay khoang cach thuc bang ORS.
    """
    print(f"--- Bat dau tim kiem (Mien phi ORS): {start} -> {end} ---")
    
    # 1. Tim chuoi tinh bang BFS
    city_path = bfs_shortest_path_cities(start, end, ADJACENCY_LIST)
    
    if not city_path:
        print("LOI: Khong tim thay chuoi tinh thanh giap ranh lien ket (Kiem tra ADJACENCY_LIST).")
        return

    print(f"\nChuoi tinh thanh it buoc nhay nhat (BFS): {' -> '.join(city_path)}")
    print(f"Tong so buoc nhay: {len(city_path) - 1}")

    # 2. Lay chi tiet duong đi thuc te tu ORS
    print("\n--- Lay Chi tiet Duong di Thuc te (OpenRouteService) ---")
    
    total_distance_m = 0
    total_duration_s = 0
    detailed_legs = []

    for i in range(len(city_path) - 1):
        origin = city_path[i]
        destination = city_path[i+1]
        
        print(f"  > Tinh toan chang {i+1}: {origin} -> {destination}...")
        route_info = get_route_details_ors(origin, destination)
        
        if route_info and route_info["status"] == "OK":
            total_distance_m += route_info["distance_m"]
            total_duration_s += route_info["duration_s"]
            detailed_legs.append({
                "origin": origin,
                "destination": destination,
                "distance": route_info["distance_text"],
                "duration": route_info["duration_text"]
            })
        elif route_info is None or route_info["status"] != "OK":
            print(f"    [BO QUA CHANG] Loi lay thong tin chang {origin} -> {destination}: {route_info.get('error', 'Loi khong xac dinh')}")
            return # Dừng nếu có lỗi API

    # 3. Hien thi ket qua
    print("\n=======================================================")
    print(f"KET QUA DUONG DI: {start} -> {end}")
    print("=======================================================")
    
    # Hien thi chi tiet tung chang
    for leg in detailed_legs:
        print(f"**{leg['origin']} -> {leg['destination']}**: Khoang cach: {leg['distance']}, Thoi gian: {leg['duration']}")
    
    # Tinh tong khoang cach/thoi gian
    total_distance_km = total_distance_m / 1000
    hours = int(total_duration_s // 3600)
    minutes = int((total_duration_s % 3600) // 60)
    
    print("\n**TONG HOP:**")
    print(f"Tong khoang cach thuc te: **{total_distance_km:.2f} km**")
    print(f"Tong thoi gian di chuyen (uoc tinh): **{hours} gio {minutes} phut**")
    print("=======================================================")

# ======================================================================
# THUC THI CHINH: NHAP TU BAN PHIM
# ======================================================================

def get_user_input():
    # In ra danh sach tinh co san de nguoi dung chon
    print("\n------------------------------------------------------")
    print("DANH SACH CAC TINH THANH CO SAN (SU DUNG TEN KHONG DAU):")
    print("------------------------------------------------------")
    
    # Hien thi danh sach tinh theo 3 cot
    cities = list(ADJACENCY_LIST.keys())
    num_cities = len(cities)
    num_cols = 3
    rows = (num_cities + num_cols - 1) // num_cols
    
    for i in range(rows):
        row_str = ""
        for j in range(num_cols):
            index = i + j * rows
            if index < num_cities:
                city = cities[index].ljust(15) # Canh le 15 ky tu
                row_str += f"{city}"
        print(row_str)

    print("------------------------------------------------------")
    
    # Nhap tinh bat dau
    while True:
        start_city = input("Nhap ten tinh bat dau (VD: Ha Noi): ").strip()
        if start_city in ADJACENCY_LIST:
            break
        print(f"Loi: Tinh '{start_city}' khong hop le hoac khong co trong danh sach. Hay nhap lai.")

    # Nhap tinh ket thuc
    while True:
        end_city = input("Nhap ten tinh ket thuc (VD: TP.HCM): ").strip()
        if end_city in ADJACENCY_LIST:
            break
        print(f"Loi: Tinh '{end_city}' khong hop le hoac khong co trong danh sach. Hay nhap lai.")
        
    return start_city, end_city

# Goi ham nhap input va tim duong
start_city_input, end_city_input = get_user_input()
find_shortest_city_route(start_city_input, end_city_input)