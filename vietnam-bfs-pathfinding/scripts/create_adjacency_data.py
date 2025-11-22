import json
import os
from pathlib import Path
from typing import Dict, List, Tuple


# Source: Bản đồ hành chính Việt Nam - 34 tỉnh thành
# Mapping: Hà Nội=01, Cao Bằng=04, Tuyên Quang=08, Điện Biên=11, Lai Châu=12, Sơn La=14, Lào Cai=15
# Thái Nguyên=19, Lạng Sơn=20, Quảng Ninh=22, Bắc Ninh=24, Phú Thọ=25, Hải Phòng=31, Hưng Yên=33
# Ninh Bình=37, Thanh Hóa=38, Nghệ An=40, Hà Tĩnh=42, Quảng Trị=44, Huế=46, Đà Nẵng=48
# Quảng Ngãi=51, Gia Lai=52, Khánh Hòa=56, Đắk Lắk=66, Lâm Đồng=68, Đồng Nai=75, TP.HCM=79
# Tây Ninh=80, Đồng Tháp=82, Vĩnh Long=86, An Giang=91, Cần Thơ=92, Cà Mau=96

ADJACENCY_DATA: Dict[str, List[str]] = {
    # Miền Bắc
    "01": ["24", "25", "33", "37", "19"],  # Hà Nội giáp: Bắc Ninh, Phú Thọ, Hưng Yên, Ninh Bình, Thái Nguyên
    "04": ["08", "19", "20"],  # Cao Bằng giáp: Tuyên Quang, Thái Nguyên, Lạng Sơn
    "08": ["04", "15", "19", "25"],  # Tuyên Quang giáp: Cao Bằng, Lào Cai, Thái Nguyên, Phú Thọ
    "11": ["12", "14"],  # Điện Biên giáp: Lai Châu, Sơn La
    "12": ["11", "14", "15"],  # Lai Châu giáp: Điện Biên, Sơn La, Lào Cai
    "14": ["11", "12", "15", "25", "38"],  # Sơn La giáp: Điện Biên, Lai Châu, Lào Cai, Phú Thọ, Thanh Hóa
    "15": ["08", "12", "14", "19", "25"],  # Lào Cai giáp: Tuyên Quang, Lai Châu, Sơn La, Thái Nguyên, Phú Thọ
    "19": ["01", "04", "08", "15", "20", "24", "25"],  # Thái Nguyên giáp: Hà Nội, Cao Bằng, Tuyên Quang, Lào Cai, Lạng Sơn, Bắc Ninh, Phú Thọ
    "20": ["04", "19", "22", "24"],  # Lạng Sơn giáp: Cao Bằng, Thái Nguyên, Quảng Ninh, Bắc Ninh
    "22": ["20", "24", "31"],  # Quảng Ninh giáp: Lạng Sơn, Bắc Ninh, Hải Phòng
    "24": ["01", "19", "20", "22", "31", "33"],  # Bắc Ninh giáp: Hà Nội, Thái Nguyên, Lạng Sơn, Quảng Ninh, Hải Phòng, Hưng Yên
    "25": ["01", "08", "14", "15", "19", "37", "38"],  # Phú Thọ giáp: Hà Nội, Tuyên Quang, Sơn La, Lào Cai, Thái Nguyên, Ninh Bình, Thanh Hóa
    "31": ["22", "24", "33"],  # Hải Phòng giáp: Quảng Ninh, Bắc Ninh, Hưng Yên
    "33": ["01", "24", "31", "37"],  # Hưng Yên giáp: Hà Nội, Bắc Ninh, Hải Phòng, Ninh Bình
    
    # Miền Trung
    "37": ["01", "25", "33", "38"],  # Ninh Bình giáp: Hà Nội, Phú Thọ, Hưng Yên, Thanh Hóa
    "38": ["14", "25", "37", "40"],  # Thanh Hóa giáp: Sơn La, Phú Thọ, Ninh Bình, Nghệ An
    "40": ["38", "42"],  # Nghệ An giáp: Thanh Hóa, Hà Tĩnh
    "42": ["40", "44"],  # Hà Tĩnh giáp: Nghệ An, Quảng Trị
    "44": ["42", "46"],  # Quảng Trị giáp: Hà Tĩnh, Huế
    "46": ["44", "48"],  # Huế giáp: Quảng Trị, Đà Nẵng
    "48": ["46", "51"],  # Đà Nẵng giáp: Huế, Quảng Ngãi
    "51": ["48", "52"],  # Quảng Ngãi giáp: Đà Nẵng, Gia Lai
    "52": ["51", "66"],  # Gia Lai giáp: Quảng Ngãi, Đắk Lắk
    "56": ["66", "68"],  # Khánh Hòa giáp: Đắk Lắk, Lâm Đồng
    "66": ["52", "56", "68"],  # Đắk Lắk giáp: Gia Lai, Khánh Hòa, Lâm Đồng
    "68": ["56", "66", "75"],  # Lâm Đồng giáp: Khánh Hòa, Đắk Lắk, Đồng Nai
    
    # Miền Nam
    "75": ["68", "79", "80"],  # Đồng Nai giáp: Lâm Đồng, TP.HCM, Tây Ninh
    "79": ["75", "80", "82"],  # TP.HCM giáp: Đồng Nai, Tây Ninh, Đồng Tháp
    "80": ["75", "79", "82"],  # Tây Ninh giáp: Đồng Nai, TP.HCM, Đồng Tháp
    "82": ["79", "80", "86", "91", "92"],  # Đồng Tháp giáp: TP.HCM, Tây Ninh, Vĩnh Long, An Giang, Cần Thơ
    "86": ["82", "92"],  # Vĩnh Long giáp: Đồng Tháp, Cần Thơ
    "91": ["82", "92", "96"],  # An Giang giáp: Đồng Tháp, Cần Thơ, Cà Mau
    "92": ["82", "86", "91", "96"],  # Cần Thơ giáp: Đồng Tháp, Vĩnh Long, An Giang, Cà Mau
    "96": ["91", "92"],  # Cà Mau giáp: An Giang, Cần Thơ
}


