from flask import Flask
import mysite.views
import os
from mysite import db


basedir = os.path.abspath(os.path.dirname(__file__))


class Drug(object):

    def __init__(self, name, ndc, unit, otc, b_or_g, source):
        self.name = name
        self.scientific_name = "(none listed)"
        self.id = ndc
        self.prices = {} #dictionary of datestr: pricefloat
        self.unit = unit
        self.otc = otc
        self.b_or_g = b_or_g
        self.lowest = ("20500101", 1000000.0)
        self.highest = ("20000101", 0.0)
        self.current = ("19000101", 0.0)
        self.oldest = ("20500101", 0.0)
        self.change = 0
        self.vendor = "(None listed)"
        self.package = "(None listed)"
        self.source = source
        self.desc = ""

    def add_price(self, datestr, price): #datestr formatted YYYYMMDD, price formatted as str
        if price is None:
            self.prices[datestr] = None
        elif datestr in self.prices:
            pass
        else:
            self.prices[datestr] = float(price)
            Drug.update_prices(self)

    def add_vendor(self, vendor):
        self.vendor = vendor

    def add_sci_name(self, name):
        self.scientific_name = name

    def add_desc(self, desc):
        self.desc = desc

    def add_package(self, package):
        self.package = package

    def update_prices(self):
        for date in self.prices:
            if self.prices[date] is None:
                pass
            if date > self.current[0]:
                self.current = (date, self.prices[date])
            if date < self.oldest[0]:
                self.oldest = (date, self.prices[date])
            if self.prices[date] < self.lowest[1]:
                lowest = self.prices[date]
                self.lowest = (date, lowest)
            if self.prices[date] > self.highest[1]:
                highest = self.prices[date]
                self.highest = (date, highest)
        try:
            self.change = ( self.current[1] / self.oldest[1] ) - 1
        except (ZeroDivisionError, TypeError):
            pass

    def printer(self):
        print "Proprietary name: " + self.name
        print "Scientific name: " + self.scientific_name
        print "NDC: " + self.id
        print "What it is: " + self.desc
        print "Manufacturer: " + self.vendor
        if self.source == "VA":
            print "NOTE: THIS DRUG INFORMATION IS FROM THE VETERANS' AFFAIRS CONTRACT.\nTHESE ARE NOT RETAIL PRICES."
        print "B/G:",
        if self.b_or_g == "B":
            print "Brand"
        elif self.b_or_g == "G":
            print "Generic"
        else:
            print self.b_or_g
        print "Current Price: $%.2f" % float(self.current[1])
        if self.change > 0:
            print "Lowest Price: $%.2f" % float(self.lowest[1])
        else:
            print "Highest Price: $%.2f" % float(self.highest[1])
        print "Change by percent: %.2f%%" % (self.change * 100)
        #print "Prices: ",
        #pprint(self.prices)


class DrugDB(db.Model):
    __tablename__ = 'drugs'
    drug_id = db.Column(db.Integer, primary_key=True)
    ndc = db.Column(db.String(11), index=True)
    p_name = db.Column(db.String(64), index=True)
    s_name = db.Column(db.String(64), index=True)
    unit = db.Column(db.String(64))
    otc = db.Column(db.String(12))
    b_or_g = db.Column(db.String(12))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'))
    company = db.relationship('Company', backref='all_drugs')
    package = db.Column(db.String(64))
    description = db.Column(db.String(128))
    prices = db.relationship('Price', backref='this_drug', lazy='dynamic')
    # earliest_price = db.Column(db.Float)
    # curr_price = db.Column(db.Float)

    def __repr__(self):
        return '<%r - #%r>' % (self.p_name, self.ndc)


class Price(db.Model):
    __tablename__ = 'prices'
    price_id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.drug_id'))
    drug = db.relationship('DrugDB', backref='all_prices')
    price = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    def __repr__(self):
        return '<%r: $%r %r>' % (self.drug_id, self.price, self.start_date)


class Company(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    drugs = db.relationship('DrugDB', backref='vendor', lazy='dynamic')

    def __repr__(self):
        return '<%r>' % self.name
