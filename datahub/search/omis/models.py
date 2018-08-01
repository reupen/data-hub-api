from elasticsearch_dsl import Boolean, Date, Integer, Keyword, Text

from .. import dict_utils
from .. import dsl_utils
from ..models import BaseESModel


class Order(BaseESModel):
    """Elasticsearch representation of Order model."""

    id = Keyword()
    reference = dsl_utils.SortableCaseInsensitiveKeywordText(copy_to=['reference_trigram'])
    reference_trigram = dsl_utils.TrigramText()
    status = dsl_utils.SortableCaseInsensitiveKeywordText()
    company = dsl_utils.nested_company_field('company')
    contact = dsl_utils.nested_contact_or_adviser_partial_field('contact')
    created_by = dsl_utils.nested_contact_or_adviser_field('created_by', include_dit_team=True)
    created_on = Date()
    modified_on = Date()
    primary_market = dsl_utils.nested_id_name_field()
    sector = dsl_utils.nested_sector_field()
    uk_region = dsl_utils.nested_id_name_field()
    description = dsl_utils.EnglishText()
    contacts_not_to_approach = Text()
    further_info = Text()
    existing_agents = Text(index=False)
    delivery_date = Date()
    service_types = dsl_utils.nested_id_name_field()
    contact_email = dsl_utils.SortableCaseInsensitiveKeywordText()
    contact_phone = Keyword()
    subscribers = dsl_utils.nested_contact_or_adviser_field('subscribers', include_dit_team=True)
    assignees = dsl_utils.nested_contact_or_adviser_field('assignees', include_dit_team=True)
    po_number = Keyword(index=False)
    discount_value = Integer(index=False)
    vat_status = Keyword(index=False)
    vat_number = Keyword(index=False)
    vat_verified = Boolean(index=False)
    net_cost = Integer(index=False)
    subtotal_cost_string = Keyword()
    subtotal_cost = Integer(copy_to=['subtotal_cost_string'])
    vat_cost = Integer(index=False)
    total_cost_string = Keyword()
    total_cost = Integer(copy_to=['total_cost_string'])
    payment_due_date = Date()
    paid_on = Date()
    completed_by = dsl_utils.nested_contact_or_adviser_field('completed_by')
    completed_on = Date()
    cancelled_by = dsl_utils.nested_contact_or_adviser_field('cancelled_by')
    cancelled_on = Date()
    cancellation_reason = dsl_utils.nested_id_name_field()

    billing_company_name = Text()
    billing_contact_name = Text()
    billing_email = dsl_utils.SortableCaseInsensitiveKeywordText()
    billing_phone = dsl_utils.SortableCaseInsensitiveKeywordText()
    billing_address_1 = Text()
    billing_address_2 = Text()
    billing_address_town = dsl_utils.SortableCaseInsensitiveKeywordText()
    billing_address_county = dsl_utils.SortableCaseInsensitiveKeywordText()
    billing_address_postcode = Text()
    billing_address_country = dsl_utils.nested_id_name_field()

    MAPPINGS = {
        'id': str,
        'company': dict_utils.company_dict,
        'contact': dict_utils.contact_or_adviser_dict,
        'created_by': dict_utils.adviser_dict_with_team,
        'primary_market': dict_utils.id_name_dict,
        'sector': dict_utils.sector_dict,
        'uk_region': dict_utils.id_name_dict,
        'service_types': lambda col: [dict_utils.id_name_dict(c) for c in col.all()],
        'subscribers': lambda col: [
            dict_utils.contact_or_adviser_dict(c.adviser, include_dit_team=True) for c in col.all()
        ],
        'assignees': lambda col: [
            dict_utils.contact_or_adviser_dict(c.adviser, include_dit_team=True) for c in col.all()
        ],
        'billing_address_country': dict_utils.id_name_dict,
        'completed_by': dict_utils.contact_or_adviser_dict,
        'cancelled_by': dict_utils.contact_or_adviser_dict,
        'cancellation_reason': dict_utils.id_name_dict,
    }

    COMPUTED_MAPPINGS = {
        'payment_due_date': lambda x: x.invoice.payment_due_date if x.invoice else None,
    }

    SEARCH_FIELDS = (
        'reference_trigram',
        'company.name',
        'company.name_trigram',
        'contact.name',
        'contact.name_trigram',
        'total_cost_string',
        'subtotal_cost_string',
    )

    class Meta:
        """Default document meta data."""

        doc_type = 'order'
