import unittest

from house_finder.secrets import KeysExhaustedError, Secret, Secrets


class TestSecret(unittest.TestCase):

    def test_rotate(self):
        secret = Secret(['a', 'b', 'c'])
        self.assertEqual(secret.key, 'a')

        secret.rotate()
        self.assertEqual(secret.key, 'b')

        secret.rotate()
        self.assertEqual(secret.key, 'c')

        with self.assertRaises(KeysExhaustedError):
            secret.rotate()

    def test_from_config(self):
        secret_a = Secret.from_config({
            'api_key': 'a',
        })

        secret_b = Secret.from_config({
            'api_keys': ['a', 'b'],
        })

        self.assertEqual(secret_a.key, 'a')

        self.assertEqual(secret_b.key, 'a')


class TestSecrets(unittest.TestCase):

    def test_from_config(self):
        secrets = Secrets.from_config({
            'service_a': {
                'api_key': 'key',
            },
            'service_b': {
                'api_keys': ['key1', 'key2'],
            },
        })

        self.assertIn('service_a', secrets)
        self.assertIn('service_b', secrets)

        self.assertEqual(secrets['service_a'].key, 'key')
        self.assertEqual(secrets['service_b'].key, 'key1')
