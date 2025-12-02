from django.test import TestCase
from medtrackerapp.models import Medication, Note
from django.utils import timezone


class NoteModelTests(TestCase):

    def setUp(self):
        self.med = Medication.objects.create(name="Aspirin", dosage_mg=100, prescribed_per_day=2)

    def test_create_note(self):
        note = Note.objects.create(medication=self.med, text="Take with food")
        self.assertEqual(note.medication, self.med)
        self.assertEqual(note.text, "Take with food")
        self.assertIsNotNone(note.created_at)

    def test_str_representation(self):
        note = Note.objects.create(medication=self.med, text="Take with food")
        expected = f"Note for {self.med.name}: Take with food"
        self.assertEqual(str(note), expected)

    def test_ordering(self):
        note1 = Note.objects.create(medication=self.med, text="First note")
        note2 = Note.objects.create(medication=self.med, text="Second note")
        notes = Note.objects.all()
        self.assertEqual(notes[0], note2)  # Most recent first
        self.assertEqual(notes[1], note1)
