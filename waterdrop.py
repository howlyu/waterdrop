# This is a sample Python script.

import codecs
import os.path
import time
from os import makedirs
from os.path import exists

import click
import sarge
import yaml
from jinja2 import Environment, FileSystemLoader

from _version import __version__
from modes.command import Command
from modes.streamx import Streamx


def check_env() -> bool:
    return True if os.getenv("WATERDROP_HOME") is not None else False


def check_table_exists_config(table) -> bool:
    return True if table in get_configure().get("tables") else False


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('current version: %s' % __version__)
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show current version.')
def cli():
    """This script make the realtime synchronized data easy with cdc. """
    pass


def get_configure(filename=os.path.join(
    os.path.dirname(__file__), "./configure.yaml")) -> dict:
    """ get the configure from YAML file"""
    filename = filename if exists(filename) or filename != '' else os.path.join(
        os.path.dirname(__file__) + "/configure.yaml")
    if filename.endswith('.yaml') or filename.endswith('.yml'):
        with codecs.open(filename, 'r', 'utf-8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    else:
        return {}


def generate_single_config(table):
    """Generate the single configure file."""
    loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader=loader)
    tpl = env.get_template('config.tpl')
    data = get_configure()
    data['table'] = table
    data['output_dir'] = os.path.join('..', data['output_dir'] + '-' + table)
    return tpl.render(data)


def append_params_to_all_script():
    config = get_configure()
    for table in config.get("tables"):
        append_params_single_script(table)
        replace_single_script(table.split('.')[0], table.split('.')[1])


def append_params_single_script(table):
    """ put the flink env parameters into the flink job script"""
    config = get_configure()
    output_dir = os.path.join(os.path.dirname(__file__), config.get("output_dir") + '-' + table)
    pipeline_name_suffix = config.get("flink_pipeline_name_suffix") if config.get(
        "flink_pipeline_name_suffix") is not None else "cdc-task-"
    cmd = "SET pipeline.name = " + pipeline_name_suffix + table + ";\\n"
    if len(config.get("flink_env_parameters")) > 0:
        cmd = cmd + "\\n".join(["SET " + p + ";" for p in config.get("flink_env_parameters")])
    if not exists(output_dir):
        return None
    try:
        p = sarge.run("sed -i '1i\%s\\n' %s" % (cmd, output_dir + "/flink-create." + table + ".sql"),
                      stderr=sarge.Capture())
        if p.returncode != 0:
            returncode = p.returncode
            stderr_text = p.stderr.text
            click.echo("Append params failed with return code %i: %s" % (returncode, stderr_text))
            return "Append params failed with return code %i: %s" % (returncode, stderr_text)
        else:
            return True
    except Exception as e:
        click.echo("Append params failed with return code : %s" % e)


def replace_single_script(dbname, table):
    """ database name add the suffix"""
    config = get_configure()
    if config.get("sinkdb_dbname_suffix") is None:
        return
    cmd = "find %s -type f -iname '*' -print0 | xargs -0 sed -i 's/`%s`/`%s`/g'" % (
        config.get("output_dir") + '-' + table, dbname, config.get("sinkdb_dbname_suffix") + dbname)
    cmd1 = "find %s -type f -iname 'flink-create*' -print0 |xargs -0 sed -i '/%s` (/,/);/ s/'\"'\"%s\"'\"/\"'\"%s\"'\"'/'" % (
        config.get("output_dir") + '-' + table, table.split(".")[1] + "_sink",
        dbname, config.get("sinkdb_dbname_suffix") + dbname)
    try:
        p = sarge.run(cmd, stderr=sarge.Capture())
        p = sarge.run(cmd1, stderr=sarge.Capture())
        if p.returncode != 0:
            returncode = p.returncode
            stderr_text = p.stderr.text
            click.echo("Replace failed with return code %i: %s" % (returncode, stderr_text))
            return "Replace failed with return code %i: %s" % (returncode, stderr_text)
        else:
            return True
    except Exception as e:
        click.echo("Replace failed with return code : %s" % e)


@cli.command("gen-all-scripts")
@click.argument("output_dir",
                default="output/",
                type=click.Path())
def generate_all_config(output_dir):
    """According to configure yaml file, generate all configs and scripts."""
    if not check_env():
        click.echo("Please set %s first." % click.style("WATERDROP_HOME", fg="red"))
        return None
    config = get_configure()
    with click.progressbar(
            length=len(config.get("tables")),
            label="Generating all config",
            show_percent=False,
            show_pos=True,
            bar_template="%(label)s  %(bar)s | %(info)s",
            fill_char=click.style("█", fg="cyan"),
            empty_char=" ",
    ) as bar:
        for table in config.get("tables"):
            config_filename = "config-" + table + ".conf"
            dump_file(output_dir + "/config/" + config_filename, generate_single_config(table))
            generate_single_script(output_dir + "/config/" + config_filename)
            append_params_single_script(table)
            replace_single_script(table.split(".")[0], table)
            bar.update(1)


