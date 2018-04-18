import uuid
from random import choice

import factory
from django.utils.timezone import now

from datahub.company.ch_constants import COMPANY_CATEGORY_TO_BUSINESS_TYPE_MAPPING
from datahub.company.constants import BusinessTypeConstant
from datahub.company.models import ExportExperienceCategory
from datahub.core import constants
from datahub.core.test_utils import random_country, random_foreign_country
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
    registered_address_country_id = factory.LazyFunction(random_country)
    trading_address_1 = factory.Sequence(lambda x: f'{x} Fake Lane')
    trading_address_town = 'Woodside'
    trading_address_country_id = factory.LazyAttribute(lambda o: o.registered_address_country_id)
    business_type_id = BusinessTypeConstant.private_limited_company.value.id
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


class UKCompanyFactory(CompanyFactory):
    """UK company factory."""

    registered_address_country_id = factory.LazyFunction(constants.Country.united_kingdom.value.id)


class ForeignCompanyFactory(CompanyFactory):
    """Foreign company factory."""

    registered_address_country_id = factory.LazyFunction(random_foreign_country)


def _get_random_company_category():
    categories = ([key for key, val in COMPANY_CATEGORY_TO_BUSINESS_TYPE_MAPPING.items() if val])
    return choice(categories).capitalize()


class CompaniesHouseCompanyFactory(factory.django.DjangoModelFactory):
    """Companies house company factory."""

    name = factory.Sequence(lambda n: f'name{n}')
    company_number = factory.Sequence(str)
    company_category = factory.LazyFunction(_get_random_company_category)
    registered_address_1 = factory.Sequence(lambda n: f'{n} Bar st.')
    registered_address_town = 'Rome'
    registered_address_country_id = constants.Country.united_kingdom.value.id
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
    job_title = factory.Faker('job')
    primary = True
    telephone_countrycode = '+44'
    telephone_number = '123456789'
    address_same_as_company = True
    created_on = now()
    contactable_by_email = True
    archived_documents_url_path = factory.Faker('uri_path')

    class Meta:
        model = 'company.Contact'
