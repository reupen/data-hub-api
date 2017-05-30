from unittest.mock import MagicMock, Mock

from datahub.core.validate_utils import UpdatedDataView


def test_get_value_instance():
    """Tests getting a simple value from an instance."""
    instance = Mock(field1=1, field2=2)
    data = {'field2': 456}
    data_view = UpdatedDataView(instance, data)
    assert data_view.get_value('field1') == 1


def test_get_value_data():
    """Tests getting a simple value from update data."""
    instance = Mock(field1=1, field2=2)
    data = {'field2': 456}
    data_view = UpdatedDataView(instance, data)
    assert data_view.get_value('field2') == 456


def test_get_value_to_many_instance():
    """Tests getting a to-many value from an instance."""
    instance = Mock(field1=MagicMock())
    instance.field1.all.return_value = [123]
    data_view = UpdatedDataView(instance, None)
    assert data_view.get_value_to_many('field1') == [123]


def test_get_value_to_many_data():
    """Tests getting a to-many value from update data."""
    instance = Mock(field1=MagicMock())
    data = {'field1': [123]}
    data_view = UpdatedDataView(instance, data)
    assert data_view.get_value_to_many('field1') == data['field1']


def test_get_value_id_instance():
    """Tests getting a foreign key from an instance."""
    subinstance = Mock()
    subinstance.id = 1234
    instance = Mock(field1=subinstance)
    data_view = UpdatedDataView(instance, None)
    assert data_view.get_value_id('field1') == str(subinstance.id)


def test_get_value_id_value():
    """Tests getting a foreign key from update data."""
    subinstance = Mock()
    subinstance.id = 1234
    new_subinstance = Mock()
    new_subinstance.id = 456
    instance = Mock(field1=subinstance)
    data_view = UpdatedDataView(instance, {'field1': new_subinstance})
    assert data_view.get_value_id('field1') == str(new_subinstance.id)
