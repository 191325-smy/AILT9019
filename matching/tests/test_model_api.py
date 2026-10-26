"""Real DeepSeek SDK and structured parser against mock HTTP, without live keys."""

import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import httpx
from langchain_deepseek import ChatDeepSeek

from matching import matcher
from matching.filters import candidates_for_model


class ModelAPIContractTests(unittest.TestCase):
    def setUp(self):
        pool = json.loads((Path(__file__).resolve().parents[1] / 'sample_pool.json').read_text(encoding='utf-8'))
        self.me = next(profile for profile in pool if profile['username'] == 'alice_chen')
        self.candidates, _, _ = candidates_for_model(self.me, pool)

    def test_real_sdk_sends_supported_tool_request_and_parses_response(self):
        captured = []
        ids = [profile['account_id'] for profile in self.candidates[:5]]

        def handler(request):
            payload = json.loads(request.content)
            captured.append(payload)
            self.assertEqual(str(request.url), 'https://api.deepseek.com/v1/chat/completions')
            self.assertEqual(payload['model'], 'deepseek-flash')
            self.assertEqual(payload['thinking'], {'type': 'disabled'})
            self.assertEqual(payload['tool_choice']['function']['name'], 'Shortlist')
            self.assertNotIn('contact_info', json.dumps(payload['messages']))
            self.assertNotIn('password_hash', json.dumps(payload['messages']))
            return httpx.Response(200, json={
                'id': 'fixture-call', 'object': 'chat.completion', 'created': 0,
                'model': 'deepseek-flash', 'choices': [{
                    'index': 0, 'finish_reason': 'tool_calls', 'message': {
                        'role': 'assistant', 'content': None, 'tool_calls': [{
                            'id': 'fixture-tool', 'type': 'function', 'function': {
                                'name': 'Shortlist', 'arguments': json.dumps({'picks': [
                                    {'account_id': account_id, 'reason': 'Adds a complementary project role.'}
                                    for account_id in ids
                                ]})
                            }
                        }]
                    }
                }], 'usage': {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30}
            })

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            def build(name, **options):
                self.assertEqual(options['max_retries'], 0)
                self.assertEqual(options['timeout'], 30)
                return ChatDeepSeek(model=name.split(':', 1)[1], api_key='test-key-not-real',
                                    http_client=client, **options)
            with patch.dict(os.environ, {'MATCH_MODEL': 'deepseek:deepseek-flash'}), \
                 patch('langchain.chat_models.init_chat_model', side_effect=build):
                picks, source = matcher.pick(self.me, self.candidates)
        self.assertEqual(source, 'deepseek:deepseek-flash')
        self.assertEqual([pick['profile']['account_id'] for pick in picks], ids)
        self.assertEqual(len(captured), 1)

    def test_api_error_is_honestly_reported_as_fallback(self):
        requests = []
        def handler(request):
            requests.append(request)
            return httpx.Response(401, json={'error': {'message': 'Invalid demo key', 'type': 'authentication_error'}})
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            def build(name, **options):
                return ChatDeepSeek(model=name.split(':', 1)[1], api_key='test-key-not-real',
                                    http_client=client, **options)
            with patch.dict(os.environ, {'MATCH_MODEL': 'deepseek:deepseek-flash'}), \
                 patch('langchain.chat_models.init_chat_model', side_effect=build):
                picks, source = matcher.pick(self.me, self.candidates)
        self.assertEqual(source, 'fallback:OpenAIAuthenticationError')
        self.assertEqual(len(picks), 5)
        self.assertEqual(len(requests), 1)


if __name__ == '__main__':
    unittest.main()
