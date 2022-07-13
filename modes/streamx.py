import codecs
import os
from os.path import exists

import click
import httpx
from datetime import datetime

import waterdrop
from modes.base import Base


class Streamx(Base):

    def __init__(self):
        self.sys_config = waterdrop.get_configure()
        self.url_header = self.sys_config.get("streamx_url")
        self.username = self.sys_config.get("streamx_username")
        self.password = self.sys_config.get("streamx_password")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/98.0.4758.109 Safari/537.36',
            'Authorization': self.get_token()
        }

    def __passport_signin(self) -> str:
        data = {'username': self.username,
                'password': self.password}
        token_dir = os.getenv('WATERDROP_HOME') + '.token' if os.getenv('WATERDROP_HOME') else '../.token'
        r = httpx.post(url=self.url_header + 'passport/signin', data=data)
        if r.status_code == httpx.codes.OK:
            token = r.json().get("data").get("token")
            with codecs.open(token_dir, 'w', 'utf-8') as f:
                f.write(token)
                click.echo("saved the token to (%s)" % token_dir)
            return token
        else:
            return ''

    def get_token(self) -> str:
        token_dir = os.getenv('WATERDROP_HOME') + '.token'
        if not exists(token_dir) or (
                exists(token_dir) and (
                datetime.now() - datetime.fromtimestamp(os.path.getatime(token_dir))).days >= 0.5):
            click.echo("sign in  and save the token.")
            self.__passport_signin()
        click.echo("get the token from local.")
        return str(codecs.open(token_dir, 'r', 'utf-8').readline())

    def start(self, job_id) -> bool:
        data = {'id': job_id}
        r = httpx.post(url=self.url_header + 'flink/app/start', headers=self.headers, data=data)
        if r.status_code == httpx.codes.OK:
            return True
        else:
            return False

    def create(self, table_name: str) -> bool:
        if self.sys_config is not None:
            sql_script = os.getenv("WATERDROP_HOME") + '/' + self.sys_config.get(
                "output_dir") + table_name + "/flink-create." + table_name + ".sql"
            if not exists(sql_script):
                return False
            # Check the application name
            for app in self.list():
                if self.sys_config.get("flink_pipeline_name_suffix") + table_name == app.get("jobName"):
                    click.echo("Application id (%s) / name (%s) existed!" % (app.get("id"), app.get("jobName")))
                    return False
            sql = "".join(codecs.open(sql_script, "r", "utf-8").readlines())
            # verified the sql syntax
            if self.sql_verify(sql):
                data = {'jobName': self.sys_config.get("flink_pipeline_name_suffix") + table_name,
                        'jobType': 2,
                        'executionMode': 1,
                        'versionId': 100000,
                        'flinkSql': sql,
                        'appType': 1,
                        'options': '{"parallelism.default":1,"taskmanager.numberOfTaskSlots":1}',
                        'resolveOrder': 0,
                        'restartSize': 0,
                        'description': table_name,
                        'flinkClusterId': self.sys_config.get("streamx_cluster_id"),
                        'socketId': 'ae308d32-d8cf-46a6-ac5e-9390b7fec611'}
                # r = httpx.post(url=self.url_header + 'flink/app/create', headers=self.headers, data=data)
                # if r.status_code == httpx.codes.OK:
                #     return True
                return True
            else:
                return False

    def get(self, job_id: int) -> dict:
        data = {'id': job_id}
        r = httpx.post(url=self.url_header + 'flink/app/get', headers=self.headers, data=data)
        if r.status_code == httpx.codes.OK:
            return r.json().get("data")
        else:
            return {}

    def list(self) -> list:
        r = httpx.post(url=self.url_header + 'flink/app/list', headers=self.headers)
        if r.status_code == httpx.codes.OK:
            return r.json().get("data").get("records")
        else:
            return []

    def sql_verify(self, sql: str) -> bool:
        data = {'versionId': 100000,
                'sql': sql}
        r = httpx.post(url=self.url_header + 'flink/sql/verify', headers=self.headers, data=data)
        if r.status_code == httpx.codes.OK and r.json().get("status") == 'success':
            click.echo("SQL Verify [%s]: %s" % (r.json().get("data"), r.json().get("message")))
            if r.json().get("data"):
                return True
        else:
            click.echo("SQL Verify [%s]: %s" % (r.json().get("status"), r.json().get("exception").split("\n")[0]))
            return False


def main():
    sx = Streamx()
    for i in sx.list():
        print(i.get('id'))


if __name__ == '__main__':
    main()
