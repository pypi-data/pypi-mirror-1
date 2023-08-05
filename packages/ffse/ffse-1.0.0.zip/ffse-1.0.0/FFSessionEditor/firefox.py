"""Firefox utilities."""

from ConfigParser import SafeConfigParser as ConfigParser

import demjson
import os
import platform

_linux   = (platform.system() == 'Linux')
_windows = (platform.system() == 'Windows')
_mac     = (platform.system() == 'Darwin')

def get_config_path():
    """Return the Firefox config path for the current user, or None."""
    if _linux:
        root = os.getenv('HOME')
        path = '.mozilla/firefox'
    elif _windows:
        root = os.getenv('APPDATA')
        path = 'Mozilla\\Firefox'
    elif _mac:
        root = os.getenv('HOME')
        path = 'Library/Application Support/Firefox'
    else:
        # Try ~/.mozilla/firefox before giving up.
        root = os.getenv('HOME') or '.'
        path = os.path.join('.mozilla', 'firefox')
        if not os.path.isdir(os.path.join(root, path)):
            raise RuntimeError, "No information on Firefox config path for "\
                                "system %s." % platform.system()
    return os.path.join(root, path)


def fix_backslashes(s):
    """Replace forward slashes with backslashes on Windows."""
    if _windows:
        return s.replace('/', '\\')
    else:
        return s


def get_profiles():
    """Return a list of dicts of profile entries."""
    config_path = get_config_path()
    ini_path = os.path.join(config_path, 'profiles.ini')
    cfg = ConfigParser()
    cfg.read(ini_path)
    
    result = []
    index = 0
    while True:
        section = 'Profile' + str(index)
        profile = {}
        if not cfg.has_section(section):
            break
        for key, value in cfg.items(section):
            profile[key] = value
        if not ('name' in profile and 'path' in profile and 'isrelative' in
                profile):
            # TODO: warn about skipping bad profiles
            continue
        result.append(profile)

        index += 1
    # end while

    # Make all paths absolute.
    for profile in result:
        if profile['isrelative'] != 0:
            relative_path = fix_backslashes(profile['path'])
            profile['path'] = os.path.join(config_path, relative_path)
    return result


def session_load(file):
    """Return the dict or list contents of a file-like object."""
    data = file.read()
    data = data.strip()
    if not data.startswith('('):
        raise ValueError('Firefox session data is missing enclosing '\
                         'parenthesis')
    data = data[1:-1]
    return demjson.decode(data)

def session_save(obj, file):
    """Write the object to a file-like object."""
    data = demjson.encode(obj)
    file.write('(%s)' % data)

def session_extract_entries(session):
    """Extract all top-level entries into a list."""
    result = []
    for window in session['windows']:
        for tab in window['tabs']:
            for entry in tab['entries']:
                result.append(entry)
    return result


def session_remove_entry(session, e):
    """Remove an entry from a session, possibly erasing an entry and tab."""
    for window in session['windows']:
        for tab in window['tabs']:
            for entry in tab['entries']:
                if entry is e:
                    tab['entries'].remove(entry)
                    if len(tab['entries']) == 0:
                        window['tabs'].remove(tab)
                    return
    raise KeyError, "Entry %s not found" % repr(e)
