def test_get_factors_normal_case():
    assert get_factors(12) == [2, 6]

def test_get_factors_prime_number():
    assert get_factors(7) == []

def test_get_factors_one():
    assert get_factors(1) == []

def test_get_factors_negative_number():
    with pytest.raises(ValueError):
        get_factors(-5)

def test_get_factors_zero():
    with pytest.raises(ValueError):
        get_factors(0)