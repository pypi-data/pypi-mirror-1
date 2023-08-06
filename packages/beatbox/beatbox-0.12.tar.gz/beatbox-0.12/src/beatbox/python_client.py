from _beatbox import _tPartnerNS, _tSObjectNS, _tSoapNS
from _beatbox import Client as BaseClient
from marshall import marshall
from types import TupleType, ListType
import re
import copy
from xmltramp import Namespace

_tSchemaInstanceNS = Namespace('http://www.w3.org/2001/XMLSchema-instance')
_tSchemaNS = Namespace('http://www.w3.org/2001/XMLSchema')

querytyperegx = re.compile('(?:from|FROM) (\S+)')

class SObject(object):

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def marshall(self, fieldname, xml):
        field = self.fields[fieldname]
        return field.marshall(xml)


class Client(BaseClient):

    def login(self, username, passwd):
        res = BaseClient.login(self, username, passwd)
        data = dict()
        data['passwordExpired'] = _bool(res[_tPartnerNS.passwordExpired])
        data['serverUrl'] = str(res[_tPartnerNS.serverUrl])
        data['sessionId'] = str(res[_tPartnerNS.sessionId])
        data['userId'] = str(res[_tPartnerNS.userId])
        data['userInfo'] = _extractUserInfo(res[_tPartnerNS.userInfo])
        return data

    def isConnected(self):
        """ First pass at a method to check if we're connected or not """
        if self.__conn and self.__conn._HTTPConnection__state == 'Idle':
            return True
        return False
    
    def describeGlobal(self):
        res = BaseClient.describeGlobal(self)
        data = dict()
        data['encoding'] = str(res[_tPartnerNS.encoding])
        data['maxBatchSize'] = int(str(res[_tPartnerNS.maxBatchSize]))
        data['types'] = [str(t) for t in res[_tPartnerNS.types:]]
        return data

    def describeSObjects(self, sObjectTypes):
        res = BaseClient.describeSObjects(self, sObjectTypes)
        if type(res) not in (TupleType, ListType):
            res = [res]
        data = list()
        for r in res:
            d = dict()
            d['activateable'] = _bool(r[_tPartnerNS.activateable])
            d['createable'] = _bool(r[_tPartnerNS.createable])
            d['custom'] = _bool(r[_tPartnerNS.custom])
            d['deletable'] = _bool(r[_tPartnerNS.deletable])
            fields = r[_tPartnerNS.fields:]
            fields = [_extractFieldInfo(f) for f in fields]
            field_map = dict()
            for f in fields:
                field_map[f.name] = f
            d['fields'] = field_map
            rawreldata = r[_tPartnerNS.ChildRelationships:]
            relinfo = [_extractChildRelInfo(cr) for cr in rawreldata]
            d['ChildRelationships'] = relinfo
            d['keyPrefix'] = str(r[_tPartnerNS.keyPrefix])
            d['label'] = str(r[_tPartnerNS.label])
            d['labelPlural'] = str(r[_tPartnerNS.labelPlural])
            d['layoutable'] = _bool(r[_tPartnerNS.layoutable])
            d['name'] = str(r[_tPartnerNS.name])
            d['queryable'] = _bool(r[_tPartnerNS.queryable])
            d['replicateable'] = _bool(r[_tPartnerNS.replicateable])
            d['retrieveable'] = _bool(r[_tPartnerNS.retrieveable])
            d['searchable'] = _bool(r[_tPartnerNS.searchable])
            d['undeletable'] = _bool(r[_tPartnerNS.undeletable])
            d['updateable'] = _bool(r[_tPartnerNS.updateable])
            d['urlDetail'] = str(r[_tPartnerNS.urlDetail])
            d['urlEdit'] = str(r[_tPartnerNS.urlEdit])
            d['urlNew'] = str(r[_tPartnerNS.urlNew])
            data.append(SObject(**d))
        return data

    def create(self, sObjects):
        preparedObjects = _prepareSObjects(sObjects)
        res = BaseClient.create(self, preparedObjects)
        if type(res) not in (TupleType, ListType):
            res = [res]
        data = list()
        for r in res:
            d = dict()
            data.append(d)
            d['id'] = str(r[_tPartnerNS.id])
            d['success'] = success = _bool(r[_tPartnerNS.success])
            if not success:
                d['errors'] = [_extractError(e)
                               for e in r[_tPartnerNS.errors:]]
            else:
                d['errors'] = list()
        return data

    def retrieve(self, fields, sObjectType, ids):
        resultSet = BaseClient.retrieve(self, fields, sObjectType, ids)
        type_data = self.describeSObjects(sObjectType)[0]

        if type(resultSet) not in (TupleType, ListType):
            if isnil(resultSet):
                resultSet = list()
            else:
                resultSet = [resultSet]
        fields = [f.strip() for f in fields.split(',')]
        data = list()
        for result in resultSet:
            d = dict()
            data.append(d)
            for fname in fields:
                d[fname] = type_data.marshall(fname, result)
        return data

    def update(self, sObjects):
        preparedObjects = _prepareSObjects(sObjects)
        res = BaseClient.update(self, preparedObjects)
        if type(res) not in (TupleType, ListType):
            res = [res]
        data = list()
        for r in res:
            d = dict()
            data.append(d)
            d['id'] = str(r[_tPartnerNS.id])
            d['success'] = success = _bool(r[_tPartnerNS.success])
            if not success:
                d['errors'] = [_extractError(e)
                               for e in r[_tPartnerNS.errors:]]
            else:
                d['errors'] = list()
        return data

    def query(self, fields, sObjectType, conditionExpression=''):
        type_data = self.describeSObjects(sObjectType)[0]
        queryString = 'select %s from %s' % (fields, sObjectType)
        if conditionExpression:
            queryString = '%s where %s' % (queryString, conditionExpression)
        fields = [f.strip() for f in fields.split(',')]
        res = BaseClient.query(self, queryString)
        locator = QueryLocator(str(res[_tPartnerNS.queryLocator]), type_data,
                                fields)
        data = dict(queryLocator = locator,
            done = _bool(res[_tPartnerNS.done]),
            records = [_extractRecord(type_data, fields, r)
                       for r in res[_tPartnerNS.records:]],
            size = int(str(res[_tPartnerNS.size]))
            )
        return data

    def queryMore(self, queryLocator):
        locator = queryLocator.locator
        type_data = queryLocator.type_data
        fields = queryLocator.fields
        res = BaseClient.queryMore(self, locator)
        locator = QueryLocator(str(res[_tPartnerNS.queryLocator]), type_data,
                                fields)
        data = dict(queryLocator = locator,
            done = _bool(res[_tPartnerNS.done]),
            records = [_extractRecord(type_data, fields, r)
                       for r in res[_tPartnerNS.records:]],
            size = int(str(res[_tPartnerNS.size]))
            )
        return data

    def delete(self, ids):
        res = BaseClient.delete(self, ids)
        if type(res) not in (TupleType, ListType):
            res = [res]
        data = list()
        for r in res:
            d = dict()
            data.append(d)
            d['id'] = str(r[_tPartnerNS.id])
            d['success'] = success = _bool(r[_tPartnerNS.success])
            if not success:
                d['errors'] = [_extractError(e)
                               for e in r[_tPartnerNS.errors:]]
            else:
                d['errors'] = list()
        return data

    def upsert(self, externalIdName, sObjects):
        preparedObjects = _prepareSObjects(sObjects)
        res = BaseClient.upsert(self, externalIdName, preparedObjects)
        if type(res) not in (TupleType, ListType):
            res = [res]
        data = list()
        for r in res:
            d = dict()
            data.append(d)
            d['id'] = str(r[_tPartnerNS.id])
            d['success'] = success = _bool(r[_tPartnerNS.success])
            if not success:
                d['errors'] = [_extractError(e)
                               for e in r[_tPartnerNS.errors:]]
            else:
                d['errors'] = list()
            d['isCreated'] = d['created'] = _bool(r[_tPartnerNS.created])
        return data

    def getDeleted(self, sObjectType, start, end):
        res = BaseClient.getDeleted(self, sObjectType, start, end)
        res = res[_tPartnerNS.deletedRecords:]
        if type(res) not in (TupleType, ListType):
            res = [res]
        data = list()
        for r in res:
            d = dict(
                id = str(r[_tPartnerNS.id]),
                deletedDate = marshall('datetime', 'deletedDate', r,
                ns=_tPartnerNS))
            data.append(d)
        return data

    def getUpdated(self, sObjectType, start, end):
        res = BaseClient.getUpdated(self, sObjectType, start, end)
        res = res[_tPartnerNS.ids:]
        if type(res) not in (TupleType, ListType):
            res = [res]
        return [str(r) for r in res]

    def getUserInfo(self):
        res = BaseClient.getUserInfo(self)
        data = _extractUserInfo(res)
        return data

    def describeTabs(self):
        res = BaseClient.describeTabs(self)
        data = list()
        for r in res:
            tabs = [_extractTab(t) for t in r[_tPartnerNS.tabs:]]
            d = dict(
                    label = str(r[_tPartnerNS.label]),
                    logoUrl = str(r[_tPartnerNS.logoUrl]),
                    selected = _bool(r[_tPartnerNS.selected]),
                    tabs=tabs)
        return data

    def describeLayout(self, sObjectType):
        raise NotImplementedError

