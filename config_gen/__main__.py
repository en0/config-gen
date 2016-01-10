from adapters import get_adapters
from argparse import ArgumentParser, FileType
from library import Library
from template_processor import TemplateProcessor
from os import environ, path
import logging
import sys
import urlparse


def _to_uri(path):
    return urlparse.urlunsplit(urlparse.urlsplit(path, scheme="file"))


def _confirm(prompt, confirm_value, match_case=False):
    c = raw_input(prompt)
    if match_case:
        return c == confirm_value
    else:
        return c.lower() == confirm_value.lower()


def _setup_logger(verbosity):
    _level = [
        "CRITICAL", "ERROR",
        "WARNING", "INFO",
        "DEBUG"
    ][min(max(int(verbosity or 0), 0), 4)]

    logging.basicConfig(level=_level, format="%(message)s")


def print_error(m):
    sys.stderr.write("{}\n".format(m))
    sys.stderr.flush()


def ep_init_library(library, uri):
    """Initialize a library with a default keystore.

    Warning: This will clobber an existing library if the file exists.

    Arguments:
        library: A path to store the library as.
        uri: the URI to the default keystore. (file://)
    """
    if path.exists(library):
        print "WARNING: A Library already exists!"
        print "The path you specified points to an existing library. It will"
        print "be truncated and setup as a new empty library.\n"

        if not _confirm("Do you want to continue? <Y/n>: ", 'Y', True):
            print_error("Aborting request...")
            exit()

    with open(library, 'w+r') as fp:
        logging.info("Creating library at: {}".format(library))
        _lib = Library(fp=fp)
        logging.debug("Adding default keystore at: {}".format(uri))
        _lib.add_keystore("default", "ini", uri)
        _lib.save()


def ep_add_keystore(library, name, type, uri):
    """Add a new keystore to a library.

    Arguments:
        library: The path to the library to use.
        name: A name to register this keystore under.
        type: The type of keystore to link to.
        uri: The URI to the new keystore.
    """
    logging.debug("Loading library: {}".format(library))
    lib = Library(path=library)
    logging.info("Adding new keystore: {}".format(name))
    lib.add_keystore(name, type, uri)
    lib.save()


def ep_del_keystore(library, name):
    """Remove a new keystore from a library.

    Arguments:
        library: The path to the library to use.
        name: The name of the keystore to remove.
    """
    logging.debug("Loading library: {}".format(library))
    lib = Library(path=library)
    logging.info("Removing keystore: {}".format(name))
    lib.remove_keystore(name)
    lib.save()


def ep_list_keystore(library):
    """List the available keystores in the given library.

    Arguments:
        library: The path to the library to use.
    """
    logging.debug("Loading library: {}".format(library))
    lib = Library(path=library)
    print "Keystores:"
    print "\n".join([" - {}".format(s) for s in lib.stores])


def ep_set_key_value(library, store, key, value):
    """Set a key to a value on the given store from the given library.

    Arguments:
        library: A open file pointer to the library.
        store: The name of the keystore.
        key: The name of the key.
        value: The value to set on <key>.
    """
    logging.debug("Loading library: {}".format(library.name))
    lib = Library(fp=library)
    logging.debug("Loading keystore: {}".format(store))
    ks = lib.get_keystore(store)
    logging.info("Setting value: {}={}".format(key, value))
    ks[key] = value


def ep_get_key_value(library, store, key):
    """Get a key from the given store from the given library.

    Arguments:
        library: A open file pointer to the library.
        store: The name of the keystore.
        key: The name of the key.
    """
    logging.debug("Loading library: {}".format(library.name))
    lib = Library(fp=library)
    logging.debug("Loading keystore: {}".format(store))
    ks = lib.get_keystore(store)
    print "{} = {}".format(key, ks[key])


def ep_list_keys(library, store):
    """List all keys in the given store from the given library.

    Arguments:
        library: A open file pointer to the library.
        store: The name of the keystore.
    """
    logging.debug("Loading library: {}".format(library.name))
    lib = Library(fp=library)
    logging.debug("Loading keystore: {}".format(store))
    ks = lib.get_keystore(store)
    print "Keys:"
    print "\n".join([" - {}".format(s) for s in ks])


