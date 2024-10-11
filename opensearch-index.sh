

# Create OpenSearch mappings for Objective quickstart data

curl -H "Content-Type: application/x-ndjson" -X PUT "https://localhost:9200/obj-quickstart" -ku admin:${OPENSEARCH_INITIAL_ADMIN_PASSWORD} --data-binary "@os-mappings.json"

# Download the Objective quickstart data into OpenSearch bulk index format

curl https://d11p8vtjlacpl4.cloudfront.net/demos/ecommerce/hm-10k.json | jq -c '.[] | { index: { _index: "obj-quickstart", _id: .article_id } }, .' > bulk_data.json

# Bulk index the Objective quickstart data

curl -H "Content-Type: application/x-ndjson" -X POST "https://localhost:9200/obj-quickstart/_bulk" -ku admin:${OPENSEARCH_INITIAL_ADMIN_PASSWORD} --data-binary "@bulk_data.json"


curl -X GET "https://localhost:9200/obj-quickstart/_search?q=*&pretty" -ku admin:${OPENSEARCH_INITIAL_ADMIN_PASSWORD}