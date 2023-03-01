from travel_scraper.utils import load_json_to_s3, load_json
import json

if __name__ == "__main__":
    data = load_json("result/19ef041d-fe13-4b8a-8017-c4c36fac5ee9/meta.json")
    load_json_to_s3(data, "test/data.json", "parsing", is_json=True)

    with open("result/19ef041d-fe13-4b8a-8017-c4c36fac5ee9/content.html", "r") as file:
        content = file.read()
    
    load_json_to_s3(content, "test/content.html", "parsing")
    load_json_to_s3(data, "test.json", "parsing")