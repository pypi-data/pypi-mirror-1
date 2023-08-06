from Products.Archetypes.atapi import *
from Products.Archetypes.Field import __all__ as ATField_all
from archetypes.schemaextender.field import ExtensionField

for klass in ATField_all:
    exec("class ef%s(ExtensionField, %s): pass" % (klass, klass))

