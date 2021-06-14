from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from settings.settings import BASE_DIR
from ImageSearch.viewsets import save_search_result
from ImageSearch.models import SearchResult


class SaveSearchResultTests(APITestCase):

    def setUp(self):
        self.test_id = "55a5c5ba-0134-48b5-9b6d-2e7d6213e2bd"
        self.search_result_ids = [3,18,19,33,52,236,308,312,313,324]
        test_image_path= str(BASE_DIR) + '/assets/test_images/3.png'
        test_image = SimpleUploadedFile(name='test_image.jpg', content=open(test_image_path, 'rb').read(), content_type='image/jpeg')

        SearchResult.objects.create(
            id= self.test_id,
            keep=False,
            results=self.search_result_ids,
            image=test_image)
        print("SearchResult.id: ", self.test_id)


    def test_create_search_result(self):
        """test the endpoint that keeps search results"""

        url = reverse('save-search-result')
        data = {
            "id":str(self.test_id),
            "keep":True,
            }
        response = self.client.post(url, data, format='multipart')
        res = response.data

        assert response.status_code == status.HTTP_200_OK
        assert res['id'] == self.test_id
        assert 'created_date' in res
        assert 'image' in res
        assert res['results'] == self.search_result_ids
        assert SearchResult.objects.count() == 1
