import yaml

# loads only the setting value associated with the provided key
def get(key):
    with open('UserSettings', 'r') as f:
        s = yaml.load(f)
        try:
            result = s[key]
        except():
            return None
    return result

# returns a dictionary containing all user settings
def getAll():
    with open('UserSettings', 'r') as f:
        s = yaml.load(f)
        result = s.items()
    return dict(result)


def saveAll(dict):
    with open('UserSettings', 'w') as f:
        yaml.dump(dict, f)


def save(key, value):
    with open('UserSettings', 'w') as f:
        s = yaml.load(f)
        try:
            s[key] = value;
            yaml.dump(s, f)
        except():
            return None
    return True