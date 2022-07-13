from unittest import TestCase

from modes.streamx import Streamx


class TestStreamx(TestCase):
    sx = Streamx()

    def test_create(self):
        assert self.sx.create('cdcdemo.table1')
        assert 1 == 1

    def test_list(self):
        assert len(self.sx.list()) > 0

    def test_sql_verify(self):
        sql1 = """
        CREATE DATABASE IF NOT EXISTS `default_catalog`.`cdcdemo`;

        CREATE TABLE IF NOT EXISTS `default_catalog`.`cdcdemo`.`table1_src` (
          `age` INT NOT NULL,
          `name` STRING NOT NULL,
          PRIMARY KEY(`age`)
         NOT ENFORCED
        ) with (
          'hostname' = '192.168.30.130',
          'port' = '3306',
          'username' = 'flinkcdc',
          'password' = 'flinkcdc',
          'database-name' = 'cdcdemo',
          'table-name' = 'table1',
          'connector' = 'mysql-cdc'
        );
        
        CREATE TABLE IF NOT EXISTS `default_catalog`.`cdcdemo`.`table1_sink` (
          `age` INT NOT NULL,
          `name` STRING NOT NULL,
          PRIMARY KEY(`age`)
         NOT ENFORCED
        ) with (
          'jdbc-url' = 'jdbc:mysql://192.168.30.134:9030',
          'load-url' = '192.168.30.134:8030',
          'sink.max-retries' = '10',
          'sink.properties.format' = 'json',
          'table-name' = 'table1',
          'password' = 'sailingdw',
          'sink.properties.strip_outer_array' = 'true', 
          'username' = 'sailingdw',
          'sink.buffer-flush.interval-ms' = '15000',
          'connector' = 'starrocks',
          'database-name' = 'cdcdemo'
        );

        INSERT INTO `default_catalog`.`cdcdemo`.`table1_sink` SELECT * FROM `default_catalog`.`cdcdemo`.`table1_src`;
        """
        sql2 = """
        INSERT INTO `default_catalog`.`cdcdemo`.`table1_sink` SELECT * FROM `default_catalog`.`cdcdemo`.`table1_src`;"""

        assert not self.sx.sql_verify(sql1)
        assert self.sx.sql_verify(sql2)
