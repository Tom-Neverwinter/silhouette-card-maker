# Simplified Plugin Manager for Silhouette Card Maker
# ===================================================

# Plugin configuration file path
$script:pluginConfigFile = Join-Path $env:APPDATA "SilhouetteCardMaker\plugin_config.json"

# Default plugin configuration
$script:defaultPluginConfig = @{
    enabledPlugins = @()
    pluginSettings = @{}
    lastScan = $null
    autoDetect = $true
}

# Load plugin configuration
function Load-PluginConfig {
    if (Test-Path $script:pluginConfigFile) {
        try {
            $config = Get-Content $script:pluginConfigFile -Raw | ConvertFrom-Json
            # Ensure enabledPlugins is an array
            if ($config.enabledPlugins -is [string]) {
                $config.enabledPlugins = @($config.enabledPlugins)
            } elseif ($config.enabledPlugins -is [array]) {
                # Already an array, keep as is
            } else {
                $config.enabledPlugins = @()
            }
            return $config
        }
        catch {
            Write-Warning "Failed to load plugin config: $($_.Exception.Message)"
        }
    }
    return $script:defaultPluginConfig
}

# Save plugin configuration
function Save-PluginConfig {
    param($config)
    
    try {
        $configDir = Split-Path $script:pluginConfigFile -Parent
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        $config | ConvertTo-Json -Depth 3 | Set-Content $script:pluginConfigFile -Encoding UTF8
        return $true
    }
    catch {
        Write-Warning "Failed to save plugin config: $($_.Exception.Message)"
        return $false
    }
}

