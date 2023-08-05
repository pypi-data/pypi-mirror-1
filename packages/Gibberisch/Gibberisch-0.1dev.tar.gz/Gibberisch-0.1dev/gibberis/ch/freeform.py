import random

def random_text(data, num_words=100):
    """Source: http://www.physics.cornell.edu/sethna/StatMech/ComputerExercises/RandText"""
    # Read in the file and create a prefix mapping
    words = data.split()
    prefix = {}
    for i in xrange(len(words)-2):
        prefix.setdefault((words[i], words[i+1]), []).append(words[i+2])

    current_pair = random.choice(prefix.keys()) 
    random_text = '%s %s' % (current_pair[0], current_pair[1])
    for i in xrange(num_words-2):
        # last two words in document may not have a suffix
        if current_pair not in prefix:
            break
        next = random.choice(prefix[current_pair])
        random_text = '%s %s' % (random_text, next)
        current_pair = (current_pair[1], next)

    return random_text