class QueryLocator(object):

    def __init__(self, locator, type_data, fields):
        self.locator = locator
        self.type_data = type_data
        self.fields = fields


class Field(object):

    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self, k, v)

    def marshall(self, xml):
        return marshall(self.type, self.name, xml)


# sObjects can be 1 or a list. If values are python lists or tuples, we
# convert these to strings:
# ['one','two','three'] becomes 'one;two;three'
def _prepareSObjects(sObjects):
     def _doPrep(field_dict):
         """Salesforce expects string to be "apple;orange;pear"
            so if a field is in Python list format, convert it to string.
            We also set an array of any list-type fields that should be
            set to empty, as this is a special case in the Saleforce API,
            and merely setting the list to an empty string doesn't cause
            the values to be updated."""
         fieldsToNull = []
         for k,v in field_dict.items():
             if hasattr(v,'__iter__'):
                 if len(v) == 0:
                     fieldsToNull.append(k)
                 else:
                     field_dict[k] = ";".join(v)
         field_dict['fieldsToNull'] = fieldsToNull
     
     sObjectsCopy = copy.deepcopy(sObjects)
     if isinstance(sObjectsCopy,dict):
         _doPrep(sObjectsCopy)
     else:
         for listitems in sObjectsCopy:
             _doPrep(listitems)   
     return sObjectsCopy