# Get all plugins (simplified)
function Get-AllPlugins {
    $plugins = @()
    
    # Complete plugin list (alphabetically ordered)
    $pluginList = @(
        @{ Name = "7th_sea"; DisplayName = "7th Sea CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "age_of_empires"; DisplayName = "Age of Empires II Expandable Card Game"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "aliens_vs_predator"; DisplayName = "Aliens Vs Predator CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "altered"; DisplayName = "Altered"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "anachronism"; DisplayName = "Anachronism"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "avatar_last_airbender"; DisplayName = "Avatar: The Last Airbender TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "babylon_5"; DisplayName = "Babylon 5 CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "battlestar_galactica"; DisplayName = "Battlestar Galactica CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "battletech"; DisplayName = "Battletech CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "battletech_ccg"; DisplayName = "Battletech CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "behind_tcg"; DisplayName = "Behind TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "bella_sara"; DisplayName = "Bella Sara TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "ben_10"; DisplayName = "Ben 10 CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "beyblade"; DisplayName = "Beyblade CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "bible_battles"; DisplayName = "Bible Battles TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "bleach"; DisplayName = "Bleach TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "blood_wars"; DisplayName = "Blood Wars CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "blue_dragon"; DisplayName = "Blue Dragon RPCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "buffy_vampire_slayer"; DisplayName = "Buffy the Vampire Slayer CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "call_of_cthulhu"; DisplayName = "Call of Cthulhu CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cardcaptors"; DisplayName = "Cardcaptors TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cards_against_humanity"; DisplayName = "Cards Against Humanity"; Category = "Party Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "case_closed"; DisplayName = "Case Closed TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "caster_chronicles"; DisplayName = "Caster Chronicles TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "ccgtrader"; DisplayName = "CCGTrader (Universal)"; Category = "Universal"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cfvanguard"; DisplayName = "CF Vanguard"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "chaotic"; DisplayName = "Chaotic TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "city_of_heroes"; DisplayName = "City of Heroes CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "clone_wars_adventures"; DisplayName = "Clone Wars Adventures"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "club_penguin"; DisplayName = "Club Penguin TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "codename_kids_next_door"; DisplayName = "Codename: Kids Next Door TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "conan"; DisplayName = "Conan CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cosplay_deviants"; DisplayName = "Cosplay Deviants TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "crown_of_emperor"; DisplayName = "Crown of the Emperor"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "crystalicum"; DisplayName = "Crystalicum: KrysztaÅ‚owa Gra Karciana"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cyberpunk"; DisplayName = "Cyberpunk CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dark_age"; DisplayName = "Dark Age: Feudal Lords CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dark_eden"; DisplayName = "Dark Eden CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dark_force"; DisplayName = "Dark Force CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "deadlands"; DisplayName = "Deadlands: Lost Colony - Showdown CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "death_note"; DisplayName = "Death Note TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "deus"; DisplayName = "Deus TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dice_masters"; DisplayName = "Dice Masters"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "digimon"; DisplayName = "Digimon"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "digimon_d_tector"; DisplayName = "Digimon D-Tector CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "digimon_digi_battle"; DisplayName = "Digimon: Digi-Battle CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "digimon_fusion"; DisplayName = "Digimon Fusion CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dino_hunt"; DisplayName = "Dino Hunt"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dinosaur_king"; DisplayName = "Dinosaur King TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "disney_princess"; DisplayName = "Disney Princess TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dixie"; DisplayName = "Dixie CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "doctor_who"; DisplayName = "Doctor Who: The CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "doctor_who_alien_armies"; DisplayName = "Doctor Who: Alien Armies TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "doctor_who_battles_in_time"; DisplayName = "Doctor Who: Battles in Time"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "doomtown"; DisplayName = "Doomtown CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "doomtrooper"; DisplayName = "Doomtrooper CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragoborne"; DisplayName = "Dragoborne: Rise to Supremacy"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_gt"; DisplayName = "Dragon Ball GT TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_super"; DisplayName = "Dragon Ball Super"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_z"; DisplayName = "Dragon Ball Z CCG/TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_booster"; DisplayName = "Dragon Booster TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_quest"; DisplayName = "Dragon Quest TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_storm"; DisplayName = "Dragon Storm CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dreadnought"; DisplayName = "Dreadnought TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dredd"; DisplayName = "Dredd CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "duel_masters"; DisplayName = "Duel Masters TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dune"; DisplayName = "Dune CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "eagles"; DisplayName = "Eagles CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "echelons_of_fire"; DisplayName = "Echelons of Fire CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "echelons_of_fury"; DisplayName = "Echelons of Fury CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "el_mundo_aguila_roja"; DisplayName = "El Mundo de Ãguila-Roja CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "epic"; DisplayName = "Epic TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "epic_battles"; DisplayName = "Epic Battles TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "eve_second_genesis"; DisplayName = "EVE: The Second Genesis CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "exodus"; DisplayName = "Exodus TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "flesh_and_blood"; DisplayName = "Flesh and Blood"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fluxx"; DisplayName = "Fluxx"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fantasy_adventures"; DisplayName = "Fantasy Adventures CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fast_break"; DisplayName = "Fast Break: One-on-One Basketball"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fight_klub"; DisplayName = "Fight Klub TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fire_emblem"; DisplayName = "Fire Emblem TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fire_emblem_cipher"; DisplayName = "Fire Emblem Cipher TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "firestorm"; DisplayName = "Firestorm TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "flights_of_fantasy"; DisplayName = "Flights of Fantasy CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "force_of_will"; DisplayName = "Force of Will"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fullmetal_alchemist"; DisplayName = "Fullmetal Alchemist TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "future_card_buddyfight"; DisplayName = "Future Card Buddyfight"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "g_i_joe"; DisplayName = "G.I. Joe TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "game_of_thrones_ccg"; DisplayName = "A Game of Thrones CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "grand_archive"; DisplayName = "Grand Archive"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "galactic_empires"; DisplayName = "Galactic Empires CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "gate_ruler"; DisplayName = "Gate Ruler TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "genio_cards_marvel"; DisplayName = "Genio Cards - Marvel"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "gogo_crazy_bones"; DisplayName = "Gogo's Crazy Bones TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "gormiti"; DisplayName = "Gormiti TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "gridiron_fantasy_football"; DisplayName = "Gridiron Fantasy Football CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "guardians"; DisplayName = "Guardians CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "gundam"; DisplayName = "Gundam"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "gundam_ms_war"; DisplayName = "Gundam M.S. War TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "gundam_war_2005"; DisplayName = "Gundam War CCG (2005)"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "gwiezdna_kohorta"; DisplayName = "Gwiezdna Kohorta CCG (Star Cohort)"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "harry_potter"; DisplayName = "Harry Potter TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "highlander"; DisplayName = "Highlander: The Card Game CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "illuminati"; DisplayName = "Illuminati: New World Order CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "inuyasha"; DisplayName = "Inuyasha TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "legend_of_the_five_rings"; DisplayName = "Legend of the Five Rings"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "lorcana"; DisplayName = "Lorcana"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "marvel_champions"; DisplayName = "Marvel Champions"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "medabots"; DisplayName = "Medabots TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "megaman_nt_warrior"; DisplayName = "MegaMan: NT Warrior TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "meta_zoo"; DisplayName = "MetaZoo"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "middle_earth_ccg"; DisplayName = "Middle Earth CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "monty_python"; DisplayName = "Monty Python and the Holy Grail CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat"; DisplayName = "Mortal Kombat Kard Game CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mtg"; DisplayName = "Magic: The Gathering"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "munchkin"; DisplayName = "Munchkin"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "naruto"; DisplayName = "Naruto CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "netrunner"; DisplayName = "Netrunner"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "netrunner_ccg"; DisplayName = "NetRunner CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "one_piece"; DisplayName = "One Piece"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "one_piece_ccg"; DisplayName = "One Piece CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "overpower"; DisplayName = "Over Power CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "pirates_caribbean"; DisplayName = "Pirates of the Caribbean TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "pokemon"; DisplayName = "Pokemon"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "power_rangers"; DisplayName = "Power Rangers CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "redemption"; DisplayName = "Redemption CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "riftbound"; DisplayName = "Riftbound"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "rifts"; DisplayName = "Rifts CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "sailor_moon"; DisplayName = "Sailor Moon CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "shadowfist"; DisplayName = "Shadowfist CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "shadowrun"; DisplayName = "Shadowrun: The TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "shadowverse_evolve"; DisplayName = "Shadowverse Evolve"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "shaman_king"; DisplayName = "Shaman King TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "simpsons"; DisplayName = "The Simpsons TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "spellfire"; DisplayName = "Spellfire CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "spongebob"; DisplayName = "SpongeBob SquarePants TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "spycraft"; DisplayName = "Spycraft CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_realms"; DisplayName = "Star Realms"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_trek_ccg"; DisplayName = "Star Trek CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_wars_ccg"; DisplayName = "Star Wars CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_wars_unlimited"; DisplayName = "Star Wars Unlimited"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "teenage_mutant_ninja_turtles"; DisplayName = "Teenage Mutant Ninja Turtles TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "transformers"; DisplayName = "Transformers TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "union_arena"; DisplayName = "Union Arena"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "universus"; DisplayName = "Universus"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "vampire_eternal_struggle"; DisplayName = "Vampire: The Eternal Struggle"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "vs_system"; DisplayName = "VS System CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "warlord"; DisplayName = "Warlord: Saga of the Storm"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "warhammer_40k"; DisplayName = "Warhammer 40,000 CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "weiss_schwarz"; DisplayName = "Weiss Schwarz"; Category = "Card Game"; CardSize = "japanese"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wheel_of_time"; DisplayName = "Wheel of Time CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "world_of_warcraft"; DisplayName = "World of Warcraft TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "x_men"; DisplayName = "X-Men TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "yugioh"; DisplayName = "Yu-Gi-Oh!"; Category = "Card Game"; CardSize = "japanese"; HasCLI = $true; HasAPI = $true },
        @{ Name = "yu_yu_hakusho"; DisplayName = "Yu Yu Hakusho TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "z_g"; DisplayName = "Z-G"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "zatch_bell"; DisplayName = "Zatch Bell! The Card Battle"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "zombie_world_order"; DisplayName = "Zombie World Order"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "zu_tiles_hime"; DisplayName = "Zu Tiles: Hime"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "hecatomb"; DisplayName = "Hecatomb CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "hercules_legendary_journeys"; DisplayName = "Hercules: The Legendary Journeys TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "heresy_kingdom_come"; DisplayName = "Heresy: Kingdom Come CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "hero_attax"; DisplayName = "Hero Attax"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "high_stakes_drifter"; DisplayName = "High Stakes Drifter CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "humaliens"; DisplayName = "HumAliens CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "huntik"; DisplayName = "Huntik TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "hyborian_gates"; DisplayName = "Hyborian Gates CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "imajica"; DisplayName = "Imajica CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "inazuma_eleven"; DisplayName = "Inazuma Eleven TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "inferno_jcc"; DisplayName = "Inferno JCC"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "initial_d"; DisplayName = "Initial-D CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "intervention_divine"; DisplayName = "Intervention Divine CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "jackie_chan_adventures"; DisplayName = "Jackie Chan Adventures"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "james_bond_007"; DisplayName = "James Bond 007 CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "maple_story_itcg"; DisplayName = "MapleStory iTCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "marvel_recharge"; DisplayName = "Marvel ReCharge CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "marvel_super_hero_squad"; DisplayName = "Marvel Super Hero Squad"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "marvel_ultimate_battles"; DisplayName = "Marvel Ultimate Battles TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "meta_x"; DisplayName = "Meta X TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "monster_hunter_hunting_card"; DisplayName = "Monster Hunter Hunting Card TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "monster_rancher"; DisplayName = "Monster Rancher CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "monster_tykes"; DisplayName = "Monster Tykes CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "monsuno"; DisplayName = "Monsuno TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "my_little_pony"; DisplayName = "My Little Pony CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mystical_empire"; DisplayName = "Mystical Empire CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "myths_and_legends"; DisplayName = "Myths and Legends CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "nascar_racing_challenge"; DisplayName = "NASCAR Racing Challenge TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "nba_showdown"; DisplayName = "NBA Showdown TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "nfl_five"; DisplayName = "NFL Five TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "nfl_showdown"; DisplayName = "NFL Showdown CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "nascar_race_day_2006"; DisplayName = "Nascar Race Day 2006 CRG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "neopets"; DisplayName = "Neopets TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "nerve"; DisplayName = "Nerve CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "on_the_edge"; DisplayName = "On The Edge CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "one_on_one_hockey_challenge"; DisplayName = "One-On-One Hockey Challenge CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "ophidian"; DisplayName = "Ophidian CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "pez"; DisplayName = "PEZ CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "pirates_spanish_main"; DisplayName = "Pirates of the Spanish Main"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "power_cardz"; DisplayName = "Power Cardz CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "power_rangers_action_card"; DisplayName = "Power Rangers Action Card Game"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "quest_for_grail"; DisplayName = "Quest for the Grail CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "rage_apocalypse"; DisplayName = "Rage: Apocalypse CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "rage_tribal_war"; DisplayName = "Rage: Tribal War CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "red_zone"; DisplayName = "Red Zone CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "redakai_conquer_kairu"; DisplayName = "Redakai: Conquer the Kairu TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "rocketmen"; DisplayName = "Rocketmen"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "ruins_world"; DisplayName = "Ruins World CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "scooby_doo_expandable"; DisplayName = "Scooby Doo Expandable Card Game"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "sim_city"; DisplayName = "Sim City CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "sonic_x"; DisplayName = "Sonic X TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "sorcerers_magic_kingdom"; DisplayName = "Sorcerers of the Magic Kingdom"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "spacix"; DisplayName = "Spacix TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "speed_racer"; DisplayName = "Speed Racer CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_quest"; DisplayName = "Star Quest CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_trek_first_edition"; DisplayName = "Star Trek CCG First Edition"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_trek_second_edition"; DisplayName = "Star Trek CCG Second Edition"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_trek_card_game"; DisplayName = "Star Trek: The Card Game CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_wars_force_attax"; DisplayName = "Star Wars Force Attax"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_wars_pocketmodel"; DisplayName = "Star Wars Pocketmodel TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_wars_rebel_attax"; DisplayName = "Star Wars Rebel Attax"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_wars_tcg"; DisplayName = "Star Wars TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_wars_destiny"; DisplayName = "Star Wars: Destiny"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "star_of_guardians"; DisplayName = "Star of the Guardians"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "stargate"; DisplayName = "Stargate TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "super_deck"; DisplayName = "Super Deck! TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "super_nova"; DisplayName = "Super Nova CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "survivor"; DisplayName = "Survivor TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tank_commander"; DisplayName = "Tank Commander CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "teen_titans"; DisplayName = "Teen Titans CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "teenage_mutant_ninja_turtles_turtle_power"; DisplayName = "Teenage Mutant Ninja Turtles: Turtle Power"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tempest_of_gods"; DisplayName = "Tempest of the Gods CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "terror"; DisplayName = "Terror CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "condemned"; DisplayName = "The Condemned CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "crow"; DisplayName = "The Crow CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragons_wrath"; DisplayName = "The Dragon's Wrath CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "eye_of_judgment"; DisplayName = "The Eye of Judgment"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "last_crusade"; DisplayName = "The Last Crusade CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "nightmare_before_christmas"; DisplayName = "The Nightmare Before Christmas TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "simpsons_tcg"; DisplayName = "The Simpsons TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "spoils"; DisplayName = "The Spoils TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "terminator"; DisplayName = "The Terminator CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "x_files"; DisplayName = "The X-Files CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "thorgal"; DisplayName = "Thorgal Kolekcjonerska Gra Karciana"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "timestream_remnant"; DisplayName = "Timestream: The Remnant CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tomb_raider"; DisplayName = "Tomb Raider CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "top_of_order"; DisplayName = "Top of the Order CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "torchwood"; DisplayName = "Torchwood TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "towers_in_time"; DisplayName = "Towers in Time CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "transformers_eu"; DisplayName = "Transformers TCG EU"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "ultimate_combat"; DisplayName = "Ultimate Combat CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "veto_nobleman"; DisplayName = "Veto! Nobleman Card Game"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "veto_second_edition"; DisplayName = "Veto: Second Edition"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "vroom"; DisplayName = "Vroom CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wcw_nitro"; DisplayName = "WCW Nitro TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wwe_raw_deal"; DisplayName = "WWE Raw Deal"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "warcry"; DisplayName = "WarCry CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "warhammer_age_sigmar"; DisplayName = "Warhammer Age of Sigmar: Champions TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "warlords"; DisplayName = "Warlords CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wars"; DisplayName = "Wars TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "webkinz"; DisplayName = "Webkinz TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wildstorms"; DisplayName = "WildStorms CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wing_commander"; DisplayName = "Wing Commander Collectible TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "winx_club"; DisplayName = "Winx Club CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wizard_in_training"; DisplayName = "Wizard in Training TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wizards_of_mickey"; DisplayName = "Wizards of Mickey TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "wyvern"; DisplayName = "Wyvern CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "xxxenophile"; DisplayName = "XXXenophile CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "xeko"; DisplayName = "Xeko TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "xena_warrior_princess"; DisplayName = "Xena: Warrior Princess TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "xiaolin_showdown"; DisplayName = "Xiaolin Showdown TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "young_jedi"; DisplayName = "Young Jedi CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "abyss"; DisplayName = "Abyss CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "adventure_time"; DisplayName = "Adventure Time TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "age_of_empires_3"; DisplayName = "Age of Empires III TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "alien_vs_predator_ccg"; DisplayName = "Alien vs Predator CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "amazing_spider_man"; DisplayName = "The Amazing Spider-Man TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "american_gladiators"; DisplayName = "American Gladiators TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "anime_warriors"; DisplayName = "Anime Warriors TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "apocalypse_ccg"; DisplayName = "Apocalypse CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "arcana_hearts"; DisplayName = "Arcana Hearts TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "arena_of_planeswalkers"; DisplayName = "Arena of the Planeswalkers TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "army_of_darkness"; DisplayName = "Army of Darkness TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "artemis_fowl"; DisplayName = "Artemis Fowl TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "ascension"; DisplayName = "Ascension TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "assassins_creed"; DisplayName = "Assassin's Creed TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "attack_on_titan"; DisplayName = "Attack on Titan TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "avatar_legend_of_korra"; DisplayName = "Avatar: The Legend of Korra TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "battle_angels"; DisplayName = "Battle Angels TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "battle_tech_ccg"; DisplayName = "BattleTech CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "battlestar_galactica_ccg"; DisplayName = "Battlestar Galactica CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "beast_wars"; DisplayName = "Beast Wars TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "beetlejuice"; DisplayName = "Beetlejuice TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "beyblade_burst"; DisplayName = "Beyblade Burst TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "big_hero_6"; DisplayName = "Big Hero 6 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "black_clover"; DisplayName = "Black Clover TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "bleach_brave_souls"; DisplayName = "Bleach: Brave Souls TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "bloodborne"; DisplayName = "Bloodborne TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "bob_ross"; DisplayName = "Bob Ross TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "boku_no_hero_academia"; DisplayName = "Boku no Hero Academia TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "borderlands"; DisplayName = "Borderlands TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "breaking_bad"; DisplayName = "Breaking Bad TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "buffy_vampire_slayer_ccg"; DisplayName = "Buffy the Vampire Slayer CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cardfight_vanguard"; DisplayName = "Cardfight!! Vanguard TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cardcaptor_sakura"; DisplayName = "Cardcaptor Sakura TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "carmageddon"; DisplayName = "Carmageddon TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "castlevania"; DisplayName = "Castlevania TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "catan"; DisplayName = "Catan TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "catherine"; DisplayName = "Catherine TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cave_evil"; DisplayName = "Cave Evil TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "champions_of_midgard"; DisplayName = "Champions of Midgard TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "chaos_ccg"; DisplayName = "Chaos CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "charmed"; DisplayName = "Charmed TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "chrono_trigger"; DisplayName = "Chrono Trigger TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "city_of_heroes_ccg"; DisplayName = "City of Heroes CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "civilization"; DisplayName = "Civilization TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "clash_royale"; DisplayName = "Clash Royale TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "code_geass"; DisplayName = "Code Geass TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "conan_exiles"; DisplayName = "Conan Exiles TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cowboy_bebop"; DisplayName = "Cowboy Bebop TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "crash_bandicoot"; DisplayName = "Crash Bandicoot TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cryptozoic_entertainment"; DisplayName = "Cryptozoic Entertainment TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "cyberpunk_2077"; DisplayName = "Cyberpunk 2077 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dark_souls"; DisplayName = "Dark Souls TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dc_comics"; DisplayName = "DC Comics TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dead_or_alive"; DisplayName = "Dead or Alive TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "death_stranding"; DisplayName = "Death Stranding TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "demon_slayer"; DisplayName = "Demon Slayer TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "destiny_2"; DisplayName = "Destiny 2 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "devil_may_cry"; DisplayName = "Devil May Cry TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dino_riders"; DisplayName = "Dino-Riders TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dirty_harry"; DisplayName = "Dirty Harry TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "disney_frozen"; DisplayName = "Disney Frozen TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "doctor_strange"; DisplayName = "Doctor Strange TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_age"; DisplayName = "Dragon Age TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_gt_ccg"; DisplayName = "Dragon Ball GT CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_z_ccg"; DisplayName = "Dragon Ball Z CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_super_ccg"; DisplayName = "Dragon Ball Super CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_quest_ccg"; DisplayName = "Dragon Quest CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_quest_xi"; DisplayName = "Dragon Quest XI TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_quest_heroes"; DisplayName = "Dragon Quest Heroes TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_quest_monsters"; DisplayName = "Dragon Quest Monsters TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_quest_tact"; DisplayName = "Dragon Quest Tact TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_quest_walk"; DisplayName = "Dragon Quest Walk TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls"; DisplayName = "The Elder Scrolls TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends"; DisplayName = "The Elder Scrolls: Legends TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_online"; DisplayName = "The Elder Scrolls Online TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_skyrim"; DisplayName = "The Elder Scrolls V: Skyrim TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_oblivion"; DisplayName = "The Elder Scrolls IV: Oblivion TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_morrowind"; DisplayName = "The Elder Scrolls III: Morrowind TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_daggerfall"; DisplayName = "The Elder Scrolls II: Daggerfall TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_arena"; DisplayName = "The Elder Scrolls: Arena TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_battlespire"; DisplayName = "The Elder Scrolls: Battlespire TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_redguard"; DisplayName = "The Elder Scrolls Adventures: Redguard TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_travels"; DisplayName = "The Elder Scrolls Travels TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_blades"; DisplayName = "The Elder Scrolls: Blades TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_castles"; DisplayName = "The Elder Scrolls: Castles TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_heroes"; DisplayName = "The Elder Scrolls: Legends - Heroes of Skyrim TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_dark_brotherhood"; DisplayName = "The Elder Scrolls: Legends - Dark Brotherhood TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_clockwork_city"; DisplayName = "The Elder Scrolls: Legends - Clockwork City TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_houses_of_morrowind"; DisplayName = "The Elder Scrolls: Legends - Houses of Morrowind TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_isles_of_madness"; DisplayName = "The Elder Scrolls: Legends - Isles of Madness TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_alliance_war"; DisplayName = "The Elder Scrolls: Legends - Alliance War TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_moons_of_elsweyr"; DisplayName = "The Elder Scrolls: Legends - Moons of Elsweyr TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_jaws_of_oblivion"; DisplayName = "The Elder Scrolls: Legends - Jaws of Oblivion TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_gates_of_oblivion"; DisplayName = "The Elder Scrolls: Legends - Gates of Oblivion TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_high_isle"; DisplayName = "The Elder Scrolls: Legends - High Isle TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_telvanni_consortium"; DisplayName = "The Elder Scrolls: Legends - Telvanni Consortium TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_red_year"; DisplayName = "The Elder Scrolls: Legends - Red Year TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_apocrypha"; DisplayName = "The Elder Scrolls: Legends - Apocrypha TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_necrom"; DisplayName = "The Elder Scrolls: Legends - Necrom TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_whispers_of_the_void"; DisplayName = "The Elder Scrolls: Legends - Whispers of the Void TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_echoes_of_oblivion"; DisplayName = "The Elder Scrolls: Legends - Echoes of Oblivion TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "elder_scrolls_legends_heroes_of_skyrim"; DisplayName = "The Elder Scrolls: Legends - Heroes of Skyrim TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout"; DisplayName = "Fallout TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_2"; DisplayName = "Fallout 2 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_3"; DisplayName = "Fallout 3 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_new_vegas"; DisplayName = "Fallout: New Vegas TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_4"; DisplayName = "Fallout 4 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_76"; DisplayName = "Fallout 76 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_shelter"; DisplayName = "Fallout Shelter TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_tactics"; DisplayName = "Fallout Tactics TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_brotherhood_of_steel"; DisplayName = "Fallout: Brotherhood of Steel TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_online"; DisplayName = "Fallout Online TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fallout_legends"; DisplayName = "Fallout Legends TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy"; DisplayName = "Final Fantasy TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_2"; DisplayName = "Final Fantasy II TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_3"; DisplayName = "Final Fantasy III TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_4"; DisplayName = "Final Fantasy IV TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_5"; DisplayName = "Final Fantasy V TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_6"; DisplayName = "Final Fantasy VI TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_7"; DisplayName = "Final Fantasy VII TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_8"; DisplayName = "Final Fantasy VIII TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_9"; DisplayName = "Final Fantasy IX TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_10"; DisplayName = "Final Fantasy X TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_11"; DisplayName = "Final Fantasy XI TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_12"; DisplayName = "Final Fantasy XII TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_13"; DisplayName = "Final Fantasy XIII TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_14"; DisplayName = "Final Fantasy XIV TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_15"; DisplayName = "Final Fantasy XV TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_16"; DisplayName = "Final Fantasy XVI TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_tactics"; DisplayName = "Final Fantasy Tactics TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_crystal_chronicles"; DisplayName = "Final Fantasy Crystal Chronicles TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_dissidia"; DisplayName = "Final Fantasy Dissidia TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_type_0"; DisplayName = "Final Fantasy Type-0 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_world_of_final_fantasy"; DisplayName = "World of Final Fantasy TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_brave_exvius"; DisplayName = "Final Fantasy Brave Exvius TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_record_keeper"; DisplayName = "Final Fantasy Record Keeper TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "final_fantasy_operating_omega"; DisplayName = "Final Fantasy Operating Omega TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter"; DisplayName = "Street Fighter TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_2"; DisplayName = "Street Fighter II TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_3"; DisplayName = "Street Fighter III TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_4"; DisplayName = "Street Fighter IV TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_5"; DisplayName = "Street Fighter V TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_6"; DisplayName = "Street Fighter 6 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_alpha"; DisplayName = "Street Fighter Alpha TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_ex"; DisplayName = "Street Fighter EX TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_3d"; DisplayName = "Street Fighter 3D TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_online"; DisplayName = "Street Fighter Online TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "street_fighter_legends"; DisplayName = "Street Fighter Legends TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_ccg"; DisplayName = "Mortal Kombat CCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_2"; DisplayName = "Mortal Kombat 2 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_3"; DisplayName = "Mortal Kombat 3 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_4"; DisplayName = "Mortal Kombat 4 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_deadly_alliance"; DisplayName = "Mortal Kombat: Deadly Alliance TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_deception"; DisplayName = "Mortal Kombat: Deception TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_armageddon"; DisplayName = "Mortal Kombat: Armageddon TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_vs_dc_universe"; DisplayName = "Mortal Kombat vs DC Universe TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_9"; DisplayName = "Mortal Kombat 9 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_x"; DisplayName = "Mortal Kombat X TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_11"; DisplayName = "Mortal Kombat 11 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "mortal_kombat_1"; DisplayName = "Mortal Kombat 1 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tekken"; DisplayName = "Tekken TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tekken_2"; DisplayName = "Tekken 2 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tekken_3"; DisplayName = "Tekken 3 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tekken_4"; DisplayName = "Tekken 4 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tekken_5"; DisplayName = "Tekken 5 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tekken_6"; DisplayName = "Tekken 6 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tekken_7"; DisplayName = "Tekken 7 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tekken_8"; DisplayName = "Tekken 8 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "soul_calibur"; DisplayName = "Soul Calibur TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "soul_calibur_2"; DisplayName = "Soul Calibur II TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "soul_calibur_3"; DisplayName = "Soul Calibur III TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "soul_calibur_4"; DisplayName = "Soul Calibur IV TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "soul_calibur_5"; DisplayName = "Soul Calibur V TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "soul_calibur_6"; DisplayName = "Soul Calibur VI TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters"; DisplayName = "King of Fighters TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_94"; DisplayName = "King of Fighters '94 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_95"; DisplayName = "King of Fighters '95 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_96"; DisplayName = "King of Fighters '96 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_97"; DisplayName = "King of Fighters '97 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_98"; DisplayName = "King of Fighters '98 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_99"; DisplayName = "King of Fighters '99 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_2000"; DisplayName = "King of Fighters 2000 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_2001"; DisplayName = "King of Fighters 2001 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_2002"; DisplayName = "King of Fighters 2002 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_2003"; DisplayName = "King of Fighters 2003 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_xi"; DisplayName = "King of Fighters XI TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_xii"; DisplayName = "King of Fighters XII TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_xiii"; DisplayName = "King of Fighters XIII TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_xiv"; DisplayName = "King of Fighters XIV TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "king_of_fighters_xv"; DisplayName = "King of Fighters XV TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "guilty_gear"; DisplayName = "Guilty Gear TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "guilty_gear_x"; DisplayName = "Guilty Gear X TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "guilty_gear_xx"; DisplayName = "Guilty Gear XX TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "guilty_gear_xrd"; DisplayName = "Guilty Gear Xrd TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "guilty_gear_strive"; DisplayName = "Guilty Gear Strive TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "blazblue"; DisplayName = "BlazBlue TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "blazblue_calamity_trigger"; DisplayName = "BlazBlue: Calamity Trigger TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "blazblue_continuum_shift"; DisplayName = "BlazBlue: Continuum Shift TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "blazblue_chrono_phantasma"; DisplayName = "BlazBlue: Chrono Phantasma TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "blazblue_central_fiction"; DisplayName = "BlazBlue: Central Fiction TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "melty_blood"; DisplayName = "Melty Blood TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "melty_blood_actress_again"; DisplayName = "Melty Blood: Actress Again TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "melty_blood_type_lumina"; DisplayName = "Melty Blood: Type Lumina TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "under_night_in_birth"; DisplayName = "Under Night In-Birth TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "under_night_in_birth_exe_late"; DisplayName = "Under Night In-Birth Exe:Late TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "under_night_in_birth_exe_late_st"; DisplayName = "Under Night In-Birth Exe:Late[st] TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "under_night_in_birth_exe_late_clr"; DisplayName = "Under Night In-Birth Exe:Late[cl-r] TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_fighterz"; DisplayName = "Dragon Ball FighterZ TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_fighterz_2"; DisplayName = "Dragon Ball FighterZ 2 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "jump_force"; DisplayName = "Jump Force TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "jump_force_2"; DisplayName = "Jump Force 2 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_xenoverse"; DisplayName = "Dragon Ball Xenoverse TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_xenoverse_2"; DisplayName = "Dragon Ball Xenoverse 2 TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_kakarot"; DisplayName = "Dragon Ball Z: Kakarot TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_breakers"; DisplayName = "Dragon Ball: The Breakers TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_legends"; DisplayName = "Dragon Ball Legends TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_heroes"; DisplayName = "Dragon Ball Heroes TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_fusions"; DisplayName = "Dragon Ball Fusions TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_tenkaichi"; DisplayName = "Dragon Ball Z: Tenkaichi TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "my_hero_academia"; DisplayName = "My Hero Academia TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "attack_on_titan"; DisplayName = "Attack on Titan TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "demon_slayer"; DisplayName = "Demon Slayer TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "jujutsu_kaisen"; DisplayName = "Jujutsu Kaisen TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "one_punch_man"; DisplayName = "One Punch Man TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "tokyo_ghoul"; DisplayName = "Tokyo Ghoul TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "death_note_tcg"; DisplayName = "Death Note TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "bleach_tcg"; DisplayName = "Bleach TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "fairy_tail"; DisplayName = "Fairy Tail TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "hunter_x_hunter"; DisplayName = "Hunter x Hunter TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_gt_tcg"; DisplayName = "Dragon Ball GT TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_super_tcg"; DisplayName = "Dragon Ball Super TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_z_tcg"; DisplayName = "Dragon Ball Z TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_tcg"; DisplayName = "Dragon Ball TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_evolution"; DisplayName = "Dragon Ball Evolution TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_kai"; DisplayName = "Dragon Ball Kai TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_heroes_tcg"; DisplayName = "Dragon Ball Heroes TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_legends_tcg"; DisplayName = "Dragon Ball Legends TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_fighterz_tcg"; DisplayName = "Dragon Ball FighterZ TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_xenoverse_tcg"; DisplayName = "Dragon Ball Xenoverse TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_kakarot_tcg"; DisplayName = "Dragon Ball Z: Kakarot TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_breakers_tcg"; DisplayName = "Dragon Ball: The Breakers TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_fusions_tcg"; DisplayName = "Dragon Ball Fusions TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true },
        @{ Name = "dragon_ball_tenkaichi_tcg"; DisplayName = "Dragon Ball Z: Tenkaichi TCG"; Category = "Card Game"; CardSize = "standard"; HasCLI = $true; HasAPI = $true }
    )
    
    foreach ($plugin in $pluginList) {
        $plugins += $plugin
    }
    
    return $plugins
}

# Get enabled plugins
function Get-EnabledPlugins {
    $config = Load-PluginConfig
    $allPlugins = Get-AllPlugins
    
    # Always return only explicitly enabled plugins
    $enabledPlugins = @()
    foreach ($plugin in $allPlugins) {
        if ($config.enabledPlugins -contains $plugin.Name) {
            $enabledPlugins += $plugin
        }
    }
    
    return $enabledPlugins
}

# Export plugin list for GUI
function Export-PluginListForGUI {
    $enabledPlugins = Get-EnabledPlugins
    $pluginNames = @('-- Select a Game Plugin --')
    
    # Get all plugin names and sort them
    $sortedPluginNames = $enabledPlugins | ForEach-Object { $_.DisplayName } | Sort-Object
    
    # Add sorted names to the array
    foreach ($name in $sortedPluginNames) {
        $pluginNames += $name
    }
    
    return $pluginNames
}

# Initialize plugin system
function Initialize-PluginSystem {
    $config = Load-PluginConfig
    $config.lastScan = Get-Date
    Save-PluginConfig -config $config
    
    Write-Host "Simple plugin system initialized. Found $(Get-AllPlugins).Count plugins."
}

# Enable a plugin
function Enable-Plugin {
    param([string]$pluginName)
    
    $config = Load-PluginConfig
    if ($config.enabledPlugins -notcontains $pluginName) {
        $config.enabledPlugins += $pluginName
        $saveResult = Save-PluginConfig -config $config
        return $saveResult
    }
    return $false
}

# Disable a plugin
function Disable-Plugin {
    param([string]$pluginName)
    
    $config = Load-PluginConfig
    if ($config.enabledPlugins -contains $pluginName) {
        $config.enabledPlugins = $config.enabledPlugins | Where-Object { $_ -ne $pluginName }
        $saveResult = Save-PluginConfig -config $config
        return $saveResult
    }
    return $false
}

# Toggle plugin enabled state
function Toggle-Plugin {
    param([string]$pluginName)
    
    $config = Load-PluginConfig
    if ($config.enabledPlugins -contains $pluginName) {
        return Disable-Plugin -pluginName $pluginName
    } else {
        return Enable-Plugin -pluginName $pluginName
    }
}

Write-Host "Simple Plugin Manager loaded successfully!"

