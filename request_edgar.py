import edgar
from unidecode import unidecode
import pandas as pd
import re


def clear_file(doc):
    """
    @doc: the single doc got from  edgar.getDocuments
    @return: the cleared file, decode from unicode and remove white space
    """
    parsed_string = " ".join(str(doc).split())
    return unidecode(parsed_string)

def get10KByNameAndCIK(companyName, CIKNumber, noOfDocuments=1):
    """
    @companyName: the name of the company
    @CIKNumber: the cik number of the company
    @noOfDocuments: the number of differenct files for different years
    @return: the cleared file, decode from unicode and remove white space, in a list
    
    The user have to provide the CIK number by themselves
    """
    company = edgar.Company(companyName, CIKNumber)
    tree = company.getAllFilings(filingType = "10-K")
    docs = edgar.getDocuments(tree, noOfDocuments=noOfDocuments)
    if isinstance(docs, list):
        file_lists = [ clear_file(doc) for doc in docs]
        return file_lists
    else:
        return clear_file(docs)

def clear_cik_data(file_name):
    """
    @filename: "cik-lookup-data.txt"
    @return: a table [[name, cik]...]
    """
    nameCIK_table = open(file_name, "rb")
    table = []
    for line in nameCIK_table:
        try:
            line = line.decode('utf8')
        except:
            print("Cannot decode utf-8: ", str(line))
            continue
        parts = line.split(":")
        parts.pop()
        cik = parts[-1]
        parts.pop()
        name = ":".join(parts)
        table.append((name, cik))
  
    df = pd.DataFrame(table)
    df.to_csv("company_cik.csv")
    return table

def clear_snp_500_cik(file_name):
    """
    @file_name: "snp500_cik_ticker.csv"
    @return: a table [[name, cik]...]
    """
    _df = pd.read_csv(file_name)
    return _df

def getPartsFromParsedFile(file):
    return 0
    
    
# The goal is to find the starting and Ending point of ITEM1 , ITEM1A, and ITEM7
# The Heuristic Rule is 
# 1. Make sure whether the index in matched by regex
# if matched, take the second mention of the item as the starting point, the following mention of next item as the stopping point
# if not, use the first mention



def segmentITEM1_1A_7(string):
    regex_item1 = 'I[tT][Ee][Mm]\s*1[.\s]'
    regex_item1A = 'I[tT][Ee][Mm]\s*1A[.\s]'
    regex_item1B = 'I[tT][Ee][Mm]\s*1B[.\s]'
    regex_item2 = 'I[tT][Ee][Mm]\s*2[.\s]'
    regex_item7 = 'I[tT][Ee][Mm]\s*7[.\s]'
    regex_item8 = 'I[tT][Ee][Mm]\s*8[.\s]'

    # Check first appearance of item8, if smaller than 10000, then this appearence is index
    itr = re.finditer(regex_item8, string)
    index_matched = True
    for match in itr:
        if match.span()[0] > 10000:
            index_matched = False
        break
    
     # use ignore the first mentions

    item1_start = 0
    item1A_start = 0
    item1B_start = 0
    item7_start = 0
    item8_start = 0

    
    itr = re.finditer(regex_item1, string)
    if index_matched:   
        # 1 start point
        done = False
        for match in itr:
            item1_start = match.span()[0]
            if done:
                break
            else:
                done = True
    else:
         for match in itr:
            item1_start = match.span()[0]
            break
            
    # 1A start point
    done = False
    itr = re.finditer(regex_item1A, string)
    for match in itr:
        item1A_start = match.span()[0]
        if item1A_start > item1_start:
            print("item1A, item1: ", item1A_start, item1_start)
            break
                
    # 1B start point
    done = False
    itr = re.finditer(regex_item1B, string)
    for match in itr:
        item1B_start = match.span()[0]
        if item1B_start > item1A_start:
            print("item1B, item1A: ", item1B_start, item1A_start)

    if item1B_start == 0:    
	    # 1B start point
	    done = False
	    itr = re.finditer(regex_item2, string)
	    for match in itr:
	        item1B_start = match.span()[0]
	        if item1B_start > item1A_start:
	            print("item1B, item1A: ", item1B_start, item1A_start)
	            break
        
    # 7 start point
    done = False
    itr = re.finditer(regex_item7, string)
    for match in itr:
        item7_start = match.span()[0]
        if item7_start > item1B_start:
            print("item7, item1B: ", item7_start, item1B_start)
            break
                
    # 8 start point
    done = False
    itr = re.finditer(regex_item8, string)
    for match in itr:
        item8_start = match.span()[0]
        if item8_start > item7_start:
            print("item8, item7: ", item8_start, item7_start)
            break
                
    if item1_start == 0 or item1A_start == 0 or item1B_start == 0 or item7_start == 0 or item8_start == 0:
    	raise Exception("Invalid matching!")

    return string[item1_start:item1A_start], string[item1A_start:item1B_start], string[item7_start: item8_start]
        
    
        

def getRecentFileTable(company_list):
    """
    @company_list: the table of [[name, cik]...]
    @return table of 4 lists, name, cik, file content, file number
    
    for testing, set file number to be 3 and max number of company to be 20
    """
    n_file = 100
    # max_n_company = 3
    
    comp_count = 0
    tenK_count = 0
    table = list()
    
    for company_pairs in company_list:
        # limit the amount of company, only for testing
        # if tenK_count == max_n_company:
        #     break
            
        comp_count += 1
        files = get10KByNameAndCIK(company_pairs[0], company_pairs[1], n_file)
        if len(files) != n_file: 
            print("error: ", company_pairs," want: ", n_file ,"files, actual have: ", len(files))
            
       
        tenK_count += 1
        print(tenK_count)
        for i in range(len(files)):
            try:
                item1, item1A, item7 = segmentITEM1_1A_7(files[i])
                table.append((company_pairs[0], company_pairs[1], i, files[i], item1, item1A, item7))
            except:
                print("Warning: Invalid match: ", company_pairs[0], " ", company_pairs[1], " ", i)
    return table
 


company_df = clear_snp_500_cik("snp500_cik_ticker.csv")
company_list_int = company_df[["Security", "CIK"]].values
company_list = [ [tup[0], str(tup[1])] for tup in company_list_int]

table = getRecentFileTable(company_list)


df = pd.DataFrame(table)
df.to_pickle("10-K_for_snp500.pkl")
