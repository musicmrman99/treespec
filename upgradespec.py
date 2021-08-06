import sys
import graphviz as gv
import itertools

import utils

class Relation:
    def __init__(self, num=1, combo="X"):
        self.num = int(num)
        if combo == "I":
            self.inclusive = True
        elif combo == "X":
            self.inclusive = False
        else:
            raise ValueError(f"not a valid combinatoral spec: {combo}")

        self.next = None

    def to_node(self, node):
        self.next = node

    def to_nodes(self, nodes):
        self.next = nodes

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
            or self.inclusive != False
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

    def relate(self, relation):
        self.relation = relation

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

class Builder:
    def __init__(self, name):
        self.root = Node(name)
        self.cur = self.root

    def node(self, name):
        next = Node(name)
        self.cur.to_node(next)
        self.cur = next
        return self

    def branch(self, *builders):
        next = [builder.get_root() for builder in builders]
        self.cur.to_nodes(next)
        self.cur = builders
        return self

    def to(self, num=1, combo="X"):
        relation = Relation(num, combo)
        for end in self.get_ends():
            end.relate(relation)
        self.cur = relation
        return self

    def get_root(self):
        return self.root

    def get_ends(self):
        if utils.is_iterable(self.cur):
            ends = list(itertools.chain.from_iterable(
                builder.get_ends() for builder in self.cur))
        else:
            ends = [self.cur]
        return ends

def _get_next_node(rest, spec_str):
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
    return (name, rel_spec, rest)

def _get_next_branch(rest, spec_str):
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

    # Handle divergent substructure (multiple sub-trees)
    subtrees_str = utils.split_top_level(part, ",", [("(", ")")])
    builders = list(map(lambda subtree_str: _parse_spec(subtree_str), subtrees_str))

    # Return needed values
    return (builders, rel_spec, rest)

def _parse_spec(spec_str: str) -> Builder:
    """
    Parse the given string of USL into a spec tree, returning the root builder.
    """

    # Remove ALL spaces
    rest = spec_str.replace(" ", "")

    # Nothing to parse
    if rest == "":
        return None

    # Split off first node and make the root builder
    (root_name, rel_spec, rest) = _get_next_node(rest, spec_str)
    builder = Builder(root_name)

    # Make the rest of the nodes
    while rest is not None:
        # Relate last spec "to" next spec (handling relation spec if needed)
        if rel_spec is not None:
            if rest == "":
                raise ValueError(
                    f"cannot have relation spec '{rel_spec}'"
                    f" without relation, in: {spec_str}"
                )

            # FIXME: num may be more than one character!!!
            (num, combo, struct) = rel_spec # from last iteration
            builder.to(num, combo)
        else:
            builder.to()

        if rel_spec is None or struct == "C":
            # Split off next node, and keep going
            (node_name, rel_spec, rest) = _get_next_node(rest, spec_str)
            builder.node(node_name)

        elif struct == "D":
            (branch_builders, rel_spec, rest) = _get_next_branch(rest, spec_str)
            builder.branch(*branch_builders)

    # Return the *builder*
    return builder

def parse_spec(spec_str: str) -> Node:
    """Parse the given spec string into a spec tree."""

    builder = _parse_spec(spec_str)
    if builder is None:
        return builder
    else:
        return builder.get_root()

    # Return the root
    return root
