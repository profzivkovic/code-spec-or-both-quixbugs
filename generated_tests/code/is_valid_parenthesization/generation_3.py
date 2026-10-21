def test_is_valid_parenthesization_normal_cases(function):
    assert function('()') == True
    assert function('(())') == True
    assert function('(()())') == True

    assert function('((()))') == True
    assert function('())(') == False
    assert function('(()') == False
    assert function('))') == False
    assert function('()()') == True

    assert function('') == True

    assert function('(a)') == False
    assert function('a(b)c') == False
