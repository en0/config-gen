from ConfigParser import ConfigParser
from config_gen import Keystore
from os.path import split
from unittest import TestCase
from uuid import uuid4
import tempfile
from config_gen import TemplateProcessor
from config_gen.adapaters import IniAdapter


class TestKeystore(TestCase):
    def setUp(self):
        self._path_template = tempfile.mktemp(".ini")
        self._path_target = tempfile.mktemp(".ini")
        self._path_off_target = tempfile.mktemp(".ini")
        self._path_keystore = tempfile.mktemp(".ini")
        self._keystore = Keystore(IniAdapter)
        self._keystore.load(self._path_keystore)

        self._VALUE1 = str(uuid4())
        self._VALUE2 = str(uuid4())
        self._VALUE3 = str(uuid4())

        self._keystore["VALUE1"] = self._VALUE1
        self._keystore["VALUE2"] = self._VALUE2
        self._keystore["VALUE3"] = self._VALUE3

        with open(self._path_template, 'w') as fp:
            fp.write("\n".join([
                self._path_target,
                "[DEFAULT]",
                "value1 = {{VALUE1}}",
                "value2 = {{VALUE2}}",
                "value3 = {{VALUE3}}"
            ]))

    def test_render_fp(self):
        with open(self._path_template, 'r') as fp:
            tp = TemplateProcessor(fp)

        with open(self._path_off_target, 'w') as fp:
            tp.render_fp(self._keystore, fp)

        cp = ConfigParser()
        cp.read(self._path_off_target)
        cp.get("DEFAULT", "VALUE1", self._VALUE1)
        cp.get("DEFAULT", "VALUE2", self._VALUE2)
        cp.get("DEFAULT", "VALUE3", self._VALUE3)

    def test_render_file(self):
        with open(self._path_template, 'r') as fp:
            tp = TemplateProcessor(fp)
        tp.render_file(self._keystore, self._path_off_target)
        cp = ConfigParser()
        cp.read(self._path_off_target)
        cp.get("DEFAULT", "VALUE1", self._VALUE1)
        cp.get("DEFAULT", "VALUE2", self._VALUE2)
        cp.get("DEFAULT", "VALUE3", self._VALUE3)

    def test_render_target(self):
        with open(self._path_template, 'r') as fp:
            tp = TemplateProcessor(fp)
        tp.render_file(self._keystore)
        cp = ConfigParser()
        cp.read(self._path_target)
        cp.get("DEFAULT", "VALUE1", self._VALUE1)
        cp.get("DEFAULT", "VALUE2", self._VALUE2)
        cp.get("DEFAULT", "VALUE3", self._VALUE3)

    def test_render_string(self):
        with open(self._path_template, 'r') as fp:
            tp = TemplateProcessor(fp)
        s = tp.render(self._keystore).split('\n')
        self.assertEqual(s[0], "[DEFAULT]")
        self.assertEqual(s[1], "value1 = {}".format(self._VALUE1))
        self.assertEqual(s[2], "value2 = {}".format(self._VALUE2))
        self.assertEqual(s[3], "value3 = {}".format(self._VALUE3))
