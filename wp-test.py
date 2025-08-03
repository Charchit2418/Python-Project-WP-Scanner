import unittest
from unittest.mock import patch, MagicMock
from wpscan import scan_wordpress, log_status


# Dummy tkinter output widget simulator
class DummyOutputBox:
    def __init__(self):
        self.logs = []

    def insert(self, end, msg, color):
        self.logs.append((msg.strip(), color))

    def see(self, end):
        pass

    def delete(self, start, end):
        self.logs.clear()


class DummyStatusLabel:
    def config(self, **kwargs):
        self.status = kwargs


class DummyProgressBar:
    def start(self): pass
    def stop(self): pass


class TestWordPressRecon(unittest.TestCase):

    @patch('requests.get')
    def test_xmlrpc_enabled(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "XML-RPC server accepts POST requests only"
        mock_get.return_value = mock_resp

        output = DummyOutputBox()
        status_label = DummyStatusLabel()
        progress = DummyProgressBar()

        scan_wordpress("example.com", output, status_label, progress)

        found = any("XML-RPC is enabled" in log[0] and log[1] == "green" for log in output.logs)
        self.assertTrue(found)

    @patch('requests.get')
    def test_wp_config_inaccessible(self, mock_get):
        def side_effect(url, headers, timeout):
            mock_resp = MagicMock()
            if "wp-config.php" in url:
                mock_resp.text = ""
            else:
                mock_resp.text = "Dummy"
            mock_resp.status_code = 200
            return mock_resp

        mock_get.side_effect = side_effect

        output = DummyOutputBox()
        status_label = DummyStatusLabel()
        progress = DummyProgressBar()

        scan_wordpress("example.com", output, status_label, progress)

        match = any("wp-config.php is not accessible" in log[0] for log in output.logs)
        self.assertTrue(match)

    @patch('requests.get')
    def test_robots_txt_found(self, mock_get):
        def side_effect(url, headers, timeout):
            mock_resp = MagicMock()
            if "robots.txt" in url:
                mock_resp.text = "User-agent: *\nDisallow: /admin"
            else:
                mock_resp.text = "Dummy"
            mock_resp.status_code = 200
            return mock_resp

        mock_get.side_effect = side_effect

        output = DummyOutputBox()
        status_label = DummyStatusLabel()
        progress = DummyProgressBar()

        scan_wordpress("example.com", output, status_label, progress)

        self.assertTrue(any("robots.txt found" in log[0] for log in output.logs))

    @patch('requests.get')
    def test_user_enum_from_wp_json(self, mock_get):
        def side_effect(url, headers, timeout=10):
            mock_resp = MagicMock()
            if "wp-json/wp/v2/users" in url:
                mock_resp.status_code = 200
                mock_resp.json.return_value = [{'slug': 'admin'}, {'slug': 'editor'}]
                return mock_resp
            elif "wp-json" in url:
                mock_resp.status_code = 200
                mock_resp.text = '{"description": "Sample", "endpoints": []}'
                mock_resp.json.return_value = {}  # not used, but good practice
                return mock_resp
            else:
                mock_resp.status_code = 200
                mock_resp.text = "Dummy"
                return mock_resp

        mock_get.side_effect = side_effect

        output = DummyOutputBox()
        status_label = DummyStatusLabel()
        progress = DummyProgressBar()

        scan_wordpress("example.com", output, status_label, progress)

        users_found = [log for log in output.logs if "User found" in log[0]]
        self.assertGreaterEqual(len(users_found), 2)

    def test_log_status_accessible(self):
        output = DummyOutputBox()

        def dummy_log(msg, color="black"):
            output.insert(None, msg, color)

        log_status("wp-cron.php", "<html>content</html>", "http://test.com/wp-cron.php", dummy_log)
        self.assertTrue(any("wp-cron.php is accessible" in log[0] for log in output.logs))


if __name__ == '__main__':
    unittest.main()
