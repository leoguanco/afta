-- Insert placeholder matches for custom video uploads
INSERT INTO matches (match_id, source, match_metadata)
VALUES ('2-boca', 'custom', '{"home_team_name": "Home", "away_team_name": "Away"}')
ON CONFLICT (match_id) DO NOTHING;

INSERT INTO matches (match_id, source, match_metadata)
VALUES ('1-boca', 'custom', '{"home_team_name": "Home", "away_team_name": "Away"}')
ON CONFLICT (match_id) DO NOTHING;
