def setupPloneSite():
    from Products.PloneTestCase import PloneTestCase
    PloneTestCase.installProduct('pluggablecatalog')
    PloneTestCase.setupPloneSite()
