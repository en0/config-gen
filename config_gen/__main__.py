import sys
from argparse import ArgumentParser, FileType
from library import Library
from keystore import Keystore
from jinja2 import Template


def list_keys(library, store, profile):
    """ List all keys in the profile """
    lib = Library(fp=library)
    ks = lib.get_keystore(store)
    return ["{}\n".format(n) for n in ks.get_keys(profile)]


def get_key(library, store, profile, key):
    """ Get a specific key in the profile """
    lib = Library(fp=library)
    ks = lib.get_keystore(store)
    yield "{}\n".format(ks.get(profile, key))


def set_key(library, store, profile, key, value):
    """ Set a specific key in the profile """
    yield "Adding key '{}' to profile {}...".format(key, profile)
    lib = Library(fp=library)
    ks = lib.get_keystore(store)
    ks.set(profile, key, value)
    ks.commit()
    yield " [SUCCESS]\n"


def list_profiles(library, store, profile):
    """ List all profiles in the library """
    lib = Library(fp=library)
    ks = lib.get_keystore(store)
    return ["{}\n".format(n) for n in ks.profiles]


def add_profile(library, store, profile, name):
    """ Add a profile to the store """
    yield "Adding profile '{}' to keystore {}...".format(name, store)
    lib = Library(fp=library)
    ks = lib.get_keystore(store)
    ks.add_profile(name)
    ks.commit()
    yield " [SUCCESS]\n"


def list_stores(library, store, profile):
    """ List all stores in the library """
    lib = Library(fp=library)
    return ["{}\n".format(n) for n in lib.stores]


def add_store(library, store, profile, name, ks_type, uri):
    """ Add a store to the library """
    yield "Adding keystore '{}'...".format(name)
    lib = Library(fp=library)
    ks = Keystore(ks_type)
    ks.load(uri)
    lib.add_keystore(name, ks)
    lib.save()
    yield " [SUCCESS]\n"


def render_template(library, store, profile, source):
    yield "Rendering template from {}/{}".format(store, profile)
    lib = Library(fp=library)
    ks = lib.get_keystore(store)
    kvp = ks.get_profile_dict(profile)

    _target = source.readline().decode('utf-8').rstrip('\n')
    t = Template(source.read().decode('utf-8'))

    with open(_target, 'w') as fp:
        fp.write(t.render(**kvp))

    yield " [SUCCESS]\n"


def get_opts(args):
    ap = ArgumentParser(description="The Configuration Management Tool")
    ap.add_argument(
        "-l", "--library",
        default=None,
        type=FileType('r')
    )
    ap.add_argument(
        "-s", "--store",
        default="DEFAULT",
        help="The name of the store.",
        type=str
    )
    ap.add_argument(
        "-p", "--profile",
        default="DEFAULT",
        help="The name of the profile.",
        type=str
    )
    sap = ap.add_subparsers(help="Select an action")

    _list_keys = sap.add_parser(
        'list-keys',
        help="List keys in the profile"
    )
    _list_keys.set_defaults(fn=list_keys)

    _get_key = sap.add_parser(
        'get-key',
        help="Get the value of a key in a profile"
    )
    _get_key.set_defaults(fn=get_key)
    _get_key.add_argument(
        "KEY",
        help="The name of the key.",
        type=str
    )

    _set_key = sap.add_parser(
        'set-key',
        help="Set the value of a key in a profile"
    )
    _set_key.set_defaults(fn=set_key)
    _set_key.add_argument(
        "KEY",
        help="The name of the key.",
        type=str
    )
    _set_key.add_argument(
        "VALUE",
        help="The value to set on the key.",
        type=str
    )

    _list_profiles = sap.add_parser(
        'list-profiles',
        help="List all available profiles for the store."
    )
    _list_profiles.set_defaults(fn=list_profiles)

    _add_profile = sap.add_parser(
        "add-profile",
        help="Add a new profile to the given store."
    )
    _add_profile.set_defaults(fn=add_profile)
    _add_profile.add_argument(
        "NAME",
        help="The name of the profile.",
        type=str
    )

    _list_stores = sap.add_parser(
        'list-stores',
        help="List all available stores in the library."
    )
    _list_stores.set_defaults(fn=list_stores)

    _add_store = sap.add_parser(
        "add-store",
        help="Add a new store to the library."
    )
    _add_store.set_defaults(fn=add_store)
    _add_store.add_argument(
        "NAME",
        help="The name of the store.",
        type=str
    )
    _add_store.add_argument(
        "TYPE",
        help="The type of the store.",
        choices=["ini"],
        type=str
    )
    _add_store.add_argument(
        "URI",
        help="The URI of new store.",
        type=str
    )

    _render_template = sap.add_parser(
        "render-template",
        help="Render a template."
    )
    _render_template.set_defaults(fn=render_template)
    _render_template.add_argument(
        "SOURCE",
        help="The path to the template to render.",
        type=FileType('r')
    )

    return ap.parse_args(args)


def main(args=None):
    """ config-gen entry point. See config-gen -h for details.  """
    _args = args or sys.argv[1:]
    opts = get_opts(_args)

    _fn = opts.fn

    # copy and format the argument list from the given options.
    _params = dict([(k.lower(), v) for k, v in vars(opts).iteritems()])

    # Delete the function refrence from the arg list
    del _params['fn']

    # rename the argument 'type' to ks_type to avoid global name issue
    if 'type' in _params:
        _params['ks_type'] = _params['type']
        del _params['type']

    try:
        for m in _fn(**_params):
            sys.stdout.write(m)
            sys.stdout.flush()

    except Exception as ex:
        if hasattr(ex, "message"):
            _message = ex.message
        else:
            _message = str(ex)
        sys.stderr.write("\nERROR: {}\n".format(_message))


def cfgen(args=None):
    """ Shortcut macro to render a template """
    _args = args or sys.argv[1:]

    if len(_args) % 2 == 0:
        _args.append("render-template")
        _args.append("config.template")
    else:
        _args.insert(len(_args)-1, "render-template")

    main(_args)

if __name__ == "__main__":
    main()
