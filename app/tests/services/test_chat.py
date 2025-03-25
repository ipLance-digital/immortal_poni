# async def test_create_chat(client, db):
#     response = client.post(
#         "/chat/",
#         json={
#             "customer_id": "550e8400-e29b-41d4-a716-446655440000",
#             "performer_id": "550e8400-e29b-41d4-a716-446655440001"
#         },
#         headers={"Authorization": "Bearer your_token"}
#     )
#     assert response.status_code == 201
#     assert response.json()["customer_id"] == "550e8400-e29b-41d4-a716-446655440000"
#
# async def test_get_chats(client, db):
#     response = client.get(
#         "/chat/",
#         headers={"Authorization": "Bearer your_token"}
#     )
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)