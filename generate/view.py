import json, os
from pinecone import Pinecone
from dotenv import load_dotenv


INDEX_NAME = "insurance-benefits"
NAMESPACES = [
    "insurance/free_benefits",
    "insurance/addons"
]

DIMENSION = 1024
TOP_K = 1000  # safely above your record count

load_dotenv()
key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=key)
index = pc.Index(INDEX_NAME)

def dump_namespace_to_json(namespace: str):
    zero_vector = [0.0] * DIMENSION

    response = index.query(
        namespace=namespace,
        vector=zero_vector,
        top_k=TOP_K,
        include_values=False,
        include_metadata=True
    )

    records = []
    for match in response["matches"]:
        records.append({
            "id": match["id"],
            "metadata": match.get("metadata")
        })

    file_name = namespace.replace("/", "_") + ".json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"✅ Dumped {len(records)} records from '{namespace}' → {file_name}")

for ns in NAMESPACES:
    dump_namespace_to_json(ns)

# view layer edge cases
