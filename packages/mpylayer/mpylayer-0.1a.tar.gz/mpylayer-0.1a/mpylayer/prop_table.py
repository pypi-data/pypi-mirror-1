from cPickle import load
import os
caminho, _ = os.path.split(os.path.realpath(__file__))
property_table = load(open(os.path.join(caminho, 'data', 'properties.pickle')))

if __name__ == '__main__':
    from pprint import pprint
    pprint(property_table)