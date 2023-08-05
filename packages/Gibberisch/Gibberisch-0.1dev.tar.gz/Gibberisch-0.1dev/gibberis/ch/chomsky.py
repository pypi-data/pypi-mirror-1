import random
from itertools import chain
from ConfigParser import SafeConfigParser

def chomsky(num_sentences, leadins, subjects, verbs, objects):
    """Chomsky method of generating random text."""
    return ' '.join(' '.join(random.choice(part).strip()
                             for part
                             in (leadins, subjects, verbs, objects))
                    for i in xrange(num_sentences))


def generate(config, num_sentences):
    parser = SafeConfigParser()
    parser.read([config])

    return chomsky(num_sentences, **dict((k,v.strip().splitlines()) for k,v in parser.items('gibberish')))

        
def main():
    import sys
    print generate(sys.argv[1], int(sys.argv[2]))
