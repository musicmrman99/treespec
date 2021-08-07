"""
Defines an object model, parser, and graph generator for the Upgrade Spec
Language (USL).
"""

import sys
from typing import Optional
import graphviz as gv
import itertools

import utils

# Object Model
# --------------------------------------------------

class Relation:
    """
    Represents a many-to-N relationship between node/branch specs.

    The simplest form of Relation is a one-to-one relation. In USL:
        A->B
    which is equivalent to the code:
    ```
    nA = Node("A")
    nB = Node("B")
    r = Relation()
    nA.relate(r) # Note that nA stores r, not vice-versa
    r.to_node(nB)
    ```

    **Note**: While whitespace is entirely ignored in USL, it is used in the
    following examples for readability.

    A Relation can also have properties, which are defined in USL by a *relation
    spec* between braces before the relation. Within the braces, a relation spec
    has a 3-character format:
        <num><combo><branch>

    with the following meanings:

    - num: The number of nodes (1-9) that the related-to spec (node or
      branch) represents.

    - combo: Either `X` or `I`:
      - `X` means the nodes of the following node/branch spec are exclusive
        (only one path can be navigated along).
      - `I` means the nodes of the following node/branch spec are inclusive
        (any combination of branches can be followed simultaneously).

    - branch: Either `C` or `D`:
      - `C` means the following spec is a *node spec*, ie. represents one or
        more (as per <num>) nodes with consistent (the same) substructure.
      - `D` means the following spec is a *branch spec*, ie. represents one
        or more (as per <num>) node with divergent (different)
        substructures. A branch spec is a list of <num> sub-trees (containing
        node specs, relations, relation specs, and/or branch specs), surrounded
        by brackets, eg. `... {2XD}-> (A, B)`.

    **Note**: If a relation spec isn't given, then `{1XC}` is assumed.

    Basic examples of relation specs:
    - `A {2XC}-> B` - produces a tree with one "A" node that links (by graph
      edges) to two "B" nodes, though only one of those edges can be followed.
    - `A {2IC}-> B` - produces a tree with one "A" node that links to two "B"
      nodes, any combination of which (neither, one, the other, or both) can be
      followed.
    - `A {2XD}-> (B, C)` - produces a tree with one "A" node that links to a
      "B" node and a "C" node, only one of which ("B" or "C") can be followed.
    - `A {2ID}-> (B, C)` - produces a tree with one "A" node that links to a
      "B" node and a "C" node, any combination of which can be followed.
    
    More complex example:
        A -> B -> {2IC}-> C -> D {2XD}-> (E {3IC}-> F {2XC}-> G, E -> GXX)
    
    Which produces the tree:
    A
    \\- B
       |- C
       |  \\- D {VVV Exclusive}
       |     |- E
       |     |  |- F {VVV Exclusive}
       |     |  |  |- G
       |     |  |  \\- G
       |     |  |- F {VVV Exclusive}
       |     |  |  |- G
       |     |  |  \\- G
       |     |  \\- F {VVV Exclusive}
       |     |     |- G
       |     |     \\- G
       |     \\- E
       |        \\- GXX
       \\- C
          \\- D {VVV Exclusive}
             |- E
             |  |- F {VVV Exclusive}
             |  |  |- G
             |  |  \\- G
             |  |- F {VVV Exclusive}
             |  |  |- G
             |  |  \\- G
             |  \\- F {VVV Exclusive}
             |     |- G
             |     \\- G
             \\- E
                \\- GXX

    Notably, it is also possible to continue after a branch spec, like so:
        A {2XD}-> (B, C) -> D

    Which produces the tree:
    A
    |- B
    |  \\- D
    \\- C
       \\- D
    """

    def __init__(self, num=1, combo="X"):
        self.num = int(num)
        if combo == "I":
            self.inclusive = True
        elif combo == "X":
            self.inclusive = False
        else:
            raise ValueError(f"not a valid combinatoral spec: {combo}")

        self.next = None

    def get_num(self):
        return self.num
    
    def is_inclusive(self):
        return self.inclusive

    def get_next(self):
        return self.next

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
    """
    A node spec.
    
    A node spec represents one or more nodes in a tree. The exact number of
    nodes it represents is relative to the current number of heads (which
    depends on how many one-to-many relations have been specified so far) and
    the <num> specified in the relation spec (if a relation spec is given).

    For example, in the USL:
        A {2XC}-> {2XC}B -> C

    The node spec:
    - `A` represents one node (the root node).
    - `B` represents two nodes ("two per A", as per the relation spec).
    - `C` represents four nodes ("two per B", where there are two Bs)

    Assuming no divergent relations, the number of nodes a node spec represents
    is the product of the <num>s of all relation specs before it. With divergent
    relations, only the sub-trees in which the node spec is given are included
    in the calculation.

    See Relation's docs for more information.
    """

    def __init__(self, name):
        self.name = name
        self.relation = None

    def get_name(self):
        return self.name

    def get_relation(self):
        return self.relation

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
    """
    Provides a fluent interface for building complex tree specs.

    The interface is intended to make writing tree specs in Python look more
    like nested objects, in the same way as you would nest lists, tuples, dicts,
    etc.
    
    See the test suite for examples.
    """

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