def _bool(val):
    return str(val) == 'true'

def _extractFieldInfo(fdata):
    data = dict()
    data['autoNumber'] = _bool(fdata[_tPartnerNS.autoNumber])
    data['byteLength'] = int(str(fdata[_tPartnerNS.byteLength]))
    data['calculated'] = _bool(fdata[_tPartnerNS.calculated])
    data['createable'] = _bool(fdata[_tPartnerNS.createable])
    data['nillable'] = _bool(fdata[_tPartnerNS.nillable])
    data['custom'] = _bool(fdata[_tPartnerNS.custom])
    data['defaultedOnCreate'] = _bool(fdata[_tPartnerNS.defaultedOnCreate])
    data['digits'] = int(str(fdata[_tPartnerNS.digits]))
    data['filterable'] = _bool(fdata[_tPartnerNS.filterable])
    try:
        data['htmlFormatted'] = _bool(fdata[_tPartnerNS.htmlFormatted])
    except KeyError:
        data['htmlFormatted'] = False
    data['label']  = str(fdata[_tPartnerNS.label])
    data['length'] = int(str(fdata[_tPartnerNS.length]))
    data['name'] = str(fdata[_tPartnerNS.name])
    data['nameField'] = _bool(fdata[_tPartnerNS.nameField])
    plValues = fdata[_tPartnerNS.picklistValues:]
    data['picklistValues'] = [_extractPicklistEntry(p) for p in plValues]
    data['precision'] = int(str(fdata[_tPartnerNS.precision]))
    data['referenceTo'] = [str(r) for r in fdata[_tPartnerNS.referenceTo:]]
    data['restrictedPicklist'] = _bool(fdata[_tPartnerNS.restrictedPicklist])
    data['scale'] = int(str(fdata[_tPartnerNS.scale]))
    data['soapType'] = str(fdata[_tPartnerNS.soapType])
    data['type'] = str(fdata[_tPartnerNS.type])
    data['updateable'] = _bool(fdata[_tPartnerNS.updateable])
    try:
        data['dependentPicklist'] = _bool(fdata[_tPartnerNS.dependentPicklist])
        data['controllerName'] = str(fdata[_tPartnerNS.controllerName])
    except KeyError:
        data['dependentPicklist'] = False
        data['controllerName'] = ''
    return Field(**data)


