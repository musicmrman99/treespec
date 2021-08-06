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
    assert parse_spec("a->b") == Builder("a").to().node("b").get_root()

def test_two_equiv():
    assert parse_spec("a{1XC}->b") == Builder("a").to().node("b").get_root()

def test_f_invalid_rel_spec_format():
    with pytest.raises(ValueError):
        parse_spec("a{1}->b")

def test_f_invalid_rel_spec_missing_brace():
    with pytest.raises(ValueError):
        parse_spec("a{1IC->b")

    with pytest.raises(ValueError):
        parse_spec("a{1IC->b{1IC}->c")

def test_branch():
    assert parse_spec("a{2XC}->b") == Builder("a").to(2).node("b").get_root()

def test_branch_inclusive():
    assert parse_spec("a{2IC}->b") == Builder("a").to(2,"I").node("b").get_root()

def test_branch_divergent():
    root = (Builder("a")
        .to(2).branch(Builder("b"), Builder("b"))
        .get_root())
    parsed = parse_spec("a{2XD}->(b,b)")
    print(root.str(True))
    print(parsed.str(True))
    assert parsed == root

def test_branch_inclusive_divergent():
    assert parse_spec("a{2ID}->(b,b)") == (Builder("a")
        .to(2,"I").branch(Builder("b"), Builder("b"))
        .get_root())

def test_complex_consistent():
    assert parse_spec("L0 {3IC}-> L1 -> L2 {2XC}-> L3 -> L4") == (Builder("L0")
        .to(3,"I").node("L1")
        .to().node("L2")
        .to(2).node("L3")
        .to().node("L4")
        .get_root())

def test_complex_divergent():
    parse = parse_spec("L0 -> L1 {2ID}-> (L2 -> L3, L2 {2ID}-> (L3 -> L4, L3 -> L4 {2XC}-> L5 -> L6))")
    assert parse == (Builder("L0")
        .to().node("L1")
        .to(2,"I").branch(
            Builder("L2").to().node("L3"),
            Builder("L2").to(2,"I").branch(
                Builder("L3").to().node("L4"),
                Builder("L3").to().node("L4")
                    .to(2).node("L5")
                    .to().node("L6")
            )
        )
        .get_root())

def test_branch_consistent_continuation():
    assert parse_spec("a {2XD}-> (b, c) -> d") == (Builder("a")
        .to(2).branch(Builder("b"), Builder("c"))
        .to().node("d")
        .get_root())
