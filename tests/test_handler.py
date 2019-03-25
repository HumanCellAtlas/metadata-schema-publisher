import json
from unittest import TestCase

import handler


class HandlerTest(TestCase):

    def test_process_event_for_master(self):
        # given:
        with open('./files/mock-master-github-push-event.json') as json_file:
            event_json = json.loads(json_file.read())

        # when:
        response = handler.on_github_push(event_json, None, True)
        print(response)

    def test_process_event_for_develop(self):
        # given:
        with open('./files/mock-develop-github-push-event.json') as json_file:
            event_json = json.loads(json_file.read())

        # when:
        response = handler.on_github_push(event_json, None, True)
        print(response)
