
import pytest
import requests_mock

from netboxapi import NetboxAPI
from netboxapi.api import _HTTPTokenAuth


class TestNetboxAPI():
    url = "http://localhost/api"
    login = "login"
    password = "password"
    token = "testing_token"

    @pytest.fixture()
    def prepared_api(self):
        return NetboxAPI(self.url)

    def test_url_sanitizer(self):
        complete_schema_url_netbox_api = NetboxAPI("http://test/api").url
        no_schema_url_netbox_api = NetboxAPI("test/api/").url

        assert complete_schema_url_netbox_api == no_schema_url_netbox_api

    def test_build_model_route(self, prepared_api):
        app = "test_app"
        model = "test_model"

        model_route = prepared_api.build_model_route(app, model).rstrip("/")
        expected_route = "{}/{}".format(app, model).rstrip("/")
        assert model_route == expected_route

    def test_build_model_url(self, prepared_api):
        app = "test_app"
        model = "test_model"

        model_url = prepared_api.build_model_url(app, model).rstrip("/")
        expected_url = self.url + "/{}/{}".format(app, model).rstrip("/")
        assert model_url == expected_url

    def test_get(self, prepared_api, **kwargs):
        self._generic_test_http_method_request(prepared_api, "get")

    def test_get_loggedin(self, **kwargs):
        prepared_api = NetboxAPI(self.url, self.login, self.password)
        self._generic_test_http_method_request(prepared_api, "get")

    def test_get_loggedin_token(self, **kwargs):
        prepared_api = NetboxAPI(self.url, token=self.token)
        self._generic_test_http_method_json(prepared_api, "get")

    def test_post(self, prepared_api, **kwargs):
        self._generic_test_http_method_json(prepared_api, "post")

    def test_put(self, prepared_api, **kwargs):
        self._generic_test_http_method_json(prepared_api, "put")

    def test_patch(self, prepared_api, **kwargs):
        self._generic_test_http_method_json(prepared_api, "patch")

    def test_delete(self, prepared_api, **kwargs):
        self._generic_test_http_method(prepared_api, "delete")

    def _generic_test_http_method_json(self, prepared_api, method):
        response, expected_json = self._generic_test_http_method_request(
            prepared_api, method
        )

        assert response == expected_json

    def _generic_test_http_method(self, prepared_api, method):
        response, _ = self._generic_test_http_method_request(
            prepared_api, method
        )

        assert response.status_code == 200

    def _generic_test_http_method_request(self, prepared_api, method):
        app = "test_app"
        model = "test_model"
        url = prepared_api.build_model_url("test_app", "test_model")
        route = prepared_api.build_model_route("test_app", "test_model")

        expected_json = {"id": 1, "name": "test"}
        with requests_mock.Mocker() as m:
            m.register_uri(method, url, json=expected_json)
            response = getattr(prepared_api, method)(route)

        return response, expected_json


class TestHTTPTokenAuth():
    def test_eq(self):
        assert _HTTPTokenAuth("test") == _HTTPTokenAuth("test")

    def test_not_eq(self):
        assert _HTTPTokenAuth("test") != _HTTPTokenAuth("test1")
