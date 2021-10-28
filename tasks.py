import os, pathlib, platform, subprocess

from invoke import task
from invoke.collection import Collection
from invoke.config import Config

from scripts import config
from scripts import fingerprint
from scripts import linters
from scripts.lib import string as xstring

# Get the current working directory for the root of the project.
rootdir = pathlib.Path.cwd()

# ==============
# === Config ===
# ==============

cfgpath = os.path.join(rootdir, ".env.yaml")

if not os.path.isfile(cfgpath):
    config.generate_config(rootdir)

cfg = Config({"stage": "development"})
cfg.set_runtime_path(cfgpath)
cfg.load_runtime()

ns = Collection()
ns.configure(cfg)


@task(name="refresh")
def _refresh(context):
    # Set the current project stage
    os.environ["PROJECT_STAGE"] = context.stage

    # Set the project commit hash.
    os.environ["PROJECT_COMMIT"] = xstring.normalize(
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    )

    # Set the current operating system & CPU architecture of the current
    # development environment
    os.environ["PROJECT_SYSTEM"] = platform.system().lower()
    os.environ["PROJECT_ARCH"] = platform.machine().lower()

    if fingerprint.has_file_changed(rootdir, "package.json"):
        context.run("npm install")

    if fingerprint.has_file_changed(rootdir, "pyproject.toml"):
        context.run("poetry install")

    generate(context)


ns.add_task(_refresh)

# ===================
# === Collections ===
# ===================


# === Generate ===


# generate.all (generate)
@task(default=True, name="all")
def generate(context):
    """
    Trigger all generators.
    """
    generate_config(context)
    generate_linters(context)


generate_col = Collection("generate", generate)
ns.add_collection(generate_col)

# generate.config
@task(
    name="config",
    help={"stage": "Indicate project environment (default 'development')"},
)
def generate_config(context, stage="development"):
    """
    Generate all root level config files.
    """
    config.generate_config(rootdir, context.stage or stage)


generate_col.add_task(generate_config)


# generate.linters
@task(name="linters")
def generate_linters(context):
    """
    Copy the linters found in the `./linters` directory to the `root`,
    and `./.github/linters` directories.
    """
    linters.generate_linters(rootdir)


generate_col.add_task(generate_linters)


# === Dry ===

# dry.all (dry)
@task(pre=[_refresh], default=True, name="all")
def dry(context):
    """
    Run all `dry` tasks.
    """
    dry_release(context)
    dry_act(context)


dry_col = Collection("dry", dry)
ns.add_collection(dry_col)


# dry.release
@task(pre=[_refresh], name="release")
def dry_release(context):
    """
    Trigger a new git dry run release via `semantic-release`.
    """
    context.run("npm run release-dry-run")


dry_col.add_task(dry_release)


# dry.act.all (dry.act)
@task(pre=[_refresh], default=True, name="all")
def dry_act(context):
    """
    Trigger all Github Actions dry-runs.
    """
    dry_act_pull_request(context)
    dry_act_push(context)


dry_act_col = Collection("act", dry_act)
dry_col.add_collection(dry_act_col)


# dry.act.pull-request
@task(
    pre=[_refresh],
    name="pull-request",
    aliases=["pr"],
    help={
        "dryrun": "Enable dryrun mode",
        "job": "Run specified job",
        "list": "List available jobs",
        "verbose": "Enable verbose output",
    },
    optional=["job"],
)
def dry_act_pull_request(context, dryrun=False, job=None, list=False, verbose=False):
    """
    Trigger all `pull_request` Github Action workflows on the current branch.
    """
    flags = [
        f"--dryrun={str(dryrun).lower()}",
        f"--env DEFAULT_WORKSPACE={rootdir}",
        f"--env MEGALINTER_VOLUME_ROOT={rootdir}",
        f"--list={str(list).lower()}",
        f"--verbose={str(verbose).lower()}",
        f"--secret GITHUB_TOKEN={os.environ['GITHUB_TOKEN']}",
    ]

    if job:
        context.run(f"act pull_request --job={job} {' '.join(flags)}")
    else:
        context.run(f"act pull_request {' '.join(flags)}")


dry_act_col.add_task(dry_act_pull_request)


