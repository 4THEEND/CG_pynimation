import pytest

import pynimation.io.importer as importer
import pynimation.io.exporter as exporter
from pynimation.io import BVHImporter
from pynimation.io import FBXImporter
from pynimation.io import FBXExporter


class TestImporter(importer.Importer):
    extension = "__test"

    def load(filename):
        pass


class TestExporter(exporter.Exporter):
    extension = "__test"

    def save(filename, animation):
        pass


def testFactoryImporterReturnsCorrectImplementation():
    testImporter = importer._importerFactory("__test")
    assert isinstance(testImporter, TestImporter)


def testFactoryExporterReturnsCorrectImplementation():
    testExporter = exporter._exporterFactory("__test")
    assert isinstance(testExporter, TestExporter)


def testFactoryExporterThrowsCorrectException():
    with pytest.raises(NotImplementedError, match="Exporter"):
        exporter._exporterFactory("__doesnotexist")


def testFactoryImporterThrowsCorrectException():
    with pytest.raises(NotImplementedError, match="Importer"):
        importer._importerFactory("__doesnotexist")


def testFactoryImporterReturnsBvhImporter():
    bvhImporter = importer._importerFactory("bvh")
    assert isinstance(bvhImporter, BVHImporter)


def testFactoryImporterReturnsFbxImporter():
    bvhImporter = importer._importerFactory("fbx")
    assert isinstance(bvhImporter, FBXImporter)


def testFactoryExporterReturnsFbxExporter():
    fbxExporter = exporter._exporterFactory("fbx")
    assert isinstance(fbxExporter, FBXExporter)
