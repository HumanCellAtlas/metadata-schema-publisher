from unittest import TestCase
from unittest.mock import patch
import handler
import json

class HandlerTest(TestCase):
    
    def test_process_event(self):
        # given:
        with open('tests/files/github-event-release.json') as json_file:
            event_json = json.loads(json_file.read())
            
        # when:
        release = handler.process_event(event_json)
        
        # then:
        self.assertTrue(release)
        self.assertEqual('danielvaughan/metadata-schema', release)