import csv
from glob import glob
import os
from models import Drug


def return_highest(drug_dict, min_percent, min_price, max_percent, max_price):
    highest = {}
    for drug in drug_dict:
        if (min_percent <= drug_dict[drug].change <= max_percent and
            min_price <= drug_dict[drug].current[1] <= max_price):
            highest[drug] = drug_dict[drug]
        else:
            pass
    return highest


def return_match(drug_dict, search_term):
    matches = {}
    for drug in drug_dict:
        if ( ( search_term.upper() in (drug_dict[drug].name).upper())
             or ( search_term.upper() in (drug_dict[drug].scientific_name).upper())) and (drug_dict[drug].prices > 1):
            matches[drug] = drug_dict[drug]
        else:
            pass
    return matches


def start():
    # to initialize the price change search, it's much quicker to add prices for just three dates
    # than for every date in the list. once the search has narrowed the list of results, the fill_in() function
    # fills in the date/price info for the dates in the middle.
    latest = "nadac/NADAC 20160120"
    middle = "nadac/NADAC 20140625"
    earliest = "nadac/NADAC 20121004"
    drugs = builder(latest)
    drugs = update(earliest, drugs)
    drugs = update(middle, drugs)
    return drugs


def builder(csvtext):
    # The function that takes a given CSV filename/date and creates a dictionary of drugs.
    # Their key is the drug NDC, and their value is the Drug object.

    date = csvtext[-8:]
    drug_dict = {}
    count = 1
    headers = which_headers(date)
    with open(csvtext+".csv", "r") as drugcsv:
        drugreader = csv.reader(drugcsv)
        for line in drugreader:
            if count < 5:
                pass
            else:
                drug = {}
                for i in range(len(headers)):
                    drug[headers[i]] = line[i]
                price = drug["Price"]
                this_drug = Drug(drug["Name"], drug["NDC"], drug["Pricing Unit"],
                                    drug["OTC or Not"], drug["Brand or Generic"], "NADAC")
                Drug.add_price(this_drug, date, price)
                drug_dict[drug["NDC"]] = this_drug
            count += 1
        drugcsv.close()
    return drug_dict


def multiple_results(drugFDA, choices_list):
    # FOR TESTING
    # sometimes the simple "if 8-digit-NDC in 11-digit-NDC" search
    # returns more than one result. this function prints out the results.
    # drugFDA is the dict with FDA info
    # choices_list is a list of Drug objects that potentially match
    findings = []
    nameFDA = (drugFDA["PROPRIETARYNAME"].split(" "))[0]
    for choice in choices_list:
        if nameFDA.lower() in (choice.name).lower():
            findings.append(choice)
    return findings


def add_FDA_info(drug_dict):

    # this function supplies drug and vendor names via NDCs from the FDA's official database.
    # sadly the FDA and NADAC have a slightly different format for NDCs, so it's not perfect.
    # It is very unlikely to assign an incorrect NDC -- rather, it will pass on drugs it cannot find a match for.

    name_file = "FDA-20160118.csv"
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


def which_headers(datestr):
    if int(datestr) > 20130214:
        headers = ["Name", "NDC", "Price", "Effective date", "Pricing Unit", "Pharmacy Type", "OTC or Not",
                   "Explanation Code", "Brand or Generic"]
    else:
        headers = ["Name", "NDC", "Price", "Pharmacy Type", "OTC or Not", "Effective date", "Explanation Code", "Update"]
    return headers


def update(csvtext, drug_dict):

    # accesses a one-date CSV file (date given as str csvtext) and adds prices for drugs in the given drug dictionary.
    # if a drug is not in the drug dict, this function adds the drug and its info to the dictionary.

    date = csvtext[-8:]
    count = 1
    headers = which_headers(date)
    with open(csvtext+".csv", "r") as drugcsv:
        drugreader = csv.reader(drugcsv)
        for line in drugreader:
            if count < 5:
                pass
            else:
                drug = {}
                for i in range(len(headers)):
                    drug[headers[i]] = line[i]
                price = drug["Price"]
                if drug["NDC"] in drug_dict:
                    Drug.add_price(drug_dict[drug["NDC"]], date, price)
                else:
                    if int(date) < 20130215:
                        drug["Pricing Unit"] = "Unknown"
                        drug["Brand or Generic"] = "Unknown"
                    this_drug = Drug(drug["Name"], drug["NDC"], drug["Pricing Unit"],
                                     drug["OTC or Not"], drug["Brand or Generic"], "NADAC")
                    Drug.add_price(this_drug, date, price)
                    drug_dict[drug["NDC"]] = this_drug
            count += 1
        drugcsv.close()
    return drug_dict


def add_prices(csvtext, drug_dict):
    # adds prices from a CSV file (the date is the str csvtext arg) to each drug in a given drug dictionary.
    # for drugs in the dictionary but not in the file, the function adds None as the price.
    # this function passes on drugs in the CSV but not in the drug_dict.
    date = csvtext[-8:]
    count = 1
    headers = which_headers(date)
    drug_list = [drug for drug in drug_dict]
    with open(csvtext+".csv", "r") as drugcsv:
        drugreader = csv.reader(drugcsv)
        for line in drugreader:
            if count < 5:
                pass
            else:
                drug = {}
                for i in range(len(headers)):
                    drug[headers[i]] = line[i]
                price = drug["Price"]
                if drug["NDC"] in drug_dict:
                    Drug.add_price(drug_dict[drug["NDC"]], date, price)
                    drug_list.remove(drug["NDC"])
                else:
                    pass
            count += 1
        drugcsv.close()
    for drug in drug_list:
        Drug.add_price(drug_dict[drug], date, None)
    return drug_dict


def get_date_list():
    datelist = []
    for path in glob("nadac/NADAC *.csv"):
        datestr = os.path.basename(path).split('.')[0].split(' ')[1]
        datelist.append(datestr)
    return datelist


def fill_in(drugs):
    # this function fills in every date in the date list with the corresponding price.
    # it speeds things up to do this after the search has narrowed the results instead of doing it for all 20,000+ drugs
    date_list = get_date_list()
    for date in date_list:
        print ".",
        drugs = add_prices("nadac/NADAC " + date, drugs)
    print
    return drugs


def remove_stuff(str):
    # removes non-number characters from the menu() raw_inputs
    numstr = ""
    for character in str:
        if character.isdigit() or character == "." or character == "-":
            numstr += character
        else:
            pass
    return numstr
