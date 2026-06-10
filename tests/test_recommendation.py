def test_recommendation_logic():
    from app.recommendation import get_recommendation_text
    
    # Test critical
    result = get_recommendation_text(15, 0)
    assert "Water Needed Now" in result[0]
    
    # Test dry
    result = get_recommendation_text(30, 0)
    assert "Water Needed Soon" in result[0]
    
    # Test good
    result = get_recommendation_text(55, 0)
    assert "Water Level Good" in result[0]
    
    # Test rain override
    result = get_recommendation_text(30, 10)
    assert "Wait Due To Recent Rainfall" in result[1]