import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.services.template_service import TemplateService

def test_template_rendering_and_placeholders():
    subject = "Hello {name}, update for {subject_topic}"
    body = "Dear {name},\n\nYour application for {position} at {company} is approved.\nEmail: {email}"
    
    data = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "subject_topic": "Q3 Review",
        "position": "Senior Developer",
        "company": "TechCorp"
    }

    rendered_sub, rendered_body, detected = TemplateService.preview(subject, body, data)

    assert rendered_sub == "Hello Alice Smith, update for Q3 Review"
    assert "Dear Alice Smith" in rendered_body
    assert "Senior Developer at TechCorp" in rendered_body
    assert "alice@example.com" in rendered_body
    assert set(detected) == {"name", "subject_topic", "position", "company", "email"}

def test_missing_variable_handling():
    body = "Hello {name}, your code is {missing_code}"
    data = {"name": "Bob"}
    rendered = TemplateService.render_template(body, data)
    assert rendered == "Hello Bob, your code is {missing_code}" # Safe fallback without crashing

