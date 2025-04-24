# [
#     {
#         "id": "1",
#         "text": "Hello, world!",
#         "audios_1":{
#         "audio1": 4,
#         "audio2": 1,
#         "audio3": 3,
#         "audio4": 2
#     }
#     },
#     {
#         "id": "2",
#         "text": "Hello, world!",
#         "audios_2":{
#             "audio1": 4,
#             "audio2": 1,
#             "audio3": 3,
#             "audio4": 2
#         }
#     }
    
# ]

import json
import random

def read_text_file(file_path="text.txt"):
    """Read lines from text file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

def generate_unique_ratings():
    """Generate random unique ratings from 1 to 4"""
    ratings = list(range(1, 5))  # [1, 2, 3, 4]
    random.shuffle(ratings)
    return {
        "audio1": ratings[0],
        "audio2": ratings[1],
        "audio3": ratings[2],
        "audio4": ratings[3]
    }

def create_metadata():
    """Create metadata in required format"""
    lines = read_text_file()
    metadata = []
    
    for idx, text in enumerate(lines, 1):
        entry = {
            "id": str(idx),
            "text": text,
            f"audios_{idx}": generate_unique_ratings()
        }
        metadata.append(entry)
    
    return metadata

def save_metadata(metadata, output_file="new_metadata.json"):
    """Save metadata to JSON file with proper formatting"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print(f"Metadata saved to {output_file}")

if __name__ == "__main__":
    metadata = create_metadata()
    save_metadata(metadata)