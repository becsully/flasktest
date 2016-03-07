import csv
import sys


def get_examples():
    reload(sys)  
    sys.setdefaultencoding('utf8')
    examples = []
    filename = "mysite/static/examples.csv"
    with open(filename, "r") as csvfile:
        examples_csv = csv.reader(csvfile)
        for line in examples_csv:
            example_dict = {"Headline": line[0], "Image": line[1], "Link": line[2], 
                            "Paragraph": line[3], "Role": line[4]}
            examples.append(example_dict)
        csvfile.close()
    return examples
