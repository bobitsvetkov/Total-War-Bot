async def setup_cogs(bot):
    from cogs.unit_comparison.unit_comparison import UnitStatsComparison
    from cogs.faction_analysis.bot import FactionAnalysisBot
    from cogs.faction_comparison.faction_comparison import FactionComparison
    from cogs.unit_stats.unit_stats import UnitStats
    from cogs.tier_list.tier_list import TierList
    from cogs.commands.commands_list import CommandsList
    from cogs.historical_results.historical_results import HistoricalResults
    from cogs.elo_rating.display_elo import TeamDisplaySystem
    from cogs.land_guide.land_guide_command import LandGuidePlaylist

    cogs = [
        FactionAnalysisBot(bot),
        FactionComparison(bot),
        UnitStats(bot),
        TierList(bot),
        CommandsList(bot),
        HistoricalResults(bot),
        TeamDisplaySystem(bot),
        UnitStatsComparison(bot),
        LandGuidePlaylist(bot)
    ]

    for cog in cogs:
        await bot.add_cog(cog)