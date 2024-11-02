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
| `!faction_analysis` | AI-powered faction strength analysis | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302284902288461884/Screenshot_2024-11-02_165501.png?ex=67278ed3&is=67263d53&hm=0eae6ac0d19bb1cc0fff651fc0af2720e64281fe7403522ed7cfb22aaffa0c2a&) |
| `!unit_stats` | Display unit statistics | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302283721302474932/Screenshot_2024-11-02_165016.png?ex=67278dba&is=67263c3a&hm=0d8ad6843edfa5687638d7124bf8d0e6d6c90c45e5c9ceb5f3f07e097479c537&) |
| `!compare_stats` | Compare two units | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302285419827691633/stats_comparison.png?ex=67278f4f&is=67263dcf&hm=01954ae21e230d452e4ed78c384f2d4dc6882ffbb4492bad2214b7eacab4ef00&) |
| `!faction_comparison` | Compare two factions | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302289051952611399/Screenshot_2024-11-02_171124.png?ex=672792b1&is=67264131&hm=69ed9fc556892c20a8c9270ba39e540671b6b2f90dd2cddf0c436736b8e3253b&) |

### Player Stats Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!kd_ratio_leaderboard` | Top K/D ratio players | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302286423151345754/Screenshot_2024-11-02_170104.png?ex=6727903e&is=67263ebe&hm=5a9b656026dcdfa4d628bb319e920a476796fe3fc9f76bc85b83275d19835593&) |
| `!historical_leaderboard` | Highest rated players | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302288274190106694/Screenshot_2024-11-02_170832.png?ex=672791f7&is=67264077&hm=7ed3e60c500676ac048e040e5559909d17bf72038505e177d2bb9355dcdbcd74&) |
| `!win_percentage_leaderboard` | Top win-rate players | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302289442865680475/Screenshot_2024-11-02_171306.png?ex=6727930e&is=6726418e&hm=69242c01fc8918fe6073810c12bb39f322928502981c2cbbf95c8268a0e43f01&) |
| `!display_team_elo` | Top 10 teams by Elo | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302291410770464939/Screenshot_2024-11-02_172102.png?ex=672794e3&is=67264363&hm=024c0012fa14a3e39a04561eac54d0125062540871c6c4c7360db2e6c50a236a&) |
| `!player_history` | Individual player stats | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302292120199102564/Screenshot_2024-11-02_172352.png?ex=6727958c&is=6726440c&hm=a8a3b235b77eff3059b325dd3a3b1baf1cfb399d2e1d2bd1dc7d30b4358629bd&) |

### Reference Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!commands` | List all available commands | - |
| `!tier_list` | Display unit tier list | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302287861025865779/3v3_Tier_List.png?ex=67279195&is=67264015&hm=a1408d55711fb42d1a8c1d33aec0ad63a85668927e4657c4fbb25eea2ae6e539&) |
| `!land_guide_playlist` | Access guide videos | [View Example](https://cdn.discordapp.com/attachments/524522932823785485/1302286745114775653/Screenshot_2024-11-02_170224.png?ex=6727908b&is=67263f0b&hm=cf6ba6d7239b299b096eb2338eef85286dbfc4b2249e4d668e919fe4eae16f34&) |

> **⚠️ Note**: The `!faction_analysis` command uses AI and may occasionally provide inaccurate information due to AI limitations.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
