from app import generate_bracket

def test_generate_bracket_length():
    teams = [{'name': f'Team{i}', 'players': []} for i in range(18)]
    bracket = generate_bracket(teams)
    assert len(bracket) >= 1

    total_matches = sum(len(round_) for round_ in bracket)
    # Winner emerges after total_matches games
    assert total_matches >= 17
