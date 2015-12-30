from config_gen import Library, Keystore
from os.path import split
from unittest import TestCase
import tempfile
from ConfigParser import SafeConfigParser
from config_gen.exception import KeystoreExistsException


class TestLibrary(TestCase):

    def setUp(self):
        self._path = tempfile.mktemp(".ini")
        self._ini_path = tempfile.mktemp(".ini")
        self._ini_uri = "file://{}".format("/".join(split(self._ini_path)))

    def test_create_library(self):
        lib = Library(self._path)
        _cp = SafeConfigParser()
        _cp.read(self._path)
        # If it didn't error, it worked
        self.assertIsInstance(lib, Library)

    def test_create_library_and_add_keystore(self):
        ks = Keystore("ini")
        ks.commit(self._ini_uri)
        lib = Library(self._path)
        lib.add_keystore("default", ks)
        lib.save()

        _cp = SafeConfigParser()
        _cp.read(self._path)
        self.assertEqual(_cp.get("DEFAULT", "uri"), self._ini_uri)

    def test_read_library(self):
        ks = Keystore("ini")
        ks.commit(self._ini_uri)
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "type = {}\n".format(ks.ks_type),
                "uri = {}\n".format(ks.uri),
            ])
        lib = Library(self._path)
        ks1 = lib.get_keystore("default")
        self.assertEqual(ks1.ks_type, ks.ks_type)
        self.assertEqual(ks1.uri, ks.uri)
        self.assertEqual(self._ini_uri, ks1.uri)

    def test_add_keystore(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
            ])

        lib = Library(self._path)
        ks = Keystore("ini")
        ks.commit(self._ini_uri)

        lib.add_keystore("my_store", ks)
        lib.save()

        _cp = SafeConfigParser()
        _cp.read(self._path)
        self.assertEqual(_cp.get("MY_STORE", "uri"), self._ini_uri)

    def test_load_keystore_from_cache(self):
        lib = Library(self._path)
        ks = Keystore("ini")
        ks.commit(self._ini_uri)
        lib.add_keystore("my_store", ks)
        ks1 = lib.get_keystore("my_store")
        self.assertIs(ks, ks1)

    def test_add_existing_keystore(self):
        lib = Library(self._path)
        ks = Keystore("ini")
        ks.commit(self._ini_uri)
        lib.add_keystore("my_store", ks)
        self.assertRaises(
            KeystoreExistsException,
            lib.add_keystore,
            "my_store", None
        )

    def test_list_stores(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "[STORE1]\n",
                "[STORE2]\n",
                "[STORE3]\n",
            ])

        lib = Library(self._path)
        self.assertListEqual(["store1", "store2", "store3"], lib.stores)

    def test_list_stores_with_default(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "type = ini\n",
                "uri = /dev/null\n",
                "[STORE1]\n",
                "[STORE2]\n",
                "[STORE3]\n",
            ])

        lib = Library(self._path)
        self.assertListEqual([
            "default",
            "store1",
            "store2",
            "store3"
        ], lib.stores)

    def test_read_file_pointer(self):
        with open(self._path, 'w') as fid:
            fid.writelines([
                "[DEFAULT]\n",
                "[STORE1]\n",
                "[STORE2]\n",
                "[STORE3]\n",
            ])

        with open(self._path, 'r') as fid:
            lib = Library(fp=fid)
            self.assertListEqual(["store1", "store2", "store3"], lib.stores)
