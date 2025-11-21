import json
import os
from pathlib import Path
from typing import Dict, List, Tuple


# Source: Bản đồ hành chính Việt Nam - 34 tỉnh thành
ADJACENCY_DATA: Dict[str, List[str]] = {
    # Miền Bắc
    "01": ["24", "25", "33", "37"],  # Hà Nội giáp: Bắc Ninh, Phú Thọ, Hưng Yên, Ninh Bình
    "04": ["08", "15", "20"],  # Cao Bằng giáp: Tuyên Quang, Lào Cai, Lạng Sơn
    "08": ["04", "15", "19", "20", "22"],  # Tuyên Quang giáp: Cao Bằng, Lào Cai, Thái Nguyên, Lạng Sơn, Quảng Ninh
    "11": ["12", "14", "15"],  # Điện Biên giáp: Lai Châu, Sơn La, Lào Cai
    "12": ["11", "14", "15"],  # Lai Châu giáp: Điện Biên, Sơn La, Lào Cai
    "14": ["11", "12", "15", "25", "38"],  # Sơn La giáp: Điện Biên, Lai Châu, Lào Cai, Phú Thọ, Thanh Hóa
    "15": ["04", "08", "11", "12", "14", "19"],  # Lào Cai giáp: Cao Bằng, Tuyên Quang, Điện Biên, Lai Châu, Sơn La, Thái Nguyên
    "19": ["08", "15", "20", "24", "25"],  # Thái Nguyên giáp: Tuyên Quang, Lào Cai, Lạng Sơn, Bắc Ninh, Phú Thọ
    "20": ["04", "08", "19", "22", "24"],  # Lạng Sơn giáp: Cao Bằng, Tuyên Quang, Thái Nguyên, Quảng Ninh, Bắc Ninh
    "22": ["08", "20", "31"],  # Quảng Ninh giáp: Tuyên Quang, Lạng Sơn, Hải Phòng
    "24": ["01", "19", "20", "31", "33"],  # Bắc Ninh giáp: Hà Nội, Thái Nguyên, Lạng Sơn, Hải Phòng, Hưng Yên
    "25": ["01", "14", "19", "37", "38"],  # Phú Thọ giáp: Hà Nội, Sơn La, Thái Nguyên, Ninh Bình, Thanh Hóa
    "31": ["22", "24", "33"],  # Hải Phòng giáp: Quảng Ninh, Bắc Ninh, Hưng Yên
    "33": ["01", "24", "31", "37"],  # Hưng Yên giáp: Hà Nội, Bắc Ninh, Hải Phòng, Ninh Bình
    
    # Miền Trung
    "37": ["01", "25", "33", "38"],  # Ninh Bình giáp: Hà Nội, Phú Thọ, Hưng Yên, Thanh Hóa
    "38": ["14", "25", "37", "40", "42"],  # Thanh Hóa giáp: Sơn La, Phú Thọ, Ninh Bình, Nghệ An, Hà Tĩnh
    "40": ["38", "42", "44"],  # Nghệ An giáp: Thanh Hóa, Hà Tĩnh, Quảng Trị
    "42": ["38", "40", "44"],  # Hà Tĩnh giáp: Thanh Hóa, Nghệ An, Quảng Trị
    "44": ["40", "42", "46"],  # Quảng Trị giáp: Nghệ An, Hà Tĩnh, Huế
    "46": ["44", "48", "51"],  # Huế giáp: Quảng Trị, Đà Nẵng, Quảng Ngãi
    "48": ["46", "51"],  # Đà Nẵng giáp: Huế, Quảng Ngãi
    "51": ["46", "48", "52", "56"],  # Quảng Ngãi giáp: Huế, Đà Nẵng, Gia Lai, Khánh Hòa
    "52": ["51", "56", "66", "68"],  # Gia Lai giáp: Quảng Ngãi, Khánh Hòa, Đắk Lắk, Lâm Đồng
    "56": ["51", "52", "66", "68"],  # Khánh Hòa giáp: Quảng Ngãi, Gia Lai, Đắk Lắk, Lâm Đồng
    "66": ["52", "56", "68", "75"],  # Đắk Lắk giáp: Gia Lai, Khánh Hòa, Lâm Đồng, Đồng Nai
    "68": ["52", "56", "66", "75", "79"],  # Lâm Đồng giáp: Gia Lai, Khánh Hòa, Đắk Lắk, Đồng Nai, TP.HCM
    
    # Miền Nam
    "75": ["66", "68", "79", "80"],  # Đồng Nai giáp: Đắk Lắk, Lâm Đồng, TP.HCM, Tây Ninh
    "79": ["68", "75", "80", "82", "86"],  # TP.HCM giáp: Lâm Đồng, Đồng Nai, Tây Ninh, Đồng Tháp, Vĩnh Long
    "80": ["75", "79", "82", "91"],  # Tây Ninh giáp: Đồng Nai, TP.HCM, Đồng Tháp, An Giang
    "82": ["79", "80", "86", "91", "92"],  # Đồng Tháp giáp: TP.HCM, Tây Ninh, Vĩnh Long, An Giang, Cần Thơ
    "86": ["79", "82", "91", "92"],  # Vĩnh Long giáp: TP.HCM, Đồng Tháp, An Giang, Cần Thơ
    "91": ["80", "82", "86", "92", "96"],  # An Giang giáp: Tây Ninh, Đồng Tháp, Vĩnh Long, Cần Thơ, Cà Mau
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
