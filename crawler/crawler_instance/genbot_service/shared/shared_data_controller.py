import requests

from crawler.constants.constants import RAW_PATH_CONSTANTS


class shared_data_controller:
    __instance = None
    topic_classifier_model = None
    nlp_model = None
    _cache = {}

    def __init__(self):
        if shared_data_controller.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            shared_data_controller.__instance = self

    def init(self):
        pass

    @staticmethod
    def _request(endpoint, method="POST", payload=None):
        try:
            if method.upper() == "POST":
                response = requests.post(endpoint, json=payload)
            elif method.upper() == "GET":
                response = requests.get(endpoint, params=payload)
            else:
                raise ValueError("Unsupported HTTP method")
            response.raise_for_status()
            return response.json()
        except Exception as _:
            pass

    def trigger_topic_classifier(self, p_base_url, p_title, p_important_content, p_content):
        if p_base_url in self._cache:
            return self._cache[p_base_url]["result"]

        payload = {"title": p_title, "description": p_important_content, "keyword": p_content}
        result = self._request(RAW_PATH_CONSTANTS.MICROSERVER + "/topic_classifier/predict", method="POST", payload=payload)
        self._cache[p_base_url] = result
        return result["result"]

    def trigger_nlp_classifier(self, p_text):
        payload = {"data": p_text}
        request = self._request(RAW_PATH_CONSTANTS.MICROSERVER+"/nlp/parse", method="POST", payload=payload)
        result = request.get("result")
        return result

    @staticmethod
    def get_instance():
        if shared_data_controller.__instance is None:
            shared_data_controller()
        return shared_data_controller.__instance
