from django.db import models
from datetime import date as _date
from django.utils import timezone
from .services import DrugInfoService


class Medication(models.Model):
    """
    Represents a prescribed medication with dosage and daily schedule.

    Each Medication instance can have multiple associated DoseLog
    entries that record when doses were taken or missed.
    """
        
    name = models.CharField(max_length=100)
    dosage_mg = models.PositiveIntegerField()
    prescribed_per_day = models.PositiveIntegerField(help_text="Expected number of doses per day")

    def __str__(self):
        """Return a human-readable representation of the medication."""
        return f"{self.name} ({self.dosage_mg}mg)"

    def adherence_rate(self):
        """
        Calculate the overall adherence rate for this medication.

        The adherence rate is the percentage of all recorded doses that
        were marked as taken. Rounded to two decimals.

        Returns:
            float: Adherence percentage between 0.0 and 100.0.
        """
        logs = self.doselog_set.all()
        if not logs.exists():
            return 0.0
        taken = logs.filter(was_taken=True).count()
        return round((taken / logs.count()) * 100, 2)

    def expected_doses(self, days: int) -> int:
        """
        Compute the expected number of doses to be taken over a given number of days.

        Args:
            days (int): Number of calendar days (must be ≥ 0).

        Returns:
            int: Expected dose count for the period.

        Raises:
            ValueError: If days < 0 or prescribed_per_day ≤ 0.
        """
        if days < 0 or self.prescribed_per_day <= 0:
            raise ValueError("Days and schedule must be positive.")
        return days * self.prescribed_per_day

    def adherence_rate_over_period(self, start_date: _date, end_date: _date) -> float:
        """
        Calculate adherence rate between two dates (inclusive).

        The method counts doses taken (was_taken=True) between the given
        start and end dates and compares them to the expected number
        based on the prescription schedule.

        Args:
            start_date (date): Start of the evaluation period.
            end_date (date): End of the evaluation period.

        Returns:
            float: Adherence percentage rounded to two decimals.
                   Returns 0.0 if there are no expected doses.

        Raises:
            ValueError: If start_date > end_date.
        """
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        logs = self.doselog_set.filter(
            taken_at__date__gte=start_date,
            taken_at__date__lte=end_date
        )
        days = (end_date - start_date).days + 1
        expected = self.expected_doses(days)

        if expected == 0:
            return 0.0

        taken = logs.filter(was_taken=True).count()
        adherence = (taken / expected) * 100
        return round(adherence, 2)

    def fetch_external_info(self):
        """
        Retrieve additional drug information from an external API.

        Uses the `DrugInfoService` to query OpenFDA for details
        about this medication's active ingredient or related data.

        Returns:
            dict: Drug information data, or {'error': message} if the
                  request fails or the API is unavailable.
        """
        try:
            return DrugInfoService.get_drug_info(self.name)
        except Exception as exc:
            return {"error": str(exc)}


class DoseLog(models.Model):
    """
    Records the administration of a medication dose.

    Each DoseLog entry corresponds to a specific date/time when the
    medication was either taken or missed.
    """
        
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    taken_at = models.DateTimeField()
    was_taken = models.BooleanField(default=True)

    class Meta:
        """Metadata options for the DoseLog model."""
        ordering = ["-taken_at"]

    def __str__(self):
        """Return a human-readable description of the dose event."""
        status = "Taken" if self.was_taken else "Missed"
        when = timezone.localtime(self.taken_at).strftime("%Y-%m-%d %H:%M")
        return f"{self.medication.name} at {when} - {status}"
