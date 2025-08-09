import yaml

def load_mapping(config_path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config["template_columns"], config["mapping"]