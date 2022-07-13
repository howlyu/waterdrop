import codecs
import os
from os.path import exists

import click
import sarge

import waterdrop
from modes.base import Base


class Command(Base):
    def __init__(self):
        self.sys_config = waterdrop.get_configure()
        self.flink_home = os.getenv("FLINK_HOME") if os.getenv("FLINK_HOME") else "~/.local/flink/"

    def start(self, job_id: int):
        pass

    def stop(self, job_id: int):
        pass

    def list(self):
        """List all of flink application"""
        try:
            p = sarge.run(self.flink_home + "/bin/flink list", stderr=sarge.Capture())
            if p.returncode != 0:
                returncode = p.returncode
                stderr_text = p.stderr.text
                click.echo(
                    "flink list failed with return code %i: %s" % (returncode, stderr_text))
            else:
                click.echo("flink list successed.")
        except Exception as e:
            click.echo("flink list failed with excepton: %s" % e)

    def cancel(self, job_id: int, job_name: str):
        """Kill the flink job"""
        try:
            p = sarge.run("flink list|grep '%s'|awk -F ':' '{print $4}'|xargs -i flink cancel {}" % job_name,
                          stderr=sarge.Capture())
            if p.returncode != 0:
                returncode = p.returncode
                stderr_text = p.stderr.text
                click.echo(
                    "kill (%s) failed with return code %i: %s" % (job_name, returncode, stderr_text))
            else:
                click.echo("kill (%s)  successed." % job_name)
        except Exception as e:
            click.echo("kill (%s)  failed with excepton: %s" % (job_name, e))

    def create(self, table_name: str):
        """According to the table name, startup the flink job. """
        sql_script = self.sys_config.get("output_dir") + table_name + "/flink-create." + table_name + ".sql"
        if not exists(sql_script):
            click.echo("Directory (%s) not exist!" % sql_script)
            return None
        # execute flink job task
        try:
            p = sarge.run(self.flink_home + "/bin/sql-client.sh -f" + sql_script,
                          stderr=sarge.Capture())
            if p.returncode != 0:
                returncode = p.returncode
                stderr_text = p.stderr.text
                click.echo(
                    "create flink job ( %s ) failed with return code %i: %s" % (table_name, returncode, stderr_text))
            else:
                click.echo("create flink job ( %s ) successed." % table_name)
        except Exception as e:
            click.echo("create flink job ( %s ) failed with excepton: %s" % (table_name, e))
