import json, jsonmerge, os, sys, yaml

from scripts.lib import env as xenv
from scripts.lib import file as xfile


def generate_config(rootdir, stage="development"):
    # Settings directory
    settingsdir = os.path.join(rootdir, "settings")

    # Combine the default, project stage, and tool version settings
    # into a global configuration file: .env.json.
    default_settings_path = os.path.join(settingsdir, "default.json")
    default_settings_str = xfile.get(default_settings_path)
    default_settings_json = json.loads(default_settings_str)

    stage_settings_path = os.path.join(settingsdir, "{}.json".format(stage))
    stage_settings_str = xfile.get(stage_settings_path)
    stage_settings_json = json.loads(stage_settings_str)

    tools_path = os.path.join(rootdir, ".tools.json")
    tools_str = xfile.get(tools_path)
    tools_json = json.loads(tools_str)

    settings_json = jsonmerge.merge(default_settings_json, stage_settings_json)
    settings_json = jsonmerge.merge(settings_json, tools_json)

    settings_json_str = json.dumps(settings_json, indent=4, sort_keys=True)
    settings_json_path = os.path.join(rootdir, ".env.json")
    if os.path.exists(settings_json_path):
        xfile.overwrite(settings_json_path, settings_json_str)
    else:
        xfile.write(settings_json_path, settings_json_str)

    # Create the following `yaml` settings files:
    # - .env.yaml
    # - invoke.yaml
    settings_yaml = yaml.load(settings_json_str, Loader=yaml.SafeLoader)
    settings_yaml_str = yaml.dump(settings_yaml)
    settings_yaml_path = os.path.join(rootdir, ".env.yaml")
    if os.path.exists(settings_yaml_path):
        xfile.overwrite(settings_yaml_path, settings_yaml_str)
    else:
        xfile.write(settings_yaml_path, settings_yaml_str)

    # Create the following dotenv files:
    # - .env
    settings_env_str = xenv.json2env(settings_json_str)
    settings_env_path = os.path.join(rootdir, ".env")
    if os.path.exists(settings_env_path):
        xfile.overwrite(settings_env_path, settings_env_str)


if __name__ == "__main__":
    # The full path of the project's root directory
    rootdir = sys.argv[1]

    # The current stage of the project, either: 'development', 'staging', or
    # 'production'
    stage = sys.argv[2]

    generate_config(rootdir, stage)
