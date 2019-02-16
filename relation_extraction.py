import re
from collections import defaultdict, Counter
from nltk.parse.stanford import StanfordDependencyParser

class_path = "/Users/heatherlogan/Desktop/stanford-parser-full-2018-10-17/stanford-parser.jar"
models_path = "/Users/heatherlogan/Desktop/stanford-english-corenlp-2018-02-27-models.jar"


def build_paths(tree):

    # # relations are edges
    # for edge in tree:
    #     print(edge)

    def build(start):
        trace = [start]
        def path(inc):
            incoming = [edge[1] for edge in tree if edge[0] == inc]
            if len(incoming)==1:
                trace.append(incoming[0])
                path(incoming[0])
        path(start)
        return trace

    # nodes with incoming edges as nsubj or nsubjpass are potential start points
    possible_start = [edge[1] for edge in tree if edge[2] in subject_labels]
    # nodes with outgoing edges as nsubj, subjpass or dobj
    possible_relations = list(set([edge[0] for edge in tree if edge[2] in subject_labels or edge[2] in ['nmod', 'dobj']]))

    print("Subject Entity", [node_lookup[i] for i in build(possible_start[0])])

    for i in possible_relations.copy():
        if not any([j for j in build(i) if pos_tagged[node_lookup[j]] in ['VB', 'VBD', 'VBG', 'VBZ', 'VBN', 'VBP']]):
            possible_relations.remove(i)
    print("Possible Relations:", [node_lookup[i] for i in possible_relations])


    effector_labels = ['xcomp', 'dobj', 'nmod', 'amod']
    possible_effectees = []
    for relation in possible_relations:
        outgoing_edges = [edge[1] for edge in tree if edge[0]==relation and edge[2] in effector_labels]
        possible_effectees.extend(outgoing_edges)
        for new in outgoing_edges:
            # possible other edges if conjunctions with others
            possible_effectees.extend([edge[1] for edge in tree if edge[0]==new and edge[2]=='conj'])

    print("Effectors:", [build(i) for i in possible_effectees])


if __name__=="__main__":

    # example sentences

    text = "CHUNK1 is caused by a CHUNK2 that involves CHUNK4, CHUNK5 and CHUNK6."
    text2 = "Given that CHUNK has been suggested to involve CHUNK in CHUNK "
    text1 = "Given that ENTITY1 has been suggested to involve ENTITY2 in ENTITY3"
    texts = "Research has linked Mirror-Touch Synaesthesia with enhanced empathy."
    text5 = "Children with Autism may have difficulties with visual disengagement, that is, inhibiting current fixations " \
            "and orientating to new stimuli in the periphery."
    text6 = "CHUNK with CHUNK may have difficulties with CHUNK, that is, " \
            "inhabiting CHUNK and orientating to CHUNK in the CHUNK."

    dependency_parser = StanfordDependencyParser(path_to_jar=class_path, path_to_models_jar=models_path)
    result = dependency_parser.raw_parse(text6)
    dep = result.__next__()

    trips = list(dep.triples())

    for trip in trips:
        print(trip)

    pos_tagged = {}
    for pos in trips:
        pos_tagged[pos[0][0]] = pos[0][1]
        pos_tagged[pos[2][0]] = pos[2][1]

    tree = str(dep.to_dot())

    for i in tree.split("\n"):
        print(i)

    tree_split = list(filter(None, [line.strip() for line in tree.split("\n") if line != "\n"]))
    node_lookup = {}
    nodes = [node for node in tree_split if node[0].isdigit() and '->' not in node]
    for node in nodes:
        num, label = node.split(' [label="')
        node_lookup[num] = label[label.find("(")+1:label.find(")")]
    relations = [edge for edge in tree_split if '->' in edge]
    tree_triples = []
    for relation in relations:
        path, label = relation.split(' [label="')
        start, end = path.split(' -> ')
        relation = label.replace('"]', '').strip()
        tree_triples.append((start, end, relation))
    subject_labels = ['nsubj', 'nsubjpass']
    c = Counter(elem[2] for elem in tree_triples if elem[2] in subject_labels)
    if sum(c.values()) > 1:
        split_indices =[]
        for triple in tree_triples:
            if triple[2] in subject_labels:
                split_indices.append(tree_triples.index(triple))
        for idx in split_indices:
            if split_indices.index(idx) == 0:
                # print(tree_triples[0:split_indices[1]-1])
                build_paths(tree_triples[0:split_indices[1]-1])
                print("\n")

            elif split_indices.index(idx) != len(split_indices)-1:
                # print(tree_triples[idx:split_indices[idx]])
                build_paths(tree_triples[idx:split_indices[idx]])
                print("\n")
            else:
                # print(tree_triples[idx-1:len(tree_triples)])
                build_paths(tree_triples[idx-1:len(tree_triples)])
                print("\n")
    else:
        build_paths(tree_triples)
        print("Build relations as normal")


    dep.tree().draw()