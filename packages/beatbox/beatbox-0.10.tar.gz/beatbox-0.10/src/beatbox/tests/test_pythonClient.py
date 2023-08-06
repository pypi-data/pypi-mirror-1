from types import DictType, StringTypes, IntType, ListType, TupleType
import unittest
import datetime

import sfconfig
import beatbox

from beatbox import SoapFaultError

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.svc = svc = beatbox.PythonClient()
        svc.login(sfconfig.USERNAME, sfconfig.PASSWORD)
        self._todelete = list()

    def tearDown(self):
        svc = self.svc
        ids = self._todelete
        if ids:
            while len(ids) > 200:
                svc.delete(ids[:200])
                ids = ids[200:]
            if ids:
                svc.delete(ids)

    def testDescribeGlobal(self):
        svc = self.svc
        res = svc.describeGlobal()
        self.assertEqual(type(res), DictType)
        self.failUnless(type(res['encoding']) in StringTypes)
        self.assertEqual(type(res['maxBatchSize']), IntType)
        self.assertEqual(type(res['types']), ListType)
        self.failUnless(len(res['types']) > 0)

    def testDescribeSObjects(self):
        svc = self.svc
        globalres = svc.describeGlobal()
        types = globalres['types']
        res = svc.describeSObjects(types[0])
        self.assertEqual(type(res), ListType)
        self.assertEqual(len(res), 1)
        res = svc.describeSObjects(types)
        self.assertEqual(len(types), len(res))

    def testCreate(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        self.failUnless(type(res) in (ListType, TupleType))
        self.failUnless(len(res) == 1)
        self.failUnless(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, FirstName, Phone, Email, Birthdate',
            'Contact', [id])
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        for k in ['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate']:
            self.assertEqual(
                data[k], contact[k])
                
        
    def testSetIntegerField(self):
    #Passes when you feed it floats, even if salesforce field is defined for 0 decimal places.  Lack of data validation in SF?
        svc = self.svc
        testField = 'Favorite_Integer__c'
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Favorite_Integer__c = -25
            )
        res = svc.create([data])
        self.failUnless(type(res) in (ListType, TupleType))
        self.failUnless(len(res) == 1)
        self.failUnless(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, FirstName, Favorite_Integer__c', 'Contact', [id])
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(data[testField], contact[testField])

    def testSetFloatField(self):
    # this fails when you have a large amount (I didn't test the #) of decimal places.
        svc = self.svc
        testField = 'Favorite_Float__c'
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Favorite_Float__c = -1.999888777
            )
        res = svc.create([data])
        self.failUnless(type(res) in (ListType, TupleType))
        self.failUnless(len(res) == 1)
        self.failUnless(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, FirstName, Favorite_Float__c', 'Contact', [id])
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(data[testField], contact[testField])
    
    def testCreatePickListMultiple(self):
         svc = self.svc
        
         data = dict(type='Contact',
             LastName='Doe',
             FirstName='John',
             Phone='123-456-7890',
             Email='john@doe.com',
             Birthdate = datetime.date(1970, 1, 4),
             Favorite_Fruit__c = ["Apple","Orange","Pear"]
             )
         res = svc.create([data])
         self.failUnless(type(res) in (ListType, TupleType))
         self.failUnless(len(res) == 1)
         self.failUnless(res[0]['success'])
         id = res[0]['id']
         self._todelete.append(id)
         contacts = svc.retrieve('LastName, FirstName, Phone, Email, Birthdate, \
             Favorite_Fruit__c', 'Contact', [id])
         self.assertEqual(len(contacts), 1)
         contact = contacts[0]
         for k in ['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate', 'Favorite_Fruit__c']:
             self.assertEqual(
                 data[k], contact[k])
            
     #def testCreatePickListMultipleWithInvalid(self):
         #""" This fails, and I guess it should(?) 
         #     SF doesn't enforce vocabularies, appearently """
         #svc = self.svc
        
         #data = dict(type='Contact',
             #LastName='Doe',
             #FirstName='John',
             #Phone='123-456-7890',
             #Email='john@doe.com',
             #Birthdate = datetime.date(1970, 1, 4),
             #Favorite_Fruit__c = ["Apple","Orange","Pear","RottenFruit"]
             #)
         #res = svc.create([data])
         #self.failUnless(type(res) in (ListType, TupleType))
         #self.failUnless(len(res) == 1)
         #self.failUnless(res[0]['success'])
         #id = res[0]['id']
         #self._todelete.append(id)
         #contacts = svc.retrieve('LastName, FirstName, Phone, Email, Birthdate, \
             #Favorite_Fruit__c', 'Contact', [id])
         #self.assertEqual(len(contacts), 1)
         #contact = contacts[0]
         #self.assertNotEqual(data['Favorite_Fruit__c'], contact['Favorite_Fruit__c'])
         #self.assertEqual(len(contact['Favorite_Fruit__c']),3)
         #for k in ['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate', 'Favorite_Fruit__c']:
             #self.assertEqual(
                 #data[k], contact[k])            

    def testFailedCreate(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = 'foo'
            )
        self.assertRaises(SoapFaultError, svc.create, data)

    def testRetrieve(self):
        svc = self.svc
        data = dict(type='Contact',
             LastName='Doe',
             FirstName='John',
             Phone='123-456-7890',
             Email='john@doe.com',
             Birthdate = datetime.date(1970, 1, 4)
             )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        typedesc = svc.describeSObjects('Contact')[0]
        fieldnames = list()
        fields = typedesc.fields.values()
        fieldnames = [f.name for f in fields]
        fieldnames = ', '.join(fieldnames)
        contacts = svc.retrieve(fieldnames, 'Contact', [id])
        self.assertEqual(len(contacts), 1)

    def testRetrieveDeleted(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create(data)
        id = res[0]['id']
        svc.delete(id)
        typedesc = svc.describeSObjects('Contact')[0]
        fieldnames = list()
        fields = typedesc.fields.values()
        fieldnames = [f.name for f in fields]
        fieldnames = ', '.join(fieldnames)
        contacts = svc.retrieve(fieldnames, 'Contact', [id])
        self.assertEqual(len(contacts), 0)
    
    def testDelete(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        id = res[0]['id']
        res = svc.delete([id])
        self.failUnless(res[0]['success'])
        contacts = svc.retrieve('LastName', 'Contact', [id])
        self.assertEqual(len(contacts), 0)
    
    def testUpdate(self):
        svc = self.svc
        originaldate = datetime.date(1970, 1, 4)
        newdate = datetime.date(1970, 1, 5)
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate=originaldate
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(contacts[0]['Birthdate'], originaldate)
        self.assertEqual(contacts[0]['LastName'], lastname)
        data = dict(type='Contact',
            Id=id,
            Birthdate = newdate)
        svc.update(data)
        contacts = svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(contacts[0]['Birthdate'], newdate)
        self.assertEqual(contacts[0]['LastName'], lastname)
    
    def testShrinkMultiPicklist(self):
        svc = self.svc
        originalList = ["Pear","Apple"]
        newList = ["Pear",]
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Favorite_Fruit__c=originalList
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),2)
        data = dict(type='Contact',
            Id=id,
            Favorite_Fruit__c=newList)
        svc.update(data)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),1)
    
    def testGrowMultiPicklist(self):
        svc = self.svc
        originalList = ["Pear","Apple"]
        newList = ["Pear", "Apple", "Orange"]
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Favorite_Fruit__c=originalList
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),2)
        data = dict(type='Contact',
            Id=id,
            Favorite_Fruit__c=newList)
        svc.update(data)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),3)
        
    def testUpdateDeleted(self):
        svc = self.svc
        originaldate = datetime.date(1970, 1, 4)
        newdate = datetime.date(1970, 1, 5)
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate=originaldate
            )
        res = svc.create(data)
        id = res[0]['id']
        svc.delete(id)
        contacts = svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(len(contacts), 0)
        data = dict(type='Contact',
            Id=id,
            Birthdate = newdate)
        res = svc.update(data)
        self.failUnless(not res[0]['success'])
        self.failUnless(len(res[0]['errors']) > 0)
    
    def testQuery(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        self._todelete.append(res[0]['id'])
        data2 = dict(type='Contact',
            LastName='Doe',
            FirstName='Jane',
            Phone='123-456-7890',
            Email='jane@doe.com',
            Birthdate = datetime.date(1972, 10, 15)
            )
        res = svc.create([data2])
        janeid = res[0]['id']
        self._todelete.append(janeid)
        res = svc.query('LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe'")
        self.assertEqual(res['size'], 2)
        res = svc.query('Id, LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe' and FirstName = 'Jane'")
        self.assertEqual(res['size'], 1)
        self.assertEqual(res['records'][0]['Id'], janeid)
    
    def testQueryDoesNotExist(self):
        res = self.svc.query('LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe'")
        self.assertEqual(res['size'], 0)
   
    def testQueryMore(self):
        svc = self.svc
        svc.batchSize = 100
        data = list()
        for x in range(250):
            data.append(dict(type='Contact',
                LastName='Doe',
                FirstName='John',
                Phone='123-456-7890',
                Email='john@doe.com',
                Birthdate = datetime.date(1970, 1, 4)
                ))
        res = svc.create(data[:200])
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = svc.create(data[200:])
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = svc.query('LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe'")
        self.failUnless(not res['done'])
        self.assertEqual(len(res['records']), 200)
        res = svc.queryMore(res['queryLocator'])
        self.failUnless(res['done'])
        self.assertEqual(len(res['records']), 50)
    
    def testGetDeleted(self):
        svc = self.svc
        startdate = datetime.datetime.utcnow()
        enddate = startdate + datetime.timedelta(seconds=61)
        data = dict(type='Contact',
                LastName='Doe',
                FirstName='John',
                Phone='123-456-7890',
                Email='john@doe.com',
                Birthdate = datetime.date(1970, 1, 4)
                )
        res = svc.create(data)
        id = res[0]['id']
        svc.delete(id)
        res = svc.getDeleted('Contact', startdate, enddate)
        self.failUnless(len(res) != 0)
        ids = [r['id'] for r in res]
        self.failUnless(id in ids)
    
    def testGetUpdated(self):
        svc = self.svc
        startdate = datetime.datetime.utcnow()
        enddate = startdate + datetime.timedelta(seconds=61)
        data = dict(type='Contact',
                LastName='Doe',
                FirstName='John',
                Phone='123-456-7890',
                Email='john@doe.com',
                Birthdate = datetime.date(1970, 1, 4)
                )
        res = svc.create(data)
        id = res[0]['id']
        self._todelete.append(id)
        data = dict(type='Contact',
                Id=id,
                FirstName='Jane')
        svc.update(data)
        res = svc.getUpdated('Contact', startdate, enddate)
        self.failUnless(id in res)
   
    def testGetUserInfo(self):
        svc = self.svc
        userinfo = svc.getUserInfo()
        self.failUnless('accessibilityMode' in userinfo)
        self.failUnless('currencySymbol' in userinfo)
        self.failUnless('organizationId' in userinfo)
        self.failUnless('organizationMultiCurrency' in userinfo)
        self.failUnless('organizationName' in userinfo)
        self.failUnless('userDefaultCurrencyIsoCode' in userinfo)
        self.failUnless('userEmail' in userinfo)
        self.failUnless('userFullName' in userinfo)
        self.failUnless('userId' in userinfo)
        self.failUnless('userLanguage' in userinfo)
        self.failUnless('userLocale' in userinfo)
        self.failUnless('userTimeZone' in userinfo)
        self.failUnless('userUiSkin' in userinfo)
   
    def testDescribeTabs(self):
        tabinfo = self.svc.describeTabs()
        for info in tabinfo:
            self.failUnless('label' in info)
            self.failUnless('logoUrl' in info)
            self.failUnless('selected' in info)
            self.failUnless('tabs' in info)
            for tab in info['tabs']:
                self.failUnless('custom' in tab)
                self.failUnless('label' in tab)
                self.failUnless('sObjectName' in tab)
                self.failUnless('url' in tab)
   
    def testDescribeLayout(self):
        svc = self.svc
        self.assertRaises(NotImplementedError, svc.describeLayout,
            'Contact')
    
    def testSetMultiPicklistToEmpty(self):
        svc = self.svc
        originalList = ["Pear","Apple"]
        newList = []
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Favorite_Fruit__c=originalList
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),2)
        data = dict(type='Contact',
            Id=id,
            Favorite_Fruit__c=newList)
        svc.update(data)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.failUnless(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),0)  
    
    def testAddToEmptyMultiPicklist(self):
        svc = self.svc
        originalList = []
        newList = ["Pear","Apple"]
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Favorite_Fruit__c=originalList
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.failUnless(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),0)
        data = dict(type='Contact',
            Id=id,
            Favorite_Fruit__c=newList)
        svc.update(data)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.failUnless(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),2)  
        
    def testIsNillableField(self):
        svc = self.svc
        res = svc.describeSObjects('Contact')
        self.assertFalse(res[0].fields['LastName'].nillable)
        self.assertTrue(res[0].fields['FirstName'].nillable)
        self.assertTrue(res[0].fields['Favorite_Fruit__c'].nillable)
        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')