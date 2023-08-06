=========================================================
International Bank Account Number (IBAN) library
=========================================================

The international bank account number (IBAN) consists basically of the
following items:

1) two-letter Country ISO-Code (e.g. 'US', 'DE')
2) two-digit IBAN-Checksum (basically a mod(97))
3) Bank Code (The domestic bank code)
4) Branch Code (For national branches of a bank)
5) Account Number (Bank specific)
6) Bank specific check sum (often part of the account number)

The international bank code (BIC) is NOT part of the IBAN.

The above items are simply concatenated and form the IBAN. However, every
country has its own format of the above items, e.g. in Austria account numbers
are digits only and are between 6 and 11 digits long, which is different in
other countries.

The iban.py module offers an international account object Int_Account, which
stores the above items, checks for validity during creation and provides the
IBAN.

 >>> from ibanlib.iban import IntAccount, valid
 >>> a = IntAccount()
 Traceback (most recent call last):
 AttributeError: Country or IBAN is mandatory
 
The country or IBAN has to be specified during creation, otherwise, the class
does not know the country for which the IBAN specs should be applied.
 
 >>> a=IntAccount('AT')
 >>> a.account = '123456789'
 >>> a.bank = '12345'
 >>> a.bank
 '12345'
 >>> a.bank = '33333'
 >>> a.bank
 '33333'

These attributes are automatically checked, wrong values lead to an IBANError

 >>> a.account = '123ABC'                     # Only digits allowed
 Traceback (most recent call last):
 IBANError: Invalid value "123ABC" for account
 >>> a.account = '12234234234234324234'       # Too long
 Traceback (most recent call last):
 IBANError: Invalid value "12234234234234324234" for account

These object attributes can also be set at object creation time:
 >>> a = IntAccount('AT', bank='12345', account='123456789')
 
If all required attributes of a country are set, the iban may be retrieved

 >>> a.iban
 'AT141234500123456789'

If attributes are missing, no IBAN can be retrieved

 >>> IntAccount('AT').iban
 Traceback (most recent call last):
 IBANError: Attribute bank is missing, no IBAN can be created
 
An international account can also be initialized with the IBAN, whereas the
other given initialization options (country, account etc.) are ignored:

 >>> b=IntAccount(iban='AT141234500123456789')
 >>> b.account
 '123456789'
 >>> b == a
 True

If the given IBAN is invalid, an error is raised:

 >>> b=IntAccount(iban='AT141234500123456781')
 Traceback (most recent call last):
 IBANError: IBAN has an invalid checksum
 
If the specified country for an IBAN is not known, an error is raised:

 >>> b=IntAccount(iban='XY141234500123456789')
 Traceback (most recent call last):
 IBANError: Country XY not implemented
 >>> IntAccount('ZX')
 Traceback (most recent call last):
 IBANError: Country ZX not implemented

Moreover, it can be requested, if the international account, or, more specific,
the according country, is member of the SEPA contract:

 >>> b.is_sepa
 True

IBANs can also be easily checked for validity:

 >>> valid('AT141234500123456789')
 True
 >>> valid('AT14123450012345678')
 False
 >>> valid('AT341234500123456789')
 False
 >>> valid('AT14123450012345a78')
 False

The country specifics are stored in a configuration file called
"countries.cfg", the syntax of this file is given there. The function
get_country_specs() can be used to read in the specifications for the needed
country

 >>> from ibanlib.iban import get_country_specs
 >>> d=get_country_specs('AT')

All configurations is now read into d. Bank/Account can now be checked for
validity
 
 >>> d['account'].valid('123')   # too short
 False
 >>> d['account'].valid('1231234')  # valid
 True
 >>> d['account'].valid('12312312321312321321313') # too long
 False
 >>> d['account'].valid('123ABC234')  # only digits allowed
 False

Short data can be filled to its maximum length

 >>> d['account'].fill('1234567')
 '00001234567'
 
Of course, IBANs can be generated for various countries, here are some
examples:

Austria

 >>> IntAccount('AT',bank='19043',account='234573201').iban
 'AT611904300234573201'

Germany
 >>> IntAccount('DE',bank='37040044', account='0532013000').iban
 'DE89370400440532013000'
 >>> IntAccount(iban='DE89370400440532013000')
 IntAccount(country='DE', bank='37040044', branche='None', account='0532013000', check1='None', check2='None', check3='None')

Italy 
 
 >>> IntAccount('IT', bank='05428', branche='11101', 
 ...            account='123456', check1='X').iban
 'IT60X0542811101000000123456'
 >>> valid(iban='IT21Q054280160000ABCD12ZE34')
 True
 >>> valid('IT30C0800001000123VALE456NA')
 True
 >>> valid('IT11V0600003200000011556BFE')
 True
 >>> valid('IT21J0100516052120050012345')
 True
 
 
