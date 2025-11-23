from django.test import TestCase
from unittest.mock import patch, Mock
from medtrackerapp.services import DrugInfoService
import requests

class DrugInfoServiceTests(TestCase):

    @patch('medtrackerapp.services.requests.get')
    def test_get_drug_info_success(self, mock_get):
        # Configure the mock to return a successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "openfda": {
                        "generic_name": ["ASPIRIN"],
                        "manufacturer_name": ["Bayer"]
                    },
                    "warnings": ["Do not take if allergic."],
                    "purpose": ["Pain reliever"]
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call the service method
        result = DrugInfoService.get_drug_info("aspirin")

        # Assertions
        self.assertEqual(result["name"], "ASPIRIN")
        self.assertEqual(result["manufacturer"], "Bayer")
        self.assertEqual(result["warnings"], ["Do not take if allergic."])
        self.assertEqual(result["purpose"], ["Pain reliever"])
        
        # Verify requests.get was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], DrugInfoService.BASE_URL)
        self.assertEqual(kwargs["params"], {"search": "openfda.generic_name:aspirin", "limit": 1})

    @patch('medtrackerapp.services.requests.get')
    def test_get_drug_info_api_error(self, mock_get):
        # Configure the mock to return a 500 error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # Assert that ValueError is raised
        with self.assertRaises(ValueError) as context:
            DrugInfoService.get_drug_info("aspirin")
        
        self.assertIn("OpenFDA API error: 500", str(context.exception))

    @patch('medtrackerapp.services.requests.get')
    def test_get_drug_info_no_results(self, mock_get):
        # Configure the mock to return empty results
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        # Assert that ValueError is raised
        with self.assertRaises(ValueError) as context:
            DrugInfoService.get_drug_info("unknown_drug")
            
        self.assertIn("No results found", str(context.exception))

    def test_get_drug_info_empty_name(self):
        with self.assertRaises(ValueError) as context:
            DrugInfoService.get_drug_info("")
        self.assertEqual(str(context.exception), "drug_name is required")
