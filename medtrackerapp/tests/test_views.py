from rest_framework.test import APITestCase
from medtrackerapp.models import Medication, DoseLog
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta


class MedicationViewTests(APITestCase):
    def setUp(self):
        self.med = Medication.objects.create(name="Aspirin", dosage_mg=100, prescribed_per_day=2)

    def test_list_medications_valid_data(self):
        url = reverse("medication-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Aspirin")
        self.assertEqual(response.data[0]["dosage_mg"], 100)

    def test_create_medication_valid(self):
        url = reverse("medication-list")
        data = {"name": "Ibuprofen", "dosage_mg": 200, "prescribed_per_day": 3}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Medication.objects.count(), 2)
        self.assertEqual(Medication.objects.get(name="Ibuprofen").dosage_mg, 200)

    def test_create_medication_invalid(self):
        url = reverse("medication-list")
        # Missing required field 'dosage_mg'
        data = {"name": "Incomplete Med", "prescribed_per_day": 1}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_medication(self):
        url = reverse("medication-detail", args=[self.med.id])
        data = {"name": "Aspirin Updated", "dosage_mg": 150, "prescribed_per_day": 2}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.med.refresh_from_db()
        self.assertEqual(self.med.name, "Aspirin Updated")
        self.assertEqual(self.med.dosage_mg, 150)

    def test_delete_medication(self):
        url = reverse("medication-detail", args=[self.med.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Medication.objects.count(), 0)

    @patch("medtrackerapp.models.DrugInfoService.get_drug_info")
    def test_get_external_info_success(self, mock_get_info):
        mock_get_info.return_value = {"active_ingredient": "ASPIRIN"}
        url = reverse("medication-get-external-info", args=[self.med.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"active_ingredient": "ASPIRIN"})

    @patch("medtrackerapp.models.DrugInfoService.get_drug_info")
    def test_get_external_info_failure(self, mock_get_info):
        mock_get_info.side_effect = Exception("API Error")
        url = reverse("medication-get-external-info", args=[self.med.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("error", response.data)

    def test_expected_doses_valid(self):
        url = reverse("medication-expected-doses", args=[self.med.id])
        response = self.client.get(url, {"days": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["medication_id"], self.med.id)
        self.assertEqual(response.data["days"], 5)
        self.assertEqual(response.data["expected_doses"], 10)  # 5 days * 2 per day

    def test_expected_doses_missing_parameter(self):
        url = reverse("medication-expected-doses", args=[self.med.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expected_doses_invalid_parameter_non_integer(self):
        url = reverse("medication-expected-doses", args=[self.med.id])
        response = self.client.get(url, {"days": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expected_doses_invalid_parameter_negative(self):
        url = reverse("medication-expected-doses", args=[self.med.id])
        response = self.client.get(url, {"days": -1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expected_doses_invalid_parameter_zero(self):
        url = reverse("medication-expected-doses", args=[self.med.id])
        response = self.client.get(url, {"days": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["expected_doses"], 0)


class DoseLogViewTests(APITestCase):
    def setUp(self):
        self.med = Medication.objects.create(name="Test Med", dosage_mg=50, prescribed_per_day=1)
        self.log_url = reverse("doselog-list")

    def test_create_log_valid(self):
        data = {
            "medication": self.med.id,
            "taken_at": timezone.now(),
            "was_taken": True
        }
        response = self.client.post(self.log_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoseLog.objects.count(), 1)

    def test_create_log_invalid_medication(self):
        data = {
            "medication": 999,  # Non-existent ID
            "taken_at": timezone.now(),
            "was_taken": True
        }
        response = self.client.post(self.log_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_logs_valid(self):
        now = timezone.now()
        # Create logs
        DoseLog.objects.create(medication=self.med, taken_at=now - timedelta(days=5))
        DoseLog.objects.create(medication=self.med, taken_at=now - timedelta(days=2))
        DoseLog.objects.create(medication=self.med, taken_at=now)

        url = reverse("doselog-filter-by-date")
        # Filter for the last 3 days (should include today and 2 days ago)
        start = (now - timedelta(days=3)).date()
        end = now.date()
        response = self.client.get(url, {"start": start, "end": end})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_logs_missing_params(self):
        url = reverse("doselog-filter-by-date")
        response = self.client.get(url)  # No params
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_filter_logs_invalid_dates(self):
        url = reverse("doselog-filter-by-date")
        response = self.client.get(url, {"start": "invalid-date", "end": "2023-10-10"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