def validate_adjacency_symmetry(adjacency: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    errors = []
    
    for province_code, neighbors in adjacency.items():
        for neighbor_code in neighbors:
            if neighbor_code not in adjacency:
                errors.append(
                    f"Province {neighbor_code} (neighbor of {province_code}) "
                    f"not found in adjacency data"
                )
                continue
            
            if province_code not in adjacency[neighbor_code]:
                errors.append(
                    f"Asymmetric adjacency: {province_code} lists {neighbor_code} "
                    f"as neighbor, but {neighbor_code} doesn't list {province_code}"
                )
    
    return len(errors) == 0, errors


def get_adjacency_stats(adjacency: Dict[str, List[str]]) -> Dict:
    neighbor_counts = [len(neighbors) for neighbors in adjacency.values()]
    
    return {
        "total_provinces": len(adjacency),
        "total_edges": sum(neighbor_counts) // 2,
        "avg_neighbors": sum(neighbor_counts) / len(adjacency),
        "min_neighbors": min(neighbor_counts),
        "max_neighbors": max(neighbor_counts),
        "provinces_with_min": [
            code for code, neighbors in adjacency.items()
            if len(neighbors) == min(neighbor_counts)
        ],
        "provinces_with_max": [
            code for code, neighbors in adjacency.items()
            if len(neighbors) == max(neighbor_counts)
        ]
    }


def create_adjacency_file(output_path: str) -> None:
    is_valid, errors = validate_adjacency_symmetry(ADJACENCY_DATA)
    
    if not is_valid:
        print("Adjacency data validation FAILED:")
        for error in errors:
            print(f"  - {error}")
        raise ValueError("Adjacency data contains errors")
    
    print("Adjacency data validation PASSED")
    
    stats = get_adjacency_stats(ADJACENCY_DATA)
    print(f"\nAdjacency Statistics:")
    print(f"  Total provinces: {stats['total_provinces']}")
    print(f"  Total edges: {stats['total_edges']}")
    print(f"  Average neighbors: {stats['avg_neighbors']:.2f}")
    print(f"  Min neighbors: {stats['min_neighbors']} "
          f"(provinces: {', '.join(stats['provinces_with_min'])})")
    print(f"  Max neighbors: {stats['max_neighbors']} "
          f"(provinces: {', '.join(stats['provinces_with_max'])})")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ADJACENCY_DATA, f, ensure_ascii=False, indent=2)
    
    print(f"\nAdjacency data saved to: {output_path}")


def main() -> None:
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    adjacency_file = data_dir / "adjacency.json"
    
    print("Creating adjacency data for 34 Vietnamese provinces...")
    print(f"Output: {adjacency_file}\n")
    
    try:
        create_adjacency_file(str(adjacency_file))
    except Exception as e:
        print(f"Error creating adjacency data: {e}")
        return
    
    print("\nData creation completed successfully!")


if __name__ == "__main__":
    main()
