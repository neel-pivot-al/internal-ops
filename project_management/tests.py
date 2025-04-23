from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from project_management.factories import (
    FeatureFactory,
    FunctionFactory,
    ProjectFactory,
    UserFactory,
    WorkLogFactory,
)
from project_management.models import Project

User = get_user_model()


class ProjectTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(role=User.Role.ADMIN)
        self.client.force_authenticate(user=self.user)

    def test_list_projects(self):
        client = UserFactory(role=User.Role.CLIENT)
        ProjectFactory(client=client)
        url = "/api/projects/projects/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_list_project_by_id(self):
        project = ProjectFactory()
        url = f"/api/projects/projects/{project.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], project.id)

    def test_list_projects_filters(self):
        project = ProjectFactory()
        url = "/api/projects/projects/"
        response = self.client.get(url, {"client": project.client.id})
        ProjectFactory(status=Project.Status.SECURED)
        ProjectFactory(status=Project.Status.IN_PROGRESS)
        ProjectFactory(status=Project.Status.IN_PROGRESS)
        ProjectFactory(status=Project.Status.COMPLETED)
        ProjectFactory(status=Project.Status.COMPLETED)
        ProjectFactory(status=Project.Status.COMPLETED)

        response = self.client.get(url, {"status": Project.Status.SECURED})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(url, {"status": Project.Status.IN_PROGRESS})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        response = self.client.get(url, {"status": Project.Status.COMPLETED})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 3)

    def test_invoice_generation_by_client(self):
        client = UserFactory(role=User.Role.CLIENT)
        url = "/api/projects/generate_invoice/"
        request_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "client": client.id,
        }
        response = self.client.post(url, request_data)
        print(response.data)
        self.assertEqual(response.status_code, 403)
