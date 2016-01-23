#!flask/bin/python
from mysite import db
from mysite.models import Drug, DrugDB, Company, Price
import csv
from mysite.drug_functions import multiple_results
import datetime
import os

userhome = os.path.expanduser('~')

def add_FDA_info(drug_dict):

    # this function supplies drug and vendor names via NDCs from the FDA's official database.
    # sadly the FDA and NADAC have a slightly different format for NDCs, so it's not perfect.
    # It is very unlikely to assign an incorrect NDC -- rather, it will pass on drugs it cannot find a match for.
    name_file = os.path.join(userhome, 'Documents', 'Programming', 'Python', 'drugPrices', 'FDA-20160118.csv')
    headers = ["PRODUCTID", "PRODUCTNDC", "PRODUCTTYPENAME", "PROPRIETARYNAME", "PROPRIETARYNAMESUFFIX",
               "NONPROPRIETARYNAME", "DOSAGEFORMNAME", "ROUTENAME", "STARTMARKETINGDATE", "ENDMARKETINGDATE",
               "MARKETINGCATEGORYNAME", "APPLICATIONNUMBER", "LABELERNAME", "SUBSTANCENAME",
               "ACTIVE_NUMERATOR_STRENGTH", "ACTIVE_INGRED_UNIT", "PHARM_CLASSES", "DEASCHEDULE"]
    count = 1
    current_list = [key for key in drug_dict]
    with open(name_file, "r") as namecsv:
        csvreader = csv.reader(namecsv)
        for line in csvreader:
            if count == 1:
                pass
            else:
                drug = {}
                for i in range(len(headers)):
                    if headers [i] == "PRODUCTNDC":
                        drug["NDC"] = line[i].translate(None,"-")
                        templist = line[i].split("-")
                        templist[0] = templist[0] + "0"
                        drug["NDC2"] = "".join(templist)
                    else:
                        drug[headers[i]] = line[i]
                findings = [item for item in current_list if ( drug["NDC"] in item ) or ( drug["NDC2"] in item )]
                if len(findings) == 1:
                    this_drug = drug_dict[findings[0]]
                    Drug.add_vendor(this_drug, drug["LABELERNAME"])
                    Drug.add_sci_name(this_drug, drug["NONPROPRIETARYNAME"])
                    Drug.add_desc(this_drug, drug["PHARM_CLASSES"])
                    current_list.remove(findings[0])
                    print "%i drugs left to ID..." % len(current_list)
                elif len(findings) == 0:
                    pass
                else:
                    findings_as_drugs = [drug_dict[key] for key in findings] #converts list of keys into list of Drugs
                    findings = multiple_results(drug, findings_as_drugs) #list of Drugs
                    for finding in findings: #finding is a Drug
                        Drug.add_vendor(finding, drug["LABELERNAME"])
                        Drug.add_sci_name(finding, drug["NONPROPRIETARYNAME"])
                        Drug.add_desc(finding, drug["PHARM_CLASSES"])
                        current_list.remove(finding.id)
                        print "%i drugs left to ID..." % len(current_list)

                            # BECAUSE THE FDA NDCS ARE ONLY EIGHT DIGITS LONG, THIS SEARCH OFTEN RETURNS 2+ RESULTS.
                            # TODO: write a function to check other info to figure out which is the correct one.
                            # or, worst-case scenario, prompt user to choose which looks right, maybe?
            count += 1

    return drug_dict


def raw_drugs_begin():
    #csvpath = os.path.join(userhome, 'Documents', 'Programming', 'Python', 'drugPrices', 'NADAC', 'NADAC 20121004.csv')
    csvpath = "test NADAC.csv"
    headers = ["Name", "NDC", "Price", "Effective date", "Pricing Unit", "Pharmacy Type", "OTC or Not",
               "Explanation Code", "Brand or Generic"]
    count = 1
    drug_dict = {}
    with open(csvpath, 'r') as csvfile:
        drug_data = csv.reader(csvfile)
        for row in drug_data:
            if count < 5:
                pass
            else:
                drug = {}
                for i in range(len(headers)):
                    drug[headers[i]] = row[i]
                price = drug["Price"]
                this_drug = Drug(drug["Name"], drug["NDC"], drug["Pricing Unit"], drug["OTC or Not"],
                                 drug["Brand or Generic"], "NADAC")
                Drug.add_price(this_drug, "20141015", price)
                drug_dict[drug["NDC"]] = this_drug
            count += 1
        csvfile.close()
    drug_dict = add_FDA_info(drug_dict)
    return drug_dict


def get_or_create(model, raw_name):
    if raw_name == "(None listed)":
        return None
    company_entry = db.session.query(model).filter(Company.name == raw_name).first()
    if not company_entry:
        company_entry = Company(name=raw_name)
    return company_entry


def first_db_add(drug_dict):

    date = "20141015"

    #db.create_all()

    #flush the dbs first
    drugs = DrugDB.query.all()
    for entry in drugs:
        db.session.delete(entry)
    companies = Company.query.all()
    for entry in companies:
        db.session.delete(entry)
    prices = Price.query.all()
    for entry in prices:
        db.session.delete(entry)


    #add for each drug in drug_dict
    for key in drug_dict:
        drug = drug_dict[key]
        company = get_or_create(Company, drug.vendor)
        if company:
            db.session.add(company)
            db.session.flush()
            db_drug = DrugDB(ndc=drug.id, p_name=drug.name, s_name=drug.scientific_name, unit=drug.unit, otc=drug.otc,
                             b_or_g=drug.b_or_g, company_id=company.company_id, package=drug.package, description=drug.desc)
        else:
            db_drug = DrugDB(ndc=drug.id, p_name=drug.name, s_name=drug.scientific_name, unit=drug.unit, otc=drug.otc,
                             b_or_g=drug.b_or_g, package=drug.package, description=drug.desc)
        db.session.add(db_drug)
        db.session.flush()
        price = Price(drug_id=db_drug.drug_id, price=drug.prices[date],
                      start_date=datetime.datetime.strptime(date, "%Y%m%d"), end_date=None)
        db.session.add(price)
    db.session.commit()


def test():
    drug_dict = raw_drugs_begin()
    first_db_add(drug_dict)
    print DrugDB.query.get(20)
    print DrugDB.query.get(5)
    print Company.query.get(8)
    this = Company.query.get(4)
    print this
    for drug in this.all_drugs:
        print "- ", drug
    print Price.query.get(9)
    print Price.query.get(16)


def create_it():
    drug_dict = raw_drugs_begin()
    first_db_add(drug_dict)


if __name__ == '__main__':
    test()