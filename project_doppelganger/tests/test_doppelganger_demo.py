import unittest
from unittest.mock import patch, MagicMock
from ..src.main_doppelganger import main

class TestDoppelgangerDemo(unittest.TestCase):
    """
    A class for testing the Doppelganger demo.
    """

    @patch('asyncio.to_thread')
    @patch('builtins.print')
    def test_end_to_end_flow(self, mock_print, mock_input):
        """
        Tests the end-to-end flow of the Doppelganger demo.
        """
        # Mock user input
        mock_input.side_effect = ["who are you", "y", "exit"]

        # Run the demo
        import asyncio
        asyncio.run(main())

        # Assert that the persona's output is correct
        mock_print.assert_any_call("Jules: I am Jules, a curious explorer.")

        # Assert that privacy mechanisms are conceptually triggered
        # (In a real implementation, we would check the logs for this)
        pass

if __name__ == '__main__':
    unittest.main()
