import unittest
from unittest.mock import patch, MagicMock
import os
from supermemory import Supermemory

class TestSupermemory(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        os.environ["SUPERMEMORY_API_KEY"] = self.api_key
        self.client = Supermemory()

    def test_client_initialization(self):
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.api_key, self.api_key)

    @patch('supermemory.resources.memories.MemoriesResource.add')
    def test_add_memory(self, mock_add):
        test_content = "This is a test memory."
        self.client.memories.add(content=test_content)
        mock_add.assert_called_once_with(content=test_content)

    @patch('supermemory.resources.search.SearchResource.execute')
    def test_search_memory(self, mock_search):
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.results = ["result1", "result2"]
        
        # Configure the mock to return the mock response
        mock_search.return_value = mock_response

        query = "test query"
        response = self.client.search.execute(q=query)

        mock_search.assert_called_once_with(q=query)
        self.assertEqual(response.results, ["result1", "result2"])

    @patch('supermemory.resources.memories.MemoriesResource.add')
    @patch('supermemory.resources.search.SearchResource.execute')
    def test_conversation_flow(self, mock_search, mock_add):
        # 1. User provides information
        user_id = "user_123"
        user_info = "The user's favorite color is blue."
        
        self.client.memories.add(content=user_info, metadata={"user_id": user_id})
        
        # Verify memory was added
        mock_add.assert_called_once_with(content=user_info, metadata={"user_id": user_id})
        
        # 2. System later needs to retrieve this information
        question = "What is the user's favorite color?"
        
        # Mock the search response
        mock_response = MagicMock()
        mock_response.results = [user_info]
        mock_search.return_value = mock_response
        
        response = self.client.search.execute(q=question, filter={"user_id": user_id})
        
        # Verify search was called correctly
        mock_search.assert_called_once_with(q=question, filter={"user_id": user_id})
        
        # Verify the retrieved information
        self.assertIn(user_info, response.results)

if __name__ == '__main__':
    unittest.main() 