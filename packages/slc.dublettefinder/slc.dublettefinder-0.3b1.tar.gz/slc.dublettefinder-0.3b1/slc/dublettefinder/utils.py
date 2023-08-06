from Products.Archetypes.Field import __all__ as ATField_all

for klass in ATField_all:
    exec("class ef%s(ExtensionField, %s): pass" % (klass, klass))

