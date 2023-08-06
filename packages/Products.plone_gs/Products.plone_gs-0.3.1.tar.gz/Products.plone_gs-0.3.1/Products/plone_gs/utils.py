from OFS.PropertyManager import PropertyManager

def patchClassAsPropertyManager(klass, properties):
    # Monkey patch to allow easier export / import
    if not issubclass(klass, PropertyManager):
        klass._properties = properties
        klass.getProperty = PropertyManager.getProperty.im_func
        klass.getPropertyType = PropertyManager.getPropertyType.im_func
        klass.hasProperty = PropertyManager.hasProperty.im_func
        klass.propdict = PropertyManager.propdict.im_func
        klass._propertyMap = PropertyManager._propertyMap.im_func
        klass._setProperty = PropertyManager._setProperty.im_func
        klass._setPropValue = PropertyManager._setPropValue.im_func
        klass._updateProperty = PropertyManager._updateProperty.im_func
        klass._wrapperCheck = PropertyManager._wrapperCheck.im_func
    else:
        current = [x['id'] for x in klass._properties]
        to_add = []
        for i, required in enumerate(properties):
            if required['id'] not in current:
                to_add.append(required)
        if to_add:
            klass._properties += tuple(to_add)
