import sys
import graphviz as gv

import utils

# Circular dependency (tightly coupled) between Node <-> Relation

class Relation:
    def __init__(self, num=1, combo="I"):
        self.num = int(num)
        if combo == "I":
            self.inclusive = True
        elif combo == "X":
            self.inclusive = False
        else:
            raise ValueError(f"not a valid combinatoral spec: {combo}")

        self.next = None

    def node(self, node):
        self.next = node
        return self.next # so you can chain

    def branch(self, *names):
        self.next = names
        # you can't branch-chain anyway

    def __eq__(self, other):
        return (
            self.num == other.num
            and self.inclusive == other.inclusive
            and self.next == other.next
        )

    def __str__(self):
        return self.str()

    def str(self, detailed=False):
        if utils.is_iterable(self.next):
            next_str = ("("
                +", ".join(map(lambda n: n.str(detailed), self.next))
            +")")
        else:
            next_str = self.next.str(detailed)

        if (
            self.num != 1
            or self.inclusive != True
            or utils.is_iterable(self.next)
        ):
            rel_spec_str = "{"+str(self.num)

            if self.inclusive:
                rel_spec_str += "I"
            else:
                rel_spec_str += "X"

            if not utils.is_iterable(self.next):
                rel_spec_str += "C"
            else:
                rel_spec_str += "D"

            rel_spec_str += "}"
    
        else:
            rel_spec_str = ""

        return rel_spec_str+"->"+next_str

class Node:
    def __init__(self, name):
        self.name = name
        self.relation = None

    def to(self, relation):
        self.relation = relation
        return self.relation # so you can chain

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.relation == other.relation
        )

    def __str__(self):
        return self.str()

    def str(self, detailed=False):
        if self.relation is not None:
            rel_str = self.relation.str(detailed)
        else:
            rel_str = ""

        if detailed:
            name = "Node("+self.name+")"
        else:
            name = self.name

        return name + rel_str

def get_next_node(rest, spec_str):
    # Split off this part
    (part, rest) = utils.pad_list(rest.split("->", 1), 2, None)

    # Split the node name and the relation spec (if any)
    rel_spec = utils.get_between(part, "{", "}")
    if rel_spec is not None:
        name = part.split("{", 1)[0]
    else:
        name = part
        if part.find("{") > 0 or part.find("}") > 0:
            raise ValueError(f"incomplete relation spec in '{part}', in: {spec_str}")
    if name == "":
        raise ValueError(f"node names cannot be blank, in: {spec_str}")

    # Return needed values
    return (Node(name), rel_spec, rest)

def get_next_branch(rest, spec_str):
    # Split off this part (ie. list of sub-trees)
    # Note: Match brackets, as divergent branches are nestable
    part = utils.get_between(rest, "(", ")", True)
    if part is None or not rest.startswith("("+part+")"):
        raise ValueError(f"value of next node (the first part of '{rest}') is not a list, in: {spec_str}")
    rest = rest[len(part)+2:]
    (rel_spec_maybe, rest) = utils.pad_list(rest.split("->", 1), 2, None)

    # Split the node name and the relation spec (if any)
    rel_spec = utils.get_between(rel_spec_maybe, "{", "}")
    if rel_spec is None and (rel_spec_maybe.find("{") > 0 or rel_spec_maybe.find("}") > 0):
        raise ValueError(f"incomplete relation spec in '{rel_spec_maybe}', in: {spec_str}")

    # Handle divergent substructure (multiple sub-nodes/sub-trees)
    subtrees_str = part.split(",")
    nodes = map(lambda subtree_str: parse_spec(subtree_str), subtrees_str)

    # Return needed values
    return (nodes, rel_spec, rest)

def parse_spec(spec_str: str) -> Node:
    """Parse the given spec string into a spec tree."""

    # Remove ALL spaces
    rest = spec_str.replace(" ", "")

    # Nothing to parse
    if rest == "":
        return None

    # Split off first node and initialise the current object (node or relation)
    (root, rel_spec, rest) = get_next_node(rest, spec_str)
    cur = root

    # Make the rest of the nodes
    while rest is not None:
        # Create relation (handling relation spec)
        if rel_spec is not None:
            if rest == "":
                raise ValueError(
                    f"cannot have relation spec '{rel_spec}'"
                    f" without relation, in: {spec_str}"
                )

            # FIXME: num may be more than one character!!!
            (num, combo, struct) = rel_spec # from last iteration
            rel = Relation(num, combo)
        else:
            rel = Relation()

        cur = cur.to(rel)

        if rel_spec is None or struct == "C":
            # Split off next node, and keep going
            (node, rel_spec, rest) = get_next_node(rest, spec_str)
            cur = cur.node(node)

        elif struct == "D":
            (nodes, rel_spec, rest) = get_next_branch(rest, spec_str)
            cur = cur.branch(*nodes)

    # Return the root
    return root
