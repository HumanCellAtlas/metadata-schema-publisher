import os

from unittest import TestCase
from unittest.mock import patch
import handler
import json


class HandlerTest(TestCase):

    def test_process_event_for_master(self):
        # given:
        os.environ["API_KEY"] = "0a43698e4acb763d4713f2e1765a0d7622ab26be"
        with open('files/mock-master-github-push-event.json') as json_file:
            event_json = json.loads(json_file.read())

        # when:
        response = handler.on_github_push(event_json, None, True)
        print(response)

    def test_process_event_for_develop(self):
        # given:
        os.environ["API_KEY"] = "0a43698e4acb763d4713f2e1765a0d7622ab26be"
        with open('files/mock-develop-github-push-event.json') as json_file:
            event_json = json.loads(json_file.read())

        # when:
        response = handler.on_github_push(event_json, None, True)
        print(response)
