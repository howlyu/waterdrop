from os.path import exists
import waterdrop
import pytest


class TestCase:
    def __init__(self):
        self.config_key = ['sinkdb_jdbcurl', 'sinkdb_loadurl', 'sinkdb_host', 'sinkdb_port', 'sinkdb_username',
                           'output_dir',
                           'sourcedb_host', 'sourcedb_port', 'sourcedb_user', 'sourcedb_password', 'tables']
        self.config = waterdrop.get_configure('configure.yaml')

    def test_get_configure(self):
        pytest.assume(1 == 1)
        assert waterdrop.get_configure('../configure.ini') == {}
        assert waterdrop.get_configure('') is not None
        assert all([key in self.config.keys() for key in self.config_key])

    @pytest.mark.parametrize('table',
                             ['cdcdemo.table1', 'cdcdemo.table2'])
    def test_generate_single_config(self, table):
        pytest.assume(waterdrop.generate_single_config(table) is not None)

    # @pytest.mark.parametrize("table_input, table_expected",
    #                          [('cdcdemo.table1', None), ('cdcdemo.table2', None), ('cdcdemo.table3', None)])
    # def test_append_params_to_single_script(self, table_input, table_expected):
    #     pytest.assume(waterdrop.append_params_single_script(table_input) == table_expected)