def ep_del_key(library, store, key):
    """Remove a key from the given store from the given library.

    Arguments:
        library: A open file pointer to the library.
        store: The name of the keystore.
        key: The name of the key.
    """
    logging.debug("Loading library: {}".format(library.name))
    lib = Library(fp=library)
    logging.debug("Loading keystore: {}".format(store))
    ks = lib.get_keystore(store)
    logging.info("Removing key: {}".format(key))
    del ks[key]


def ep_dump_keystore(library, store):
    """Dump all keys and values in the given store from the given library.

    Arguments:
        library: A open file pointer to the library.
        store: The name of the keystore.
    """
    logging.debug("Loading library: {}".format(library.name))
    lib = Library(fp=library)
    logging.debug("Loading keystore: {}".format(store))
    ks = lib.get_keystore(store)
    logging.info("Dumping keys for {}".format(store))
    print "\n".join(["{} = {}".format(k, v) for k, v in ks.iteritems()])


def ep_render_template(library, store, template, output=None):
    """Render a template using the given store from the gien library.

    If output is not provided, the path identified in the template will be
    used as the output target.

    Arguments:
        library: A open file pointer to the library.
        store: The name of the keystore.
        template: A open file pointer to the template to render.
        output: A optional open file pointer to write the rendered template to.
    """
    logging.debug("Loading library: {}".format(library.name))
    lib = Library(fp=library)
    logging.debug("Loading keystore: {}".format(store))
    ks = lib.get_keystore(store)
    logging.debug("Loading template: {}".format(template.name))
    tmpl = TemplateProcessor(template)

    if output:
        logging.info("Rendering template with override: {} => {}".format(
            template.name, output
        ))
        tmpl.render_fp(ks, output)
    else:
        logging.info("Rendering template: {} => {}".format(
            template.name, tmpl.target_path
        ))
        tmpl.render_file(ks)


def main_render(args=None):
    """Render a template.

    Command line entry point. See -h for options.
    """
    _args = args or sys.argv[1:]
    ap = ArgumentParser(description="Render a template.")
    ap.add_argument(
        '-v', '--verbose',
        action="count",
        help="Set verbosity"
    )
    ap.add_argument(
        '-l', '--library',
        help="Path to the library. Default: ~/.config-lib.ini",
        type=FileType('r'),
        default=path.join(environ["HOME"], ".config-lib.ini")
    )
    ap.add_argument(
        '-s', '--store',
        help="The name of the keystore. Default: default",
        default="default"
    )
    ap.add_argument(
        '-t', '--template',
        help="Path to the template to render. Default ./config.template",
        type=FileType('r'),
        default="./config.template"
    )
    ap.add_argument(
        '-o', '--output',
        help="Override the output file to write the rendered template to.",
        type=FileType('w'),
        default=None
    )

    _opts = ap.parse_args(_args)
    exec_ep(ep_render_template, _opts)


