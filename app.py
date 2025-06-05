import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Data storage
categories = {
    'group1_men': {'label': 'Группа 1 - Мужчины (2x2)', 'team_size': 2},
    'group1_women': {'label': 'Группа 1 - Женщины (2x2)', 'team_size': 2},
    'group1_mixed': {'label': 'Группа 1 - Микст (2x2)', 'team_size': 2},
    'group2_men': {'label': 'Группа 2 - Мужчины (3x3)', 'team_size': 3},
    'group2_women': {'label': 'Группа 2 - Женщины (3x3)', 'team_size': 3},
    'group2_mixed': {'label': 'Группа 2 - Микст (3x3)', 'team_size': 3},
}

tournaments = {key: {'teams': [], 'bracket': []} for key in categories}

def generate_bracket(teams):
    """Generate knockout bracket for given teams using byes."""
    n = len(teams)
    if n == 0:
        return []

    # Next power of two determines full bracket size
    m = 1
    while m < n:
        m *= 2

    teams_copy = teams[:] + [None] * (m - n)
    bracket = []

    current = [
        {
            'team1': teams_copy[i],
            'team2': teams_copy[i + 1],
            'score1': None,
            'score2': None,
            'winner': None,
        }
        for i in range(0, len(teams_copy), 2)
    ]
    bracket.append(current)

    teams_in_round = len(current)
    while teams_in_round > 1:
        next_round = [
            {
                'team1': None,
                'team2': None,
                'score1': None,
                'score2': None,
                'winner': None,
            }
            for _ in range(teams_in_round // 2)
        ]
        bracket.append(next_round)
        teams_in_round //= 2

    advance_byes(bracket)
    return bracket


def advance_byes(bracket):
    """Automatically advance teams where opponent is None."""
    for round_idx, round_ in enumerate(bracket[:-1]):
        for match_idx, match in enumerate(round_):
            if match['winner'] is None:
                if match['team1'] is None and match['team2'] is None:
                    continue
                if match['team1'] is None:
                    match['winner'] = match['team2']
                elif match['team2'] is None:
                    match['winner'] = match['team1']
                else:
                    continue

                next_match = bracket[round_idx + 1][match_idx // 2]
                pos = 0 if match_idx % 2 == 0 else 1
                next_match[f'team{pos + 1}'] = match['winner']

@app.route('/')
def index():
    return render_template('index.html', categories=categories)

@app.route('/<category>/teams')
def show_teams(category):
    cat = categories[category]
    data = tournaments[category]
    return render_template('teams.html', category=category, cat=cat, data=data)

@app.route('/<category>/add_team', methods=['GET', 'POST'])
def add_team(category):
    cat = categories[category]
    if request.method == 'POST':
        team_name = request.form['team_name']
        players = [p for p in request.form.getlist('player') if p]
        if len(players) != cat['team_size']:
            return render_template('add_team.html', category=category, cat=cat, error='Укажите всех игроков')
        tournaments[category]['teams'].append({'name': team_name, 'players': players})
        return redirect(url_for('show_teams', category=category))
    return render_template('add_team.html', category=category, cat=cat)

@app.route('/<category>/start')
def start_tournament(category):
    data = tournaments[category]
    data['bracket'] = generate_bracket(data['teams'])
    return redirect(url_for('view_bracket', category=category))

@app.route('/<category>/bracket', methods=['GET', 'POST'])
def view_bracket(category):
    data = tournaments[category]
    if request.method == 'POST':
        round_idx = int(request.form['round'])
        match_idx = int(request.form['match'])
        score1 = int(request.form['score1'])
        score2 = int(request.form['score2'])
        match = data['bracket'][round_idx][match_idx]
        match['score1'] = score1
        match['score2'] = score2
        winner = match['team1'] if score1 > score2 else match['team2']
        match['winner'] = winner

        # propagate winner
        next_round_idx = round_idx + 1
        if next_round_idx < len(data['bracket']):
            next_match_idx = match_idx // 2
            pos = 0 if match_idx % 2 == 0 else 1
            data['bracket'][next_round_idx][next_match_idx][f'team{pos+1}'] = winner
    return render_template('bracket.html', category=category, cat=categories[category], data=data)

if __name__ == '__main__':
    # Railway typically provides the PORT environment variable. Default to 8080
    # so the app runs locally without extra configuration.
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
