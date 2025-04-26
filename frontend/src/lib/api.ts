// API base URL
const API_BASE_URL = 'http://localhost:5000';

// Types
export interface Player {
  id: number;
  name: string;
}

export interface Team {
  id: number;
  name: string;
}

export interface Match {
  id: number;
  homePlayer: Player;
  awayPlayer: Player;
  homeTeam: Team;
  awayTeam: Team;
  fixtureStart: string;
  raw_data: any;
}

export interface Prediction {
  fixtureId: number;
  homePlayer: Player;
  awayPlayer: Player;
  homeTeam: Team;
  awayTeam: Team;
  fixtureStart: string;
  prediction: {
    home_win_probability: number;
    away_win_probability: number;
    predicted_winner: 'home' | 'away';
    confidence: number;
  };
  score_prediction: {
    home_score: number;
    away_score: number;
    total_score: number;
    score_diff: number;
  };
  generated_at: string;
}

export interface PredictionStats {
  total_matches: number;
  home_wins_predicted: number;
  away_wins_predicted: number;
  avg_confidence: number;
  model_accuracy: number;
  last_updated: string;
}

// Player stats interface
export interface PlayerStats {
  player_id: number;
  player_name: string;
  total_matches: number;
  wins: number;
  losses: number;
  total_score: number;
  scores_list: number[];
  last_5_matches: {
    date: string | null;
    opponent_id: string;
    opponent_name: string;
    team_id: string;
    team_name: string;
    score: number;
    opponent_score: number;
    win: boolean;
  }[];
  teams_used: Record<string, {
    team_name: string;
    matches: number;
    wins: number;
    losses: number;
    total_score: number;
    win_rate: number;
    avg_score: number;
  }>;
  opponents_faced: Record<string, {
    matches: number;
    wins: number;
    losses: number;
    total_score: number;
    scores_against: number[];
    win_rate: number;
    avg_score: number;
    avg_score_against: number;
  }>;
}

// API functions
export async function getPredictions(): Promise<Prediction[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/predictions`);
    if (!response.ok) {
      throw new Error('Failed to fetch predictions');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching predictions:', error);
    return [];
  }
}

// Function to get player stats
export async function getPlayerStats(): Promise<Record<string, PlayerStats>> {
  try {
    // Fetch player stats from the backend
    const response = await fetch(`${API_BASE_URL}/api/player-stats`);

    if (!response.ok) {
      throw new Error('Failed to fetch player stats');
    }

    // The API returns an array, but we need a record/object
    const playerStatsArray = await response.json();

    // Convert array to record/object with player ID as key
    const playerStatsRecord: Record<string, PlayerStats> = {};

    // If the response is an array (from the API endpoint)
    if (Array.isArray(playerStatsArray)) {
      playerStatsArray.forEach(player => {
        if (player.id) {
          playerStatsRecord[player.id] = {
            player_id: parseInt(player.id),
            player_name: player.player_name,
            total_matches: player.total_matches,
            wins: player.wins,
            losses: player.losses,
            total_score: player.total_score,
            scores_list: player.scores_list || [],
            last_5_matches: player.last_5_matches || [],
            teams_used: player.teams_used || {},
            opponents_faced: player.opponents_faced || {}
          };
        }
      });
      return playerStatsRecord;
    }
    // If it's already a record (from the file directly)
    else if (typeof playerStatsArray === 'object' && !Array.isArray(playerStatsArray)) {
      return playerStatsArray as Record<string, PlayerStats>;
    }

    return {};
  } catch (error) {
    console.error('Error fetching player stats:', error);

    // Try to fetch the file directly as a fallback
    try {
      const fileResponse = await fetch(`${API_BASE_URL}/output/player_stats.json`);
      if (!fileResponse.ok) {
        throw new Error('Failed to fetch player stats file');
      }
      return await fileResponse.json();
    } catch (fallbackError) {
      console.error('Error fetching player stats file:', fallbackError);
      return {};
    }
  }
}

export async function refreshData(): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/refresh`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to refresh data');
    }

    const data = await response.json();
    return {
      success: true,
      message: data.message || 'Data refreshed successfully',
    };
  } catch (error) {
    console.error('Error refreshing data:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}

export async function getUpcomingMatches(): Promise<Match[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/upcoming-matches`);
    if (!response.ok) {
      throw new Error('Failed to fetch upcoming matches');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching upcoming matches:', error);
    return [];
  }
}

export async function getPredictionStats(): Promise<PredictionStats> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/prediction-stats`);
    if (!response.ok) {
      // If the endpoint doesn't exist, return default stats
      return {
        total_matches: 0,
        home_wins_predicted: 0,
        away_wins_predicted: 0,
        avg_confidence: 0,
        model_accuracy: 0,
        last_updated: new Date().toISOString()
      };
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching prediction stats:', error);
    // Return default stats on error
    return {
      total_matches: 0,
      home_wins_predicted: 0,
      away_wins_predicted: 0,
      avg_confidence: 0,
      model_accuracy: 0,
      last_updated: new Date().toISOString()
    };
  }
}