# dry.act.push
@task(
    pre=[_refresh],
    name="push",
    help={
        "dryrun": "Enable dryrun mode",
        "job": "Run specified job",
        "list": "List available jobs",
        "verbose": "Enable verbose output",
    },
    optional=["job"],
)
def dry_act_push(context, dryrun=False, job=None, list=False, verbose=False):
    """
    Trigger all `push` Github Action workflows on the current branch.
    """
    flags = [
        f"--dryrun={str(dryrun).lower()}",
        f"--env DEFAULT_WORKSPACE={rootdir}",
        f"--env MEGALINTER_VOLUME_ROOT={rootdir}",
        f"--list={str(list).lower()}",
        f"--verbose={str(verbose).lower()}",
        f"--secret GITHUB_TOKEN={os.environ['GITHUB_TOKEN']}",
    ]

    if job:
        context.run(f"act push --job={job} {' '.join(flags)}")
    else:
        context.run(f"act push {' '.join(flags)}")


dry_act_col.add_task(dry_act_push)


# === Init ===

# init.all (init)
@task(pre=[_refresh], default=True, name="all")
def init(context):
    """
    Run all `init` tasks.
    """
    init_git(context)
    init_tree(context)


init_col = Collection("init", init)
ns.add_collection(init_col)


# init.git
@task(pre=[_refresh], name="git")
def init_git(context):
    """
    Initialize all `git` scope modifications.
    """
    context.run("git flow init")
    context.run("git config gitflow.path.hooks .husky")


init_col.add_task(init_git)


# init.tree
@task(pre=[_refresh], name="tree")
def init_tree(context):
    """
    Create any files / directories required prior to development.
    """
    tmpdir = os.path.join(rootdir, "tmp")
    fingerprintdir = os.path.join(tmpdir, "fingerprint")
    reportdir = os.path.join(tmpdir, "report")

    dirs = [tmpdir, fingerprintdir, reportdir]

    for dir in dirs:
        pathlib.Path(dir).mkdir(parents=True, exist_ok=True)


init_col.add_task(init_tree)


# === Update ===

# update.all
@task(pre=[_refresh], default=True, name="all")
def update(context):
    """
    Run all `update` tasks.
    """
    update_niv(context)
    update_npm(context)
    update_poetry(context)


update_col = Collection("update", update)
ns.add_collection(update_col)


# update.niv
@task(pre=[_refresh], name="niv")
def update_niv(context):
    """
    Update niv dependencies.
    """
    context.run("niv update niv; niv update nixpkgs")


update_col.add_task(update_niv)


# update.npm
@task(pre=[_refresh], name="npm")
def update_npm(context):
    """
    Update npm packages.
    """
    context.run("npm run update")


update_col.add_task(update_npm)


# update.poetry
@task(pre=[_refresh], name="poetry")
def update_poetry(context):
    """
    Update python packages
    """
    context.run("poetry update")
    context.run("poetry install")


update_col.add_task(update_poetry)


# =============
# === Tasks ===
# =============


# === Clean ===


@task()
def clean(context):
    """
    Remove build artifacts, downloaded dependencies,
    and generated files.
    """
    context.run("git clean -Xdf")
    context.run("rm -rf ./.github/linters/*")


ns.add_task(clean)


# === Code ===


@task()
def code(context):
    """
    Launch Visual Studio Code.
    """
    context.run("code .")


ns.add_task(code)


# === Lint ===


@task(pre=[_refresh], help={"format": "Apply formatters and fixes in linted sources"})
def lint(context, format=False):
    """
    Run all `mega-linter` linters. Apply fixes via
    corresponding formatters via the `format` flag.
    """
    reportdir = os.path.join(rootdir, "tmp", "report")
    reportdir_remote = os.path.join("tmp", "lint", "tmp", "report")

    context.run(f"rm -rf {reportdir}")

    flags = [
        f"--env COPYPASTE_JSCPD_ARGUMENTS='--output=./tmp/report/jscpd'",
        f"--env MEGALINTER_VOLUME_ROOT={rootdir}",
        f"--env REPORT_OUTPUT_FOLDER={reportdir_remote}",
        f"--fix={str(format).lower()}",
    ]
    # Run `mega-linter` in a sub-shell to prevent instances
    # of exit failure (exit 1) from breaking subsequent commands.
    context.run(f"npm run lint -- {' '.join(flags)} &")

    # Detached head state in git after running MegaLinter
    # https://github.com/nvuillam/mega-linter/issues/604
    commit = os.environ["PROJECT_COMMIT"]
    context.run(f"git checkout -m {commit}")
    context.run(f"sudo chown -R $(whoami) {reportdir}")


ns.add_task(lint)
