import json
import logging

from django.conf import settings
from requests import HTTPError

from osmaxx.api_client.API_client import JWTClient, reasons_for

logger = logging.getLogger(__name__)

SERVICE_BASE_URL = settings.OSMAXX.get('CONVERSION_SERVICE_URL')
LOGIN_URL = '/token-auth/'

USERNAME = settings.OSMAXX.get('CONVERSION_SERVICE_USERNAME')
PASSWORD = settings.OSMAXX.get('CONVERSION_SERVICE_PASSWORD')

CONVERSION_JOB_URL = '/conversion_job/'
ESTIMATED_FILE_SIZE_URL = '/estimate_size_in_bytes/'
FORMAT_SIZE_ESTIMATION_URL = '/format_size_estimation/'


class ConversionApiClient(JWTClient):
    def __init__(self):
        super().__init__(
            service_base=SERVICE_BASE_URL,
            login_url=LOGIN_URL,
            username=USERNAME,
            password=PASSWORD,
        )

    def create_boundary(self, multipolygon, *, name):
        geo_json = json.loads(multipolygon.json)
        json_payload = dict(name=name, clipping_multi_polygon=geo_json)
        response = self.authorized_post(url='clipping_area/', json_data=json_payload)
        return response.json()

    def create_parametrization(self, *, boundary, out_format, detail_level, out_srs):
        """

        Args:
            boundary: A dictionary as returned by create_boundary
            out_format: A string identifying the output format
            detail_level: An integer identifying the level of detail of the output
            out_srs: A string identifying the spatial reference system of the output

        Returns:
            A dictionary representing the payload of the service's response
        """
        json_payload = dict(clipping_area=boundary['id'], out_format=out_format, detail_level=detail_level, out_srs=out_srs)
        response = self.authorized_post(url='conversion_parametrization/', json_data=json_payload)
        return response.json()

    def create_job(self, parametrization, callback_url, user):
        """

        Args:
            parametrization: A dictionary as returned by create_parametrization
            incoming_request: The request towards the front-end triggering this job creation

        Returns:
            A dictionary representing the payload of the service's response
        """
        json_payload = dict(
            parametrization=parametrization['id'], callback_url=callback_url, queue_name=self._priority_queue_name(user)
        )
        response = self.authorized_post(url='conversion_job/', json_data=json_payload)
        return response.json()

    def get_result_file_path(self, job_id):
        file_path = self._get_result_file_path(job_id)
        if file_path:
            return file_path
        raise ResultFileNotAvailableError

    def _priority_queue_name(self, user):
        if user.groups.filter(name=settings.OSMAXX['EXCLUSIVE_USER_GROUP']).exists():
            return 'high'
        return 'default'

    def _get_result_file_path(self, job_id):
        job_detail_url = CONVERSION_JOB_URL + '{}/'.format(job_id)
        return self.authorized_get(job_detail_url).json()['resulting_file_path']

    def job_status(self, export):
        """
        Get the status of the conversion job

        Args:
            export: an Export object

        Returns:
            The status of the associated job

        Raises:
            AssertionError: If `export` has no associated job
        """
        assert isinstance(export.conversion_service_job_id, int)
        response = self.authorized_get(url='conversion_job/{}'.format(export.conversion_service_job_id))
        return response.json()['status']

    def estimated_file_size(self, north, west, south, east):
        request_data = {
            "west": west,
            "south": south,
            "east": east,
            "north": north
        }
        try:
            response = self.authorized_post(ESTIMATED_FILE_SIZE_URL, json_data=request_data)
        except HTTPError as e:
            return reasons_for(e)
        return response.json()

    def format_size_estimation(self, estimated_pbf_size, detail_level):
        request_data = {
            "estimated_pbf_file_size_in_bytes": estimated_pbf_size,
            "detail_level": int(detail_level),
        }
        try:
            response = self.authorized_post(FORMAT_SIZE_ESTIMATION_URL, json_data=request_data)
        except HTTPError as e:
            return reasons_for(e)
        return response.json()


class ResultFileNotAvailableError(RuntimeError):
    pass
