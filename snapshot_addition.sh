# Following 3 curl request will make sure the new snapshot will be added to the local # Elasticsearch. Make sure the service is running on the same port as curl request # on (In this case 9200). Change the location of the snapshot on line number 7 of first curl # request

# The following request will add the snapshot to the elastic search

curl -X PUT "http://localhost:9200/_snapshot/my_backup" -H 'Content-Type: application/json' -d '
{
  "type": "fs",
  "settings": {
    "location": "snapshot_location",
    "compress": true
  }
}'

# Run the following command for checking if the snapshot is successfully added to the elastic search

curl -X GET "http://localhost:9200/_snapshot/my_backup/_all?pretty"

# The abobe request should give a success acknowledgement from the elastic search.

# Finally hit the following request for final few formalities of the elastic search (for example adding the names, replacing the names, global values.)

curl -X POST "http://localhost:9200/_snapshot/my_backup/snapshot-20230801/_restore" -H 'Content-Type: application/json' -d '
{
  "indices": "index_name",
  "rename_pattern": "index_name",
  "rename_replacement": "restored_index_name",
  "include_global_state": false
}'



