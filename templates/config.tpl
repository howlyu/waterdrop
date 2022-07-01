[db]
host = {{ sourcedb_host }}
port = {{ sourcedb_port }}
user = {{ sourcedb_user }}
password = {{ sourcedb_password }}
# currently available types: `mysql`, `pgsql`, `oracle`, `hive`, `clickhouse`, `sqlserver`, `tidb`
type = mysql
# # only takes effect on `type == hive`. 
# # Available values: kerberos, none, nosasl, kerberos_http, none_http, zk, ldap
# authentication = kerberos

[other]
# number of backends in StarRocks
be_num = 3
# `decimal_v3` is supported since StarRocks-1.8.1
use_decimal_v3 = true
# directory to save the converted DDL SQL
output_dir = {{ output_dir }}


# !!!`database` `table` `schema` are case sensitive in `oracle`!!!
[table-rule.{{ table.split('.')[0] }}.{{ table.split('.')[1] }}]
{# # pattern to match databases for setting properties -#}
{# # !!! database should be a `whole instance(or pdb) name` but not a regex when it comes with an `oracle db` !!! -#}
database = ^{{  table.split('.')[0]  }}$
{# # pattern to match tables for setting properties -#}
table = ^{{ table.split('.')[1] }}$
{# #`schema` only takes effect on `postgresql` and `oracle` and `sqlserver` -#}
schema = ^public$

############################################
### starrocks table configurations
############################################
# # set a column as the partition_key
# partition_key = p_key
# # override the auto-generated partitions
# partitions = START ("2021-01-02") END ("2021-01-04") EVERY (INTERVAL 1 day)
# # only take effect on tables without primary keys or unique indexes
# duplicate_keys=k1,k2
# # override the auto-generated distributed keys
# distributed_by=k1,k2
# # override the auto-generated distributed buckets
# bucket_num=32
# # properties.xxxxx: properties used to create tables
# properties.in_memory = false

############################################
### flink sink configurations
### DO NOT set `connector`, `table-name`, `database-name`, they are auto-generated
############################################
flink.starrocks.jdbc-url={{ sinkdb_jdbcurl }}
flink.starrocks.load-url={{ sinkdb_loadurl }}
flink.starrocks.username={{ sinkdb_username }}
flink.starrocks.password={{ sinkdb_password }}
flink.starrocks.sink.max-retries=10
flink.starrocks.sink.buffer-flush.interval-ms=15000
flink.starrocks.sink.properties.format=json
flink.starrocks.sink.properties.strip_outer_array=true
# # used to set the server-id for mysql-cdc jobs instead of using a random server-id
# flink.cdc.server-id = 5000

############################################
### flink-cdc configuration for `tidb`
############################################
# # Only takes effect on TiDB before v4.0.0. 
# # TiKV cluster's PD address.
# flink.cdc.pd-addresses = 127.0.0.1:2379

############################################
### flink-cdc plugin configuration for `postgresql`
############################################
# # for `9.*` decoderbufs, wal2json, wal2json_rds, wal2json_streaming, wal2json_rds_streaming
# # refer to https://ververica.github.io/flink-cdc-connectors/master/content/connectors/postgres-cdc.html 
# # and https://debezium.io/documentation/reference/postgres-plugins.html
# flink.cdc.decoding.plugin.name = decoderbufs