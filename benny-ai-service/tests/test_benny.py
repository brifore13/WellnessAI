"""Unit tests for Benny AI"""

import unittest
import asyncio
from src.core.benny import BennyWellnessAI


class TestBennyWellness(unittest.TestCase):
    """Test cases for Benny AI"""

    @classmethod
    def setUpClass(cls):
        """Initialize Benny once for all tests."""
        try:
            cls.benny = BennyWellnessAI()
            cls.setup_success = True
        except Exception as e:
            print(f"Setup failed: {e}")
            cls.setup_success = False

    def setUp(self):
        """Check Benny initialized."""
        if not self.setup_success:
            self.skipTest("Benny initialization failed")

    def test_initialization(self):
        """Test Benny initializes correctly."""
        self.assertIsNotNone(self.benny)
        self.assertIsNotNone(self.benny.client)
        print("✓ Initialization test passed")

    def test_chat_simple(self):
        """Test basic chat functionality."""
        message = "Hello Benny"
        result = asyncio.run(self.benny.chat(message))

        self.assertTrue(result["success"])
        self.assertIn("response", result)
        self.assertGreater(len(result["response"]), 0)
        self.assertGreater(result["tokens_used"], 0)

        print(f"\n Chat Test")
        print(f"  User: {message}")
        print(f"  Benny: {result['response'][:100]}...")

    def test_recommendation(self):
        """Test recommendation generation."""
        checkin = {
            "nutrition": "Okay",
            "sleep": "Poor",
            "fitness": "No, skipped",
            "stress": "High"
        }
        
        result = asyncio.run(self.benny.recommend(checkin))
        
        self.assertTrue(result["success"])
        self.assertIn("response", result)
        self.assertGreater(len(result["response"]), 0)
        
        print(f"\nRecommendation Test")
        print(f"  Check-in: {checkin}")
        print(f"  Recommendation: {result['response']}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