def main_keys(args=None):
    """Manage Keystore.

    Command line entry point. See -h for options.
    """
    _args = args or sys.argv[1:]
    ap = ArgumentParser(description="Manage config-gen keystore.")
    ap.add_argument(
        '-v', '--verbose',
        action="count",
        help="Set verbosity"
    )
    ap.add_argument(
        '-l', '--library',
        help="Path to the library. Default: ~/.config-lib.ini",
        type=FileType('r'),
        default=path.join(environ["HOME"], ".config-lib.ini")
    )
    ap.add_argument(
        '-s', '--store',
        help="The name of the keystore. Default: default",
        default="default"
    )

    # Add sub parsers (set, get, del, list, dump)
    sap = ap.add_subparsers(help="Select an action.")
    ap_get = sap.add_parser(
        'get',
        help="Print the given key to the screen."
    )
    ap_set = sap.add_parser(
        'set',
        help="Set a new or existing key to the given value."
    )
    ap_del = sap.add_parser(
        'del',
        help="Remove a key from the keystore."
    )
    ap_list = sap.add_parser(
        'list',
        help="Print the names of all the keys to the screen."
    )
    ap_dump = sap.add_parser(
        'dump',
        help="Print all keys and their values to the screen."
    )

    # action: set KEY VALUE -> ep_set_key_value
    ap_set.set_defaults(fn=ep_set_key_value)
    ap_set.add_argument('key', help="The name of the key to set.")
    ap_set.add_argument('value', help="The value to set on the given key.")

    # action: get KEY -> ep_get_key_value
    ap_get.set_defaults(fn=ep_get_key_value)
    ap_get.add_argument('key', help="The name of the key to read.")

    # action: list -> ep_list_keys
    ap_list.set_defaults(fn=ep_list_keys)

    # action: del KEY -> ep_del_key
    ap_del.set_defaults(fn=ep_del_key)
    ap_del.add_argument('key', help="The name of the key to remove.")

    # action: dump -> ep_dump_keystore
    ap_dump.set_defaults(fn=ep_dump_keystore)

    _opts = ap.parse_args(_args)
    exec_ep(_opts.fn, _opts)


def main_ks(args=None):
    """Manage Library.

    Command line entry point. See -h for options.
    """
    _args = args or sys.argv[1:]
    ap = ArgumentParser(description="Manage config-gen library.")
    ap.add_argument(
        '-v', '--verbose',
        action="count",
        help="Set verbosity"
    )
    ap.add_argument(
        '-l', '--library',
        help="Path to the library. Default: ~/.config-lib.ini",
        default=path.join(environ["HOME"], ".config-lib.ini")
    )

    # Add sub parsers (add, del, list)
    sap = ap.add_subparsers(help="Select an action.")
    ap_add = sap.add_parser(
        'add',
        help="Add a new keystore to the library."
    )
    ap_del = sap.add_parser(
        'del',
        help="Remove a keystore from the library."
    )
    ap_list = sap.add_parser(
        'list',
        help="List the available keystore in the library."
    )

    # action: add NAME TYPE URI -> ep_add_keystore
    ap_add.set_defaults(fn=ep_add_keystore)
    ap_add.add_argument("name", help="Name of the new keystore.")
    ap_add.add_argument("type", help="Type of the new keystore.",
                        choices=get_adapters())
    ap_add.add_argument("uri", help="URI of the new keystore.", type=_to_uri)

    # action: del NAME -> ep_del_keystore
    ap_del.set_defaults(fn=ep_del_keystore)
    ap_del.add_argument("name", help="The name of the keystore to be removed.")

    # action: list -> ep_list_keystore
    ap_list.set_defaults(fn=ep_list_keystore)

    _opts = ap.parse_args(_args)
    exec_ep(_opts.fn, _opts)


def main_init(args=None):
    """Initialize a new library

    Command line entry point. See -h for options.
    """
    _args = args or sys.argv[1:]
    ap = ArgumentParser(
        description="Initialize a new config-gen library with a default "
                    "keystore"
    )
    ap.add_argument(
        '-v', '--verbose',
        action="count",
        help="Set verbosity"
    )
    ap.add_argument(
        '-l', '--library',
        help="Path to store the new library. Default: ~/.config-lib.ini",
        type=str,
        default=path.join(environ["HOME"], ".config-lib.ini")
    )
    ap.add_argument(
        '-u', '--uri',
        help="Override the default keystore URI. "
             "Default: file://<HOME>/.config-ks-default.ini?default",
        type=_to_uri,
        default=path.join(environ["HOME"], ".config-ks-default.ini?default")
    )

    _opts = ap.parse_args(_args)
    exec_ep(ep_init_library, _opts)


def exec_ep(fn, opts):
    params = vars(opts)

    _setup_logger(params.get("verbose", 0))

    for k in ['verbose', 'fn']:
        if k in params:
            del params[k]

    try:
        fn(**params)
    except Exception as ex:
        print_error("FAILED: {}".format(ex))
        raise


if __name__ == "__main__":
    main_render()
