from django.test import TestCase
from medtrackerapp.models import Medication, DoseLog
from django.utils import timezone
from datetime import timedelta


class MedicationModelTests(TestCase):

    def test_str_returns_name_and_dosage(self):
        med = Medication.objects.create(name="Aspirin", dosage_mg=100, prescribed_per_day=2)
        self.assertEqual(str(med), "Aspirin (100mg)")

    def test_adherence_rate_all_doses_taken(self):
        med = Medication.objects.create(name="Aspirin", dosage_mg=100, prescribed_per_day=2)

        now = timezone.now()
        DoseLog.objects.create(medication=med, taken_at=now - timedelta(hours=30))
        DoseLog.objects.create(medication=med, taken_at=now - timedelta(hours=1))

        adherence = med.adherence_rate()
        self.assertEqual(adherence, 100.0)

    def test_adherence_rate_partial(self):
        med = Medication.objects.create(name="Ibuprofen", dosage_mg=200, prescribed_per_day=2)
        now = timezone.now()
        # One taken, one missed
        DoseLog.objects.create(medication=med, taken_at=now, was_taken=True)
        DoseLog.objects.create(medication=med, taken_at=now - timedelta(hours=4), was_taken=False)
        
        self.assertEqual(med.adherence_rate(), 50.0)

    def test_adherence_rate_no_logs(self):
        med = Medication.objects.create(name="Empty", dosage_mg=10, prescribed_per_day=1)
        self.assertEqual(med.adherence_rate(), 0.0)

    def test_expected_doses_valid(self):
        med = Medication.objects.create(name="Test", dosage_mg=10, prescribed_per_day=3)
        self.assertEqual(med.expected_doses(5), 15)

    def test_expected_doses_invalid_days(self):
        med = Medication.objects.create(name="Test", dosage_mg=10, prescribed_per_day=3)
        with self.assertRaises(ValueError):
            med.expected_doses(-1)

    def test_expected_doses_invalid_schedule(self):
        med = Medication.objects.create(name="Test", dosage_mg=10, prescribed_per_day=0)
        with self.assertRaises(ValueError):
            med.expected_doses(5)

    def test_adherence_rate_over_period_valid(self):
        med = Medication.objects.create(name="PeriodTest", dosage_mg=10, prescribed_per_day=1)
        start_date = timezone.now().date() - timedelta(days=2)
        end_date = timezone.now().date()
        
        # 3 days period (start, start+1, end). Expected doses = 3 * 1 = 3.
        # Log 1: Taken inside period
        DoseLog.objects.create(medication=med, taken_at=timezone.now() - timedelta(days=1), was_taken=True)
        # Log 2: Missed inside period
        DoseLog.objects.create(medication=med, taken_at=timezone.now() - timedelta(days=2), was_taken=False)
        
        # 1 taken out of 3 expected = 33.33%
        self.assertEqual(med.adherence_rate_over_period(start_date, end_date), 33.33)

    def test_adherence_rate_over_period_invalid_dates(self):
        med = Medication.objects.create(name="Test", dosage_mg=10, prescribed_per_day=1)
        start = timezone.now().date()
        end = start - timedelta(days=1)
        with self.assertRaises(ValueError):
            med.adherence_rate_over_period(start, end)


class DoseLogModelTests(TestCase):
    
    def test_str_taken(self):
        med = Medication.objects.create(name="Aspirin", dosage_mg=100, prescribed_per_day=2)
        taken_at = timezone.now()
        log = DoseLog.objects.create(medication=med, taken_at=taken_at, was_taken=True)
        
        expected_str = f"Aspirin at {timezone.localtime(taken_at).strftime('%Y-%m-%d %H:%M')} - Taken"
        self.assertEqual(str(log), expected_str)

    def test_str_missed(self):
        med = Medication.objects.create(name="Aspirin", dosage_mg=100, prescribed_per_day=2)
        taken_at = timezone.now()
        log = DoseLog.objects.create(medication=med, taken_at=taken_at, was_taken=False)
        
        expected_str = f"Aspirin at {timezone.localtime(taken_at).strftime('%Y-%m-%d %H:%M')} - Missed"
        self.assertEqual(str(log), expected_str)