from upgradespec import *
import pytest

def test_empty():
    assert parse_spec("") == None

def test_one():
    assert parse_spec("a") == Node("a")

def test_f_arrow():
    with pytest.raises(ValueError):
        parse_spec("->")

def test_f_one_side_of_arrow():
    with pytest.raises(ValueError):
        parse_spec("a->")
    
    with pytest.raises(ValueError):
        parse_spec("->a")

def test_two():
    root = Node("a")
    root.to(Relation()).node(Node("b"))
    assert parse_spec("a->b") == root

def test_two_equiv():
    root = Node("a")
    root.to(Relation()).node(Node("b"))
    assert parse_spec("a{1IC}->b") == root

def test_f_invalid_rel_spec_format():
    with pytest.raises(ValueError):
        parse_spec("a{1}->b")

def test_f_invalid_rel_spec_missing_brace():
    with pytest.raises(ValueError):
        parse_spec("a{1IC->b")

    with pytest.raises(ValueError):
        parse_spec("a{1IC->b{1IC}->c")

def test_branch():
    root = Node("a")
    root.to(Relation(2)).node(Node("b"))
    assert parse_spec("a{2IC}->b") == root

def test_branch_exclusive():
    root = Node("a")
    root.to(Relation(2,"X")).node(Node("b"))
    assert parse_spec("a{2XC}->b") == root

def test_branch_divergent():
    root = Node("a")
    root.to(Relation(2)).branch(Node("b"), Node("b"))
    assert parse_spec("a{2ID}->(b,b)") == root

def test_branch_exclusive_divergent():
    root = Node("a")
    root.to(Relation(2,"X")).branch(Node("b"), Node("b"))
    assert parse_spec("a{2XD}->(b,b)") == root

def test_complex_consistent():
    root = Node("L0")
    (root.to(Relation(3)).node(Node("L1"))
        .to(Relation()).node(Node("L2"))
        .to(Relation(2,"X")).node(Node("L3"))
        .to(Relation()).node(Node("L4")))
    assert parse_spec("L0 {3IC}-> L1 -> L2 {2XC}-> L3 -> L4") == root

def test_complex_divergent():
    root = Node("L0")
    (root.to(Relation()).node(Node("L1"))
        .to(Relation(2)).branch(
            Node("L2").to(Relation()).node(Node("L3")),
            Node("L2").to(Relation(2)).branch(
                Node("L3")
                    .to(Relation()).node(Node("L4")),
                Node("L3")
                    .to(Relation()).node(Node("L4"))
                    .to(Relation(2,"X")).node(Node("L5"))
                    .to(Relation()).node(Node("L6"))
            )
        )
    )
    assert parse_spec("L0 -> L1 {2ID}-> (L2 -> L3, L2 {2ID}-> (L3 -> L4, L3 -> L4 {2XC}-> L5 -> L6))") == root
