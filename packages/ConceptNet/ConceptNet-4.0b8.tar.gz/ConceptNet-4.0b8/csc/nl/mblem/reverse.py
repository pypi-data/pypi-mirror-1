from trie import *
import cPickle as pickle

def reversal_info(trie):
    import cPickle as pickle
    for node, suffix in trie.walk(''):
        for leaf in node.leaves():
            stem = leaf.apply(suffix)[0]
            if '?' in stem:
                yield (leaf.delete, leaf.delete, leaf.add, leaf.pos, leaf.inflections)
            else:
                yield (suffix, leaf.delete, leaf.add, leaf.pos, leaf.inflections)

def trim(trie):
    for (key, leaves) in trie.leaf_index.items():
        counts = defaultdict(int)
        for leaf in leaves:
            counts[leaf] += 1
        items = sorted(counts.items(), key=lambda x: -x[1])
        print items
        best = items[0][0]
        trie.leaf_index[key] = [best]
    for subtrie in trie.trie.values():
        trim(subtrie)

def reverse(trie):
    newtrie = Node()
    for suffix, delete, add, pos, infl in reversal_info(trie):
        # reversing it now
        add, delete = delete, add
        while len(suffix) >= len(delete):
            newtrie.add(suffix[::-1], Leaf.make(add, delete, pos, infl))
            if len(suffix) == 0: break
            suffix = suffix[1:]
    trim(newtrie)
    return newtrie

if __name__ == '__main__':
    trie = pickle.load(open('en.mblem.pickle'))
    reversed = reverse(trie)
    out = open('en.unlem.pickle', 'w')
    pickle.dump(reversed, out)
    out.close()