# Parser (Str -> Object Model)
# --------------------------------------------------

def _get_next_node(rest, spec_str):
    """
    Parse the next part as a node spec.

    A node spec is any name that doesn't include `{`, `}`, or `->`.
    """

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
    """
    Parse the next part as a branch spec.

    A branch spec is a comma-separated list of subtrees, surrounded by brackets,
    like `(A -> B, X, Y -> Z)`.
    """

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
    builders = list(map(lambda subtree_str: _parse(subtree_str), subtrees_str))

    # Return needed values
    return (builders, rel_spec, rest)

def _parse(spec_str: str) -> Optional[Builder]:
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

def parse(spec_str: str) -> Optional[Node]:
    """Parse the given spec string into a spec tree."""

    builder = _parse(spec_str)
    if builder is None:
        return builder
    else:
        return builder.get_root()

# Generator (Object Model -> Graph)
# --------------------------------------------------

def graph(spec: Optional[Node]) -> gv.Digraph:
    graph = gv.Digraph(graph_attr={"rankdir": "BT"})

    if spec is None:
        return graph

    index = itertools.count() # Unique-valued sequence

    # Root node
    graph_root = str(next(index))
    graph.node(graph_root, label=spec.get_name())
    graph_leaves = [graph_root]
    spec_ends = [spec]

    # Other nodes
    while len(spec_ends) > 0:
        # Decend through the list of ends in reverse order, removing any that
        # have no relation.
        new_leaves = []
        new_ends = []
        for layer_node_i in range(len(spec_ends)-1, -1, -1):
            spec_end = spec_ends[layer_node_i]

            rel = spec_end.get_relation()
            if rel is None:
                del spec_ends[layer_node_i]
                continue

            num = rel.get_num()
            inc = rel.is_inclusive()
            next_nodes = rel.get_next()
            
            if num == 1:
                color = "black"
            else:
                if inc:
                    color = "blue"
                else:
                    color = "red"

            # Handle node specs, (must be duplicated by reference) and branch
            # specs (sub-nodes are already listed in full) consistently.
            if not utils.is_iterable(next_nodes):
                leaf_branch = [next_nodes] * num
            else:
                leaf_branch = next_nodes

            for node in leaf_branch:
                new_leaf = str(next(index))

                new_leaves.append(new_leaf)
                new_ends.append(node)

                graph.node(new_leaf, label=node.get_name())
                graph.edge(graph_leaves[layer_node_i], new_leaf, color=color)

        # Bump up the leaves and ends to the next layer
        graph_leaves = new_leaves
        spec_ends = new_ends

    return graph

# Direct Usage
# --------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "You must provide a spec argument.",
            "Syntax: python upgradespec.py <spec_str>",
            sep="\n"
        )
    spec_str = sys.argv[1]

    spec = parse(spec_str)
    g = graph(spec)
    g.render("graph", format="png", cleanup=True)
