import os
import json

# Configuration
SOURCE_DIR = "merged_data"
OUTPUT_DIR = "merged_data_combined"
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

os.makedirs(OUTPUT_DIR, exist_ok=True)

json_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".json")]

current_data = []
current_size = 0
file_index = 0

def write_chunk(data, index):
    output_path = os.path.join(OUTPUT_DIR, f"combined_{index}.json")
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(data, out_file, ensure_ascii=False)
    print(f"Wrote {output_path} with {len(data)} items")

for json_file in json_files:
    path = os.path.join(SOURCE_DIR, json_file)
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    item_str = json.dumps(item)
                    item_size = len(item_str.encode("utf-8"))

                    if current_size + item_size > MAX_FILE_SIZE_BYTES:
                        write_chunk(current_data, file_index)
                        file_index += 1
                        current_data = []
                        current_size = 0

                    current_data.append(item)
                    current_size += item_size
                except json.JSONDecodeError:
                    print(f"Skipping malformed line in {json_file}")
    except Exception as e:
        print(f"Failed to process {json_file}: {e}")

# Write leftover data
if current_data:
    write_chunk(current_data, file_index)
