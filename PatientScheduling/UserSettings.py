import yaml


def get(name):
    result = None
    with open('UserSettings', 'r') as f:
        s = yaml.load(f)
        try:
            result = s[name]
        except():
            return None
    return result