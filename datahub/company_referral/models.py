from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.timezone import now

from datahub.core.models import BaseModel
from datahub.core.utils import get_front_end_url


class CompanyReferral(BaseModel):
    """
    An internal referral of a company, from one adviser (the creator of the referrer)
    to another (the recipient).

    TODO:
    - add a reason closed field
    """

    class Status(models.TextChoices):
        OUTSTANDING = ('outstanding', 'Outstanding')
        CLOSED = ('closed', 'Closed')
        COMPLETE = ('complete', 'Complete')

    id = models.UUIDField(primary_key=True, default=uuid4)
    closed_by = models.ForeignKey(
        'company.Advisor',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='closed_referrals',
    )
    closed_on = models.DateTimeField(null=True, blank=True)
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='referrals',
    )
    contact = models.ForeignKey(
        'company.Contact',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='referrals',
    )
    recipient = models.ForeignKey(
        'company.Advisor',
        on_delete=models.CASCADE,
        related_name='received_referrals',
    )
    status = models.CharField(
        max_length=settings.CHAR_FIELD_MAX_LENGTH,
        choices=Status.choices,
        default=Status.OUTSTANDING,
    )
    interaction = models.OneToOneField(
        'interaction.Interaction',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    completed_by = models.ForeignKey(
        'company.Advisor',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='completed_referrals',
    )
    completed_on = models.DateTimeField(null=True, blank=True)
    subject = models.CharField(max_length=settings.CHAR_FIELD_MAX_LENGTH)
    notes = models.TextField(blank=True)

    def __str__(self):
        """Human-friendly representation (for admin etc.)."""
        return f'{self.company} – {self.subject}'

    def get_absolute_url(self):
        """URL to the object in the Data Hub internal front end."""
        return get_front_end_url(self)

    def mark_as_complete(self, interaction, user):
        """Mark this referral as complete."""
        self.status = CompanyReferral.Status.COMPLETE
        self.interaction = interaction
        self.modified_by = user
        self.completed_by = user
        self.completed_on = now()
