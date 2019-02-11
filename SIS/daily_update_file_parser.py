"""
May need to filter citations by citation status attribute
Occasionally pub year will be None if fail to extract from MedlineDate tag? Or maybe this is not used anymore
"""
from dateutil.parser import parse
import re
import xml.etree.ElementTree as ET

from .misindexed_journal_ids import misindexed_ids

def parse_update_file(path, journal_drop, predict_medline, selectively_indexed_ids):
    """
    Main parsing function that
    calls private functions within module. 
    Will return list of dictionaries, 
    each dictionary containing citation data
    """

    with open(path, 'rt', encoding='utf8') as _file:
        citations = []
        root_node = ET.parse(_file)
        for medline_citation_node in root_node.findall('PubmedArticle/MedlineCitation'):
            citation_data = _extract_citation_data(medline_citation_node)
            # Make predictions for only selectively indexed journals 
            # that do not have a MEDLINE and PubMed-not-MEDLINE status yet.
            # Citations that do not meet this criteria will not be processed,
            # nor will citations from misindexed journals if 
            # --no-journal-drop is included
            if not predict_medline and (citation_data[6] != "MEDLINE" and citation_data[6] != "PubMed-not-MEDLINE"):
                if citation_data[4] in selectively_indexed_ids:
                    if journal_drop:
                        if citation_data[4] not in misindexed_ids: 
                            citation_dict = _construct_citation_dict(citation_data)
                            citations.append(citation_dict)
                    elif not journal_drop:
                        citation_dict = _construct_citation_dict(citation_data)
                        citations.append(citation_dict)
            # Otherwise, make predictions for citations not
            # from selectively indexed journals 
            # that HAVE a MEDLINE status
            # Citations that do not meet this criteria not be processed
            # This option is exclusively for running on everything not selectively indexed,
            # therefore the option --no-journal-drop has no effect
            elif predict_medline and citation_data[6] == "MEDLINE":
                if citation_data[4] not in selectively_indexed_ids:
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
