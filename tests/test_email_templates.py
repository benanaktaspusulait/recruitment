import pytest
from src.models import entities
from src.services.auth_service import AuthService

def test_list_templates_as_admin(client, db_session):
    # Login as admin
    response = client.post(
        "/v1/auth/token",
        data={
            "username": "admin@company.com",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Get email templates
    response = client.get(
        "/v1/email-templates/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    templates = response.json()
    assert len(templates) > 0

def test_list_templates_as_recruiter(client, db_session):
    # Login as recruiter
    response = client.post(
        "/v1/auth/token",
        data={
            "username": "recruiter@company.com",
            "password": "recruiter123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Get email templates
    response = client.get(
        "/v1/email-templates/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_list_templates_as_candidate(client, db_session):
    # Login as candidate
    response = client.post(
        "/v1/auth/token",
        data={
            "username": "candidate@company.com",
            "password": "candidate123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Try to get email templates
    response = client.get(
        "/v1/email-templates/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403  # Should be forbidden

def test_create_template_as_admin(client, db_session):
    # Login as admin
    response = client.post(
        "/v1/auth/token",
        data={
            "username": "admin@company.com",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Create new template
    template_data = {
        "name": "Test Template",
        "description": "Test description",
        "subject_template": "Test subject",
        "html_content": "<p>Test content</p>",
        "type": "test",
        "is_active": True
    }
    
    response = client.post(
        "/v1/email-templates/",
        headers={"Authorization": f"Bearer {token}"},
        json=template_data
    )
    assert response.status_code == 201
    created_template = response.json()
    assert created_template["name"] == template_data["name"] 