import csv 
from xml.etree import ElementTree

def read_topics(path_to_topic):
    """
    @path_to_topic relative path to topics from the caller e.g. "../tmp/topics-rnd4.xml"
    @return list of dict where dict represents each topic
    e.g. 
    [
        {
            'number': '1', 
            'query': 'coronavirus origin', 
            'question': 'what is the origin of COVID-19',
            'narrative': "seeking range of information about ..."
         },
         ...
    ]
    """
    tree = ElementTree.parse(path_to_topic)
    topics = list()
    for topic in tree.getroot():
        d = dict()
        d["number"] = topic.attrib["number"]
        for field in topic:
            d[field.tag] = field.text
        topics.append(d)

    return topics

def get_abstract(path, uid_to_use=None):
    """
    @path_to_topic relative path to CORD-19 from the caller e.g. "../../CORD-19/2020-06-19/"
    @uid_to_use if not None, return only abstracts where uid is in uid_to_use. Otherwise, return all abstracts.
    @return dict where key=uid and value=abstract
    """
    abstracts = dict()
    with open(path + "metadata.csv") as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            cord_uid = row['cord_uid']
            if uid_to_use is None or cord_uid in uid_to_use:
                abstract = row['abstract']
                abstracts[cord_uid] = abstract
            
    return abstracts
