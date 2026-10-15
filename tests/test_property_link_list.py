"""JSON references must become document objects before reaching FreeCAD."""
import importlib.util
from pathlib import Path
import sys
import types

import pytest


@pytest.fixture
def mapper(monkeypatch):
    freecad = types.ModuleType("FreeCAD")
    freecad.Document = object
    freecad.DocumentObject = object
    freecad.Vector = type("Vector", (), {})
    freecad.Console = types.SimpleNamespace(PrintError=lambda message: None)
    monkeypatch.setitem(sys.modules, "FreeCAD", freecad)
    path = Path(__file__).resolve().parents[1] / "addon/FreeCADMCP/rpc_server/property_mapper.py"
    spec = importlib.util.spec_from_file_location("_link_list_mapper_test", path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


class Target:
    PropertiesList = ["Shapes", "Group", "Tags"]

    def __init__(self, initial):
        self.Shapes = initial
        self.Group = []
        self.Tags = []

    def getTypeIdOfProperty(self, prop):
        return "App::PropertyStringList" if prop == "Tags" else "App::PropertyLinkList"

    def __setattr__(self, prop, value):
        if prop in ("Shapes", "Group") and any(isinstance(item, (str, int)) for item in value):
            raise TypeError("Type must be App.DocumentObject or None, not str")
        super().__setattr__(prop, value)


@pytest.fixture
def document():
    objects = {name: types.SimpleNamespace(Name=name) for name in ("Base", "Body")}
    return types.SimpleNamespace(getObject=objects.get), objects


@pytest.mark.parametrize("prop", ["Shapes", "Group"])
def test_resolves_link_list_by_property_type(mapper, document, prop):
    doc, objects = document
    target = Target([])
    mapper.set_object_property(doc, target, {prop: ["Body", "Base"]})
    assert getattr(target, prop) == [objects["Body"], objects["Base"]]


@pytest.mark.parametrize("value", [["Body", "Missing"], ["Body", 7], "Body", None])
def test_invalid_link_list_preserves_existing_links(mapper, document, value):
    doc, objects = document
    target = Target([objects["Base"]])
    with pytest.raises(ValueError):
        mapper.set_object_property(doc, target, {"Shapes": value})
    assert target.Shapes == [objects["Base"]]


def test_missing_reference_error_names_the_missing_object(mapper, document):
    doc, _ = document
    with pytest.raises(ValueError, match="Missing.*not found"):
        mapper.set_object_property(doc, Target([]), {"Shapes": ["Missing"]})


def test_empty_link_list_clears_links(mapper, document):
    doc, objects = document
    target = Target([objects["Base"]])
    mapper.set_object_property(doc, target, {"Shapes": []})
    assert target.Shapes == []


def test_string_list_is_not_resolved_as_links(mapper, document):
    doc, _ = document
    target = Target([])
    mapper.set_object_property(doc, target, {"Tags": ["not an object"]})
    assert target.Tags == ["not an object"]
