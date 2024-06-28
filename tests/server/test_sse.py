import unittest

from wwwpy.server.sse import create_event


class TestSSEProtocol(unittest.TestCase):
    def test_create_simple_event(self):
        event = create_event(data="hello", event_type="whatever")
        expected = "event: whatever\ndata: hello\n\n"
        self.assertEqual(event, expected)

    def test_create_multiline_data_event(self):
        multiline_data = "line1\nline2\nline3"
        event = create_event(data=multiline_data, event_type="whatever")
        expected = "event: whatever\ndata: line1\ndata: line2\ndata: line3\n\n"
        self.assertEqual(event, expected)

    def test_create_event_empty_data(self):
        with self.assertRaises(ValueError) as context:
            create_event(data="", event_type="whatever")
        self.assertTrue("Data field cannot be empty" in str(context.exception))

    def test_create_event_none_data(self):
        with self.assertRaises(ValueError) as context:
            create_event(data=None, event_type="whatever")
        self.assertTrue("Data field cannot be empty" in str(context.exception))


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
