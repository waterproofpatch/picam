import json

from flask_jwt_extended import create_access_token, create_refresh_token


def test_get_images(authenticated_client):
    """
    Test the images endpoint, retrieval
    """
    res = authenticated_client.get("/api/images")
    assert 200 == res.status_code
    assert "application/json" == res.content_type

    # not expecting any images
    assert not res.get_json()


def test_get_images_fail_unauthenticated(unauthenticated_client):
    """
    Test the images endpoint, retrieval
    """
    res = unauthenticated_client.get("/api/images")
    assert 401 == res.status_code


def test_post_images_fail_content_type(authenticated_client):
    """
    Test that images endpoint fails when content type is wrong
    """
    res = authenticated_client.post("/api/images")
    assert 400 == res.status_code
    assert "error" in res.json
    assert "invalid content type" in res.json["error"]


def test_delete_images_fail_unauthenticated(unauthenticated_client):
    """
    Test that images endpoint fails when we are not logged in and try to delete an image
    """
    res = unauthenticated_client.delete("/api/images?id=1")
    assert 401 == res.status_code


def test_post_images_fail_unauthenticated(unauthenticated_client):
    """
    Test that images endpoint fails when we are not logged in
    """
    res = unauthenticated_client.post("/api/images")
    assert 401 == res.status_code


def test_delete_image_wrong_id(authenticated_client, test_images):
    """
    Test that we can delete an image
    """
    res = authenticated_client.delete("api/images?id=3")
    assert res.status_code == 400
    assert "error" in res.json
    assert "Item not found" in res.json["error"]

    res = authenticated_client.get("api/images")
    assert res.status_code == 200
    assert len(res.json) == 2


def test_delete_images_success(authenticated_client, test_images):
    """
    Test that we can delete an image
    """
    res = authenticated_client.delete("api/images?id=1")
    assert res.status_code == 200

    res = authenticated_client.get("api/images")
    assert res.status_code == 200
    assert len(res.json) == 1
