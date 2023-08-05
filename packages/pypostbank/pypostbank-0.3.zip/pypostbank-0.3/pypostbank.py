# -*- coding: utf-8 -*-
# Copyright (C) 2006-2007 Tobias Bell <tobias.bell@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

"""Das Modul postbank bietet eine API zum Zugriff auf das Online-Banking System
der deutschen Postbank AG
"""
import urllib
import urllib2
import datetime
import time
try:
    from decimal import Decimal
except:
    Decimal = float        

__version__ = '0.2'

class PostBankError(Exception):
    """Basisklasse aller Exceptions dieses Moduls"""
    pass


class PostBank(object):
    """Bietet Zugriff auf das Online Banking System der
    Postbank. Unterstützte Funktionalität:
        * login
        * logout
        * getAccount
    Öffentliche Attribute:
        * accountNumber, Kontonummer
        * pinNumber, PIN
        * loggedIn, besteht eine Anmeldung
    """

    BASE_URL = "https://banking.postbank.de"    
    METHODS = {
        "login"            : "/app/login.do",
        "logout"           : "/app/logout.do;jsessionid=%(sessionID)s",
        "accountStatement" : "/app/kontoumsatz.umsatz.init.do;jsessionid=%(sessionID)s"
    }    

    def __init__(self, accountNumber="", pinNumber=""):
        """Konstruktion des PostBank Objekts zur Anmeldung. Es können
        optional Kontonummer und PIN übergeben werden
        """
        self.accountNumber = str(accountNumber)
        self.pinNumber = str(pinNumber)
        self.loggedIn = False
        self.sessionID = None

    def login(self, accountNumber="", pinNumber=""):
        """Anmeldung an das Online Banking System. Wenn Kontonummer und
        PIN nicht bei Erzeugung des Objekts angegeben wurden, kann dies auch hier
        mittels accountNumber und pinNumber geschehen

        >>> a = PostBank(9999999999, 11111)
        >>> a.loggedIn
        False
        >>> a.login()
        >>> a.loggedIn
        True
        >>> a.logout()
        >>> a.loggedIn
        False
        >>> a = PostBank()
        >>> a.login()
        Traceback (most recent call last):
            ...
        PostBankError: accountNumber and pinNumber must be set
        """
        if accountNumber:
            self.accountNumber = str(accountNumber)
        if pinNumber:
            self.pinNumber = str(pinNumber)
        if not (self.accountNumber and self.pinNumber):
            raise PostBankError("accountNumber and pinNumber must be set")

        postData = urllib.urlencode({
            "accountNumber" : self.accountNumber,
            "pinNumber"     : self.pinNumber
        })
        url = self.BASE_URL + self.METHODS["login"]
        data = urllib2.urlopen(url, postData)
        loginURL = data.geturl()
        if loginURL.find("jsessionid=") == -1:
            raise PostBankError("login failed with accountNumber `%s' and pinNumber `%s'" \
                                % (self.accountNumber, "*" * len(self.pinNumber)))
        self.sessionID = data.geturl().split("=")[-1]
        self.loggedIn = True               
                   
    def logout(self):
        """Abmelden am Online Banking System"""
        url = self.BASE_URL + self.METHODS["logout"] % self.__dict__
        data = urllib2.urlopen(url)
        self.loggedIn = False

    def getAccount(self, accountNumber=None):
        """Rückgabe eines PostBankAccount Objekts zur übergebenen accountNumber.
        Ohne Angabe der Kontonummer wird implizit das zur Anmeldung genutzte Konto
        genutzt
        """
        if accountNumber:
            konto = str(accountNumber)
        else:
            konto = self.accountNumber

        getData = urllib.urlencode({
            "action"   : "download",
            "cache"    : "true",
            "konto"    : konto,
            "zeitraum" : "tage",
            "tage"     : "00"
        })
        url = self.BASE_URL + self.METHODS["accountStatement"] % self.__dict__ \
              + "?" + getData
        data = urllib2.urlopen(url)
        as = PostBankAccount()
        as.parse(data)
        return as

    def __del__(self):
        """Führt automatisch eine Abmeldung von Online Banking System aus,
        wenn dies noch nicht geschehen ist.
        """
        if self.loggedIn:
            self.logout()


# Hilfsfunktionen zum Verarbeiten des Kontoauszugs
def parseAmount(value):
    """Wandelt einen Euro-Betrag in ein Decimal Objekt um"""
    return Decimal(value.replace(".", "").replace(",", "."))

