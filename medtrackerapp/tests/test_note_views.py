from rest_framework.test import APITestCase
from medtrackerapp.models import Medication, Note
from django.urls import reverse
from rest_framework import status


class NoteViewTests(APITestCase):

    def setUp(self):
        self.med = Medication.objects.create(name="Aspirin", dosage_mg=100, prescribed_per_day=2)

    def test_list_notes(self):
        Note.objects.create(medication=self.med, text="First note")
        Note.objects.create(medication=self.med, text="Second note")
        
        url = reverse("note-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_note_valid(self):
        url = reverse("note-list")
        data = {"medication": self.med.id, "text": "Take with water"}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.first().text, "Take with water")

    def test_create_note_invalid_missing_text(self):
        url = reverse("note-list")
        data = {"medication": self.med.id}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_note_invalid_medication(self):
        url = reverse("note-list")
        data = {"medication": 999, "text": "Invalid medication"}
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_note(self):
        note = Note.objects.create(medication=self.med, text="Test note")
        url = reverse("note-detail", args=[note.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Test note")
        self.assertEqual(response.data["medication"], self.med.id)

    def test_delete_note(self):
        note = Note.objects.create(medication=self.med, text="To be deleted")
        url = reverse("note-detail", args=[note.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 0)

    def test_update_note_not_allowed(self):
        note = Note.objects.create(medication=self.med, text="Original text")
        url = reverse("note-detail", args=[note.id])
        data = {"medication": self.med.id, "text": "Updated text"}
        response = self.client.put(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_note_not_allowed(self):
        note = Note.objects.create(medication=self.med, text="Original text")
        url = reverse("note-detail", args=[note.id])
        data = {"text": "Updated text"}
        response = self.client.patch(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
