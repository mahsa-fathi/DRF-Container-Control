from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status


class CreateApplicationAPITestCase(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.endpoint = "/apps/"
        self.payload = {
            "name": "test-image",
            "image": "test",
            "envs": {"key": "value"},
            "command": "some command"
        }

    def test_create_application(self):
        response = self.client.post(self.endpoint, data=self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_application_blank_command(self):
        payload = self.payload
        payload['command'] = ""
        response = self.client.post(self.endpoint, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_application_invalid(self):
        payload = self.payload
        payload['image'] = None
        response = self.client.post(self.endpoint, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ApplicationListAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.endpoint = "/apps/"
        self.create_endpoint = "/apps/"
        self.payload = {
            "name": "test-image",
            "image": "test",
            "envs": {"key": "value"},
            "command": "some command"
        }

    def test_get(self):
        n = 5
        for _ in range(n):
            self.client.post(self.create_endpoint, data=self.payload, format='json')
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], n)


class ApplicationAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.create_endpoint = "/apps/"
        self.payload = {
            "name": "test-image",
            "image": "test",
            "envs": {"key": "value"},
            "command": "some command"
        }
        response = self.client.post(path=self.create_endpoint, data=self.payload, format='json')
        self.id = response.data['id']
        self.endpoint = f"/apps/{self.id}/"

    def tearDown(self):
        self.client.delete(f"/apps/{self.id}/")

    def test_get(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put(self):
        payload = self.payload
        payload['name'] = 'test'
        response = self.client.put(self.endpoint, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'test')

    def test_delete(self):
        response = self.client.delete(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response_list = self.client.get("/apps/").data
        self.assertEqual(response_list['count'], 0)


class RunLogsListAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.create_endpoint = "/apps/"
        self.payload = {
            "name": "test-image",
            "image": "alpine",
            "envs": {},
            "command": "echo hello world"
        }
        response = self.client.post(path=self.create_endpoint, data=self.payload, format='json')
        self.id = response.data['id']
        self.client.get(f"/apps/{self.id}/run/")
        self.endpoint = f"/apps/{self.id}/history/"

    def test_get(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class RunAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.create_endpoint = "/apps/"
        self.payload = {
            "name": "test-image",
            "image": "alpine",
            "envs": {"network": "none"},
            "command": "echo hello world"
        }
        response = self.client.post(path=self.create_endpoint, data=self.payload, format='json')
        self.id = response.data['id']
        self.endpoint = f"/apps/{self.id}/run/"

    def test_successful_run(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['details'], 'Successful')
        self.assertEqual(response.data['logs'], 'hello world\n')

    def test_invalid_image_run(self):
        payload = self.payload
        payload['image'] = 'testalpine'
        self.client.put(f"/apps/{self.id}/", data=payload, format='json')
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_invalid_command(self):
        payload = self.payload
        payload['command'] = 'testcommand'
        self.client.put(f"/apps/{self.id}/", data=payload, format='json')
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_invalid_app_id(self):
        payload = self.payload
        self.client.put(f"/apps/{self.id}/", data=payload, format='json')
        response = self.client.get(f"/apps/{self.id+1}/run/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
