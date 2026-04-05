from pocketbase import PocketBase

def test_batch_service_queues_and_sends(httpx_mock):
    # Setup mock client
    client = PocketBase("http://localhost:8090")
    
    # Mock the API response for the batch endpoint
    httpx_mock.add_response(
        url="http://localhost:8090/api/batch",
        method="POST",
        json=[{"status": 200}, {"status": 200}, {"status": 204}],
    )

    # Initialize batch
    batch = client.batch.create()
    
    # Queue operations
    batch.collection("tasks").create({"title": "New Task"})
    batch.collection("tasks").update("id_123", {"status": "done"})
    batch.collection("tasks").delete("id_456")
    
    # Send transaction
    result = batch.send()

    # Verify results
    assert len(result) == 3
    assert len(batch.requests) == 3
    
    # Verify the structure of the constructed requests
    assert batch.requests[0]["method"] == "POST"
    assert batch.requests[0]["url"] == "/api/collections/tasks/records"
    assert batch.requests[0]["body"] == {"title": "New Task"}
    
    assert batch.requests[1]["method"] == "PATCH"
    assert batch.requests[1]["url"] == "/api/collections/tasks/records/id_123"
    
    assert batch.requests[2]["method"] == "DELETE"
    assert batch.requests[2]["url"] == "/api/collections/tasks/records/id_456"