def _extractPicklistEntry(pldata):
    data = dict()
    data['active'] = _bool(pldata[_tPartnerNS.active])
    data['validFor'] = [str(v) for v in pldata[_tPartnerNS.validFor:]]
    data['defaultValue'] = _bool(pldata[_tPartnerNS.defaultValue])
    data['label'] = str(pldata[_tPartnerNS.label])
    data['value'] = str(pldata[_tPartnerNS.value])
    return data


def _extractChildRelInfo(crdata):
    data = dict()
    data['cascadeDelete'] = _bool(rel[_tPartnerNS.cascadeDelete])
    data['childSObject'] = str(rel[_tPartnerNS.childSObject])
    data['field'] = str(rel[_tPartnerNS.field])
    return data


def _extractError(edata):
    data = dict()
    data['statusCode'] = str(edata[_tPartnerNS.statusCode])
    data['message'] = str(edata[_tPartnerNS.message])
    data['fields'] = [str(f) for f in edata[_tPartnerNS.fields:]]
    return data

def _extractRecord(type_data, fields, r):
    data = dict()
    for fname in fields:
        data[fname] = type_data.marshall(fname, r)
    return data

def _extractTab(tdata):
    data = dict(
            custom = _bool(tdata[_tPartnerNS.custom]),
            label = str(tdata[_tPartnerNS.label]),
            sObjectName = str(tdata[_tPartnerNS.sobjectName]),
            url = str(tdata[_tPartnerNS.url]))
    return data

def _extractUserInfo(res):
    data = dict(
            accessibilityMode = _bool(res[_tPartnerNS.accessibilityMode]),
            currencySymbol = str(res[_tPartnerNS.currencySymbol]),
            organizationId = str(res[_tPartnerNS.organizationId]),
            organizationMultiCurrency = _bool(
                    res[_tPartnerNS.organizationMultiCurrency]),
            organizationName = str(res[_tPartnerNS.organizationName]),
            userDefaultCurrencyIsoCode = str(
                    res[_tPartnerNS.userDefaultCurrencyIsoCode]),
            userEmail = str(res[_tPartnerNS.userEmail]),
            userFullName = str(res[_tPartnerNS.userFullName]),
            userId = str(res[_tPartnerNS.userId]),
            userLanguage = str(res[_tPartnerNS.userLanguage]),
            userLocale = str(res[_tPartnerNS.userLocale]),
            userTimeZone = str(res[_tPartnerNS.userTimeZone]),
            userUiSkin = str(res[_tPartnerNS.userUiSkin]))
    return data

def isnil(xml):
    try:
        if xml(_tSchemaInstanceNS.nil) == 'true':
            return True
        else:
            return False
    except KeyError:
        return False
