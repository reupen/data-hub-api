import uuid

import factory
from django.utils.timezone import now

from datahub.company.models import ExportExperienceCategory
from datahub.core import constants
from datahub.metadata.test.factories import TeamFactory


class AdviserFactory(factory.django.DjangoModelFactory):
    """Adviser factory."""

    id = factory.LazyFunction(uuid.uuid4)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    dit_team = factory.SubFactory(TeamFactory)
    email = factory.Sequence(lambda n: f'foo-{n}@bar.com')
    contact_email = factory.Faker('email')
    telephone_number = factory.Faker('phone_number')
    date_joined = now()

    class Meta:
        model = 'company.Advisor'
        django_get_or_create = ('email', )


class CompanyFactory(factory.django.DjangoModelFactory):
    """Company factory."""

    id = factory.LazyFunction(uuid.uuid4)
    created_by = factory.SubFactory(AdviserFactory)
    modified_by = factory.SubFactory(AdviserFactory)
    name = factory.Faker('company')
    registered_address_1 = factory.Sequence(lambda n: f'{n} Foo st.')
    registered_address_town = 'London'
    registered_address_country_id = constants.Country.united_kingdom.value.id
    trading_address_1 = factory.Sequence(lambda x: f'{x} Fake Lane')
    trading_address_town = 'Woodside'
    trading_address_country_id = constants.Country.united_kingdom.value.id
    business_type_id = constants.BusinessType.private_limited_company.value.id
    sector_id = constants.Sector.aerospace_assembly_aircraft.value.id
    archived = False
    uk_region_id = constants.UKRegion.england.value.id
    export_experience_category = factory.LazyFunction(
        ExportExperienceCategory.objects.order_by('?').first
    )
    archived_documents_url_path = factory.Faker('uri_path')
    created_on = now()

    class Meta:
        model = 'company.Company'


class CompaniesHouseCompanyFactory(factory.django.DjangoModelFactory):
    """Companies house company factory."""

    name = factory.Sequence(lambda n: f'name{n}')
    company_number = factory.Sequence(str)
    registered_address_1 = factory.Sequence(lambda n: f'{n} Bar st.')
    registered_address_town = 'Rome'
    registered_address_country_id = constants.Country.italy.value.id
    incorporation_date = factory.Faker('past_date')

    class Meta:
        model = 'company.CompaniesHouseCompany'
        django_get_or_create = ('company_number', )


class ContactFactory(factory.django.DjangoModelFactory):
    """Contact factory"""

    id = factory.LazyFunction(uuid.uuid4)
    created_by = factory.SubFactory(AdviserFactory)
    modified_by = factory.SubFactory(AdviserFactory)
    title_id = constants.Title.wing_commander.value.id
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    company = factory.SubFactory(CompanyFactory)
    email = 'foo@bar.com'
    primary = True
    telephone_countrycode = '+44'
    telephone_number = '123456789'
    address_same_as_company = True
    created_on = now()
    contactable_by_email = True
    archived_documents_url_path = factory.Faker('uri_path')

    class Meta:
        model = 'company.Contact'