def parseDate(value):
    """Wandelt ein Datum in ein date Objekt um"""
    timeTuple = time.strptime(value, "%d.%m.%Y")
    return datetime.date(*timeTuple[:3])

class PostBankAccount(object):
    """Bietet Zugriff auf einen Postbank Online Konto mit folgenden
    Daten
        * name, Name des Kontos z.B. "Girokonto", string
        * holder, Kontoinhaber, string
        * bankCode, Bankleitzahl, integer
        * accountNumber, Kontonummer, integer
        * IBAN, International Bank Account Number, string
        * balance, Saldo, Decimal
        * outstandingMoney, vorgemerkte Umsätze, Decimal
        * accountingRecords, einzelne Buchungssätze
    """

    def __init__(self):
        self.name = ""
        self.holder = ""
        self.bankCode = 0
        self.accountNumber = 0
        self.IBAN = ""
        self.balance = Decimal("0.00")
        self.outstandingMoney = Decimal("0.00")
        self.accountingRecords = []

    def parse(self, data):
        """Extrahiert die Kontodaten aus data. data muss entweder ein string
        sein oder das Iterator-Protokoll unterstützen
        """
        if isinstance(data, basestring):
            data = data.splitlines()
        iterable = iter(data)

        for line in iterable:
            line = line.strip()
            
            if not line:
                continue

            if line.startswith("Kontoums"):
                self.name = line.split()[-1]
            elif line.startswith("Name:"):
                self.holder = " ".join(line.split()[1:])
            elif line.startswith("BLZ:"):
                self.bankCode = int(line.split()[-1], 10)
            elif line.startswith("Kontonummer:"):
                self.accountNumber = int(line.split()[-1], 10)
            elif line.startswith("IBAN:"):
                self.IBAN = line.split()[-1]
            elif line.startswith("Aktueller Kontostand:"):
                self.balance = parseAmount(line.split()[-2])
            elif line.startswith("Summe vorgemerkter Umsätze:"):
                self.outstandingMoney = parseAmount(line.split()[-2])
            elif line.startswith("Datum"):
                self._parseAccountingRecords(iterable)

    def _parseAccountingRecords(self, iterable):
        for line in iterable:
            line = line.strip()
            
            if not line:
                continue

            entry = PostBankAccountRecord(line)
            self.accountingRecords.append(entry)

class PostBankAccountRecord(object):
    '''Bietet Zugriff auf einen Buchungssatz mit den Attributen
        + date, Datum, date
        + valueDate, Wertstellung, date
        + kind, Art, string
        + information, Buchungshinweis, string
        + initiator, Auftraggeber, string
        + recipient, Empfänger, string
        + amount, Betrag, Decimal
        + balance, Saldo, Decimal
    '''

    ACCOUNTING_COLUMNS = (
        ("date",        parseDate),
        ("valueDate",   parseDate),
        ("kind",        str),
        ("information", str),
        ("initiator",   str),
        ("recipient",   str),
        ("amount",      parseAmount),
        ("balance",     parseAmount)
    )

    def __init__(self, line=None):
        self.date = None
        self.valueDate = None
        self.kind = ''
        self.infomration = ''
        self.inititor = ''
        self.recipient = ''
        self.amount = Decimal('0.00')
        self.balance = Decimal('0.00')

        if line:
            self.parse(line)


    def parse(self, line):
        values = line.split("\t")

        for (key, function), value in zip(self.ACCOUNTING_COLUMNS, values):
                self.__dict__[key] = function(value)
        
        

# Funktionen zum schnellen Zugriff auf Postbank Konten oder Kontendaten
def getAccount(accountNumber, pinNumber):
    """Rückgabe eines PostBankAccount Objekts zur übergebenen Kontonummer
    
    >>> a = getAccount(9999999999, 11111)
    >>> a.name
    'Girokonto'
    >>> a.accountNumber
    9999999999L
    >>> a.bankCode
    20010020
    >>> a.IBAN
    'DE31200100209999999999'
    >>> a.holder
    'PETRA PFIFFIG'
    >>> a.balance + a.outstandingMoney == a.accountingRecords[0].balance
    True
    """
    pb = None
    try:
        pb = PostBank(accountNumber, pinNumber)
        pb.login()
        return pb.getAccount()
    finally:
        if pb and pb.loggedIn:
            pb.logout()


def getBalance(accountNumber, pinNumber):
    """Rückgabe des Saldo zur übergebenen Kontonummer"""
    account = getAccount(accountNumber, pinNumber)
    return account.balance


if __name__ == "__main__":
    import doctest
    doctest.testmod(report=True)
