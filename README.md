# Discord Bot for Rome 2 Total War

A Discord bot providing comprehensive stats, analysis, and comparisons for Rome 2 Total War game units, factions, and player performance.

## Features

- Faction analysis with AI-powered insights
- Unit stats and faction comparisons
- Player leaderboards and history
- Team Elo ratings
- Historical results tracking

## Installation

### Prerequisites

- Python 3.9 or later
- Discord Developer Account
- Bot Token from Discord Developer Portal
- Google Gemini API KEY
- Youtube API Key

### Setup Methods

#### Method 1: Local Installation

1. Clone the repository
2. Install dependencies:

   ```bash
   pip3 install -r requirements.txt
   ```

3. Configure environment variables in `.env`:

    ```env
   BOT_TOKEN=your_bot_token here
   CHANNEL=main_channel_id
   DEV_CHANNEL_ID=dev_channel_id (can remove the use of this env variable if you don't want to use a separate channel/server for testing new commands or updates to existing ones)
   GEMINI_API_KEY=your_gemini_api_key here
   YOUTUBE_API_KEY=your youtube api key here
   YOUTUBE_CHANNEL_ID = your youtube channel id here(for !land_guide command)
   PLAYLIST_LINK = your playlist link (for the same command as youtube_channel_id)
   ```

#### Method 2: Docker Installation

```bash
docker compose up -d
```

### Discord Bot Setup

1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Add a bot to your application
4. Enable MESSAGE CONTENT INTENT
5. Copy the bot token to `.env`
6. Invite bot to your server using OAuth2 URL Generator

### Channel Configuration (Optional)

To restrict bot commands to specific channels:

1. Enable Discord Developer Mode
2. Right-click desired channel → Copy ID
3. Add to `.env`:
   - Main channel: `CHANNEL=channel_id`
   - Dev channel: `DEV_CHANNEL_ID=channel_id`

## Commands

### Analysis Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!faction_analysis` | AI-powered faction strength analysis | [View Example](https://imgur.com/gMB1w3Q) |
| `!unit_stats` | Display unit statistics | [View Example](https://imgur.com/Op4IuYs) |
| `!compare_stats` | Compare two units | [View Example](https://imgur.com/6PQtKYb) |
| `!faction_comparison` | Compare two factions | [View Example](https://imgur.com/uFitkwt) |

### Player Stats Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!kd_ratio_leaderboard` | Top K/D ratio players | [View Example](https://imgur.com/HkjLkyX) |
| `!historical_leaderboard` | Highest rated players | [View Example](https://imgur.com/W1qpNPj) |
| `!win_percentage_leaderboard` | Top win-rate players | [View Example](https://imgur.com/MnBY3oN) |
| `!display_team_elo` | Top 10 teams by Elo | [View Example](https://imgur.com/kebXqcm) |
| `!player_history` | Individual player stats | [View Example](https://imgur.com/MLZLJbk) |

### Reference Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!commands` | List all available commands | - |
| `!tier_list` | Display unit tier list | [View Example](https://imgur.com/jBgSs1Q) |
| `!land_guide_playlist` | Access guide videos | [View Example](https://imgur.com/jw9AdU5) |

> **⚠️ Note**: The `!faction_analysis` command uses AI and may occasionally provide inaccurate information due to AI limitations.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
