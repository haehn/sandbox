import glob
import json
import os

from section import Section

class Indexer(object):

  def __init__(self):
    '''
    '''
    pass
    

  def index(self, input_dir):
    '''
    '''

    json_files = glob.glob(os.path.join(input_dir, '*.json'))

    sections = []

    for json_file in json_files:

      basename = os.path.basename(json_file)

      with open(json_file) as f:
        new_section = Section.fromJSON(json.load(f))
        new_section._id = basename
        new_section._data_prefix = input_dir
        sections.append(new_section)

    return sections