def dump_file(filename, data):
    if not filename.endswith('.conf'):
        return None
    if not exists(filename):
        dirs = filename.rsplit('/', 1)[0]
        # dirs, fn = '/'.join(paths[:-1]), paths[-1]
        if not exists(dirs):
            makedirs(dirs)
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(data)


def generate_single_script(output):
    if not exists(output):
        return None
    try:
        p = sarge.run(os.getenv("WATERDROP_HOME") + "tool/starrocks-migrate-tool -c " + output,
                      stderr=sarge.Capture())
        if p.returncode != 0:
            returncode = p.returncode
            stderr_text = p.stderr.text
            click.echo("Start SMT tool failed with return code %i: %s" % (returncode, stderr_text))
            return "Start SMT tool failed with return code %i: %s" % (returncode, stderr_text)
        else:
            return True
    except Exception as e:
        click.echo("Start SMT tool failed with return code : %s" % e)


@cli.command("gen-all-tables-dorisdb")
def create_all_table_in_starrocks():
    """ Create all tables in Starrocks"""
    all_script_name = "starrocks-create.all.sql"
    config = get_configure()
    with click.progressbar(
            length=len(config.get("tables")),
            label="Creating tables in Starrocks",
            show_percent=False,
            show_pos=True,
            bar_template="%(label)s  %(bar)s | %(info)s",
            fill_char=click.style("█", fg="yellow"),
            empty_char=" ",
    ) as bar:
        for table in config.get("tables"):
            create_single_table_in_starrocks(table)
            bar.update(1)


def create_single_table_in_starrocks(table):
    """ Create table in Starrocks"""
    config = get_configure()
    output_dir = config.get("output_dir") + '-' + table
    if not exists(output_dir):
        return None
    script_dir = output_dir + "starrocks-create." + table + ".sql"
    if not exists(script_dir):
        return None
    # execute sql script in mysql
    try:
        cmd = "mysql -h%s -P%s -u%s -p%s -e 'source %s'" % (config.get("sinkdb_host"),
                                                            config.get("sinkdb_port"),
                                                            config.get("sinkdb_username"),
                                                            config.get("sinkdb_password"),
                                                            script_dir)
        p = sarge.run(cmd, stderr=sarge.Capture())
        if p.returncode != 0:
            returncode = p.returncode
            stderr_text = p.stderr.text
            click.echo("create ( %s ) failed with return code %i: %s" % (table, returncode, stderr_text))
        else:
            click.echo("create ( %s ) successed." % table)
    except Exception as e:
        click.echo("create ( %s ) failed with exception : %s" % (table, e))


@cli.command("gen-all-flink-job")
@click.argument("mode",
                default="streamx",
                required=True,
                type=click.Choice(['streamx', 'command'], case_sensitive=True))
def create_all_flink_jobs(mode):
    """create flink job in local flink cluster"""
    config = get_configure()
    mode = Streamx() if mode == "streamx" else Command()
    with click.progressbar(
            length=len(config.get("tables")),
            label="Creating flink job [%s]" % mode,
            show_percent=False,
            show_pos=True,
            bar_template="%(label)s  %(bar)s | %(info)s",
            fill_char=click.style("█", fg=(255, 12, 128)),
            empty_char=" ",
    ) as bar:
        for table in config.get("tables"):
            mode.create(table, config)
            bar.update(1)


@cli.command("workflow")
@click.option('-t', '--table',
              type=str,
              prompt='The table name [schema.table]',
              required=True,
              help='input the table name that is synchronized to Dorisdb')
@click.option('-m', '--mode',
              type=click.Choice(['streamx', 'command'], case_sensitive=True),
              prompt='Choice mode [streamx|command]',
              default='streamx',
              required=True,
              help='choice the mode of flink application execution'
              )
def workflow(table, mode):
    """
    Run all step :
        1=generate the config file,
        2=create table in starrocks,
        3=create flink job with mode
    """
    if check_table_exists_config(table):
        output_dir = get_configure().get("output_dir") + "/config/" + "config-" + table + ".conf"
        dump_file(output_dir, generate_single_config(table))
        generate_single_script(output_dir)
        if mode == "command":
            append_params_single_script(table)
        replace_single_script(table.split(".")[0], table)
        click.echo("【%s】: configure and scripts generated!" % click.style("Step1", fg="red"))

        # create table in starrocks
        create_single_table_in_starrocks(table)
        click.echo("【%s】: create table (%s) succeed!" % (click.style("Step2", fg="red"), click.style(table, fg="red")))

        # start flink application with mode
        mode = Streamx() if mode == 'streamx' else Command()
        mode.create(table, get_configure())
        click.echo("【%s】: flink job (%s) started in mode [%s]!" % (
            click.style("Step3", fg="red"), click.style(table, fg="red"), mode))
    else:
        click.echo(" table( %s ) not in the configure." % click.style(table, fg="yellow"))
