"""
May need to filter citations by citation status attribute
Occasionally pub year will be None if fail to extract from MedlineDate tag? Or maybe this is not used anymore
"""
from dateutil.parser import parse
import re
import xml.etree.ElementTree as ET


def parse_update_file(path):
    with open(path, 'rt', encoding='utf8') as _file:
        citations = []
        root_node = ET.parse(_file)
        for medline_citation_node in root_node.findall('PubmedArticle/MedlineCitation'):
            citation_data = _extract_citation_data(medline_citation_node)
            if _should_process(citation_data):
                citation_dict = _construct_citation_dict(citation_data)
                citations.append(citation_dict)
        return citations    

    
def _construct_citation_dict(citation_data):
    pmid, title, abstract, affiliations, journal_nlmid, pub_year, _ = citation_data
    _dict = { 'pmid': pmid, 
              'title': title, 
              'abstract': abstract, 
              'author_list': affiliations,
              'journal_nlmid': journal_nlmid, 
              'pub_year': pub_year,
                }
    return _dict
       
      
def _extract_citation_data(medline_citation_node):

    pmid_node = medline_citation_node.find('PMID')
    pmid = pmid_node.text.strip()
    pmid = int(pmid)
    
    title_node = medline_citation_node.find('Article/ArticleTitle') 
    title = ET.tostring(title_node, encoding='unicode', method='text')
    if title is not None:
        title = title.strip()

    abstract = ''
    abstract_node = medline_citation_node.find('Article/Abstract')
    if abstract_node is not None:
        abstract_text_nodes = abstract_node.findall('AbstractText')
        for abstract_text_node in abstract_text_nodes:
            if 'Label' in abstract_text_node.attrib:
                if len(abstract) > 0:
                    abstract += ' '
                abstract += abstract_text_node.attrib['Label'].strip() + ': '
            abstract_text = ET.tostring(abstract_text_node, encoding='unicode', method='text')
            if abstract_text is not None:
                abstract += abstract_text.strip()

    affiliation_nodes = medline_citation_node.findall('.//AffiliationInfo')
    if affiliation_nodes is not None:
        affiliation_list = [ET.tostring(affiliation_node, encoding='unicode', method='text') for affiliation_node in affiliation_nodes]
        affiliations = ' '.join(affiliation_list)
    else:
        affiliations = 'None'

    journal_nlmid_node = medline_citation_node.find('MedlineJournalInfo/NlmUniqueID')
    journal_nlmid = journal_nlmid_node.text.strip() if journal_nlmid_node is not None else ''

    medlinedate_node = medline_citation_node.find('Article/Journal/JournalIssue/PubDate/MedlineDate')
    if medlinedate_node is not None:
        medlinedate_text = medlinedate_node.text.strip()
        pub_year = _extract_year_from_medlinedate(medlinedate_text)
    else:
        pub_year_node = medline_citation_node.find('Article/Journal/JournalIssue/PubDate/Year')
        pub_year = pub_year_node.text.strip()
        pub_year = int(pub_year)

    citation_status = medline_citation_node.attrib['Status'].strip()

    return pmid, title, abstract, affiliations, journal_nlmid, pub_year, citation_status


def _extract_year_from_medlinedate(medlinedate_text):
    pub_year = medlinedate_text[:4]
    try:
        pub_year = int(pub_year)
    except ValueError:
        match = re.search(r'\d{4}', medlinedate_text)
        if match:
            pub_year = match.group(0)
            pub_year = int(pub_year)
        else:
            try:
                pub_year = parse(medlinedate_text, fuzzy=True).date().year
            except ValueError:
                pub_year = None
    return pub_year


def _should_process(citation_data):
    should_process = True # TODO may only want to process certain citation status
    return should_process
    

        
