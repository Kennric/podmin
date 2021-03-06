# import the signal handlers here so they will be available before models
import handlers # noqa

# If you change this version, change it also in docs/conf.py
# Packging guide: http://guide.python-distribute.org/quickstart.html
__version_info__ = {
    "major": 0,
    "minor": 2,
    "micro": 0,
    "releaselevel": "alpha",
    "serial": 0,
}


def get_version():
    vers = ["{major}.{minor}".format(**__version_info__)]

    if __version_info__["micro"]:
        vers.append(".{micro}".format(**__version_info__))
    if __version_info__["releaselevel"] != "final":
        vers.append("{releaselevel}{serial}".format(**__version_info__))
    return "".join(vers)


__version__ = get_version()


def get_name():
    return 'Podmin'
