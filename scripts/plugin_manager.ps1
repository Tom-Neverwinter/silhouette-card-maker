# Plugin Management System for Silhouette Card Maker
# ===================================================
# This module handles plugin discovery, loading, and management

# Plugin configuration file path
$script:pluginConfigFile = Join-Path $env:APPDATA "SilhouetteCardMaker\plugin_config.json"

# Default plugin configuration
$script:defaultPluginConfig = @{
    enabledPlugins = @()
    pluginSettings = @{}
    lastScan       = $null
    autoDetect     = $true
}

# Import plugin configuration
function Import-PluginConfig {
    if (Test-Path $script:pluginConfigFile) {
        try {
            $config = Get-Content $script:pluginConfigFile -Raw | ConvertFrom-Json
            
            # Ensure pluginSettings is a hashtable for compatibility
            if ($config.pluginSettings -is [PSCustomObject]) {
                $hash = @{}
                foreach ($prop in $config.pluginSettings.PSObject.Properties) {
                    $hash[$prop.Name] = $prop.Value
                }
                $config.pluginSettings = $hash
            }
            
            # Ensure enabledPlugins is an array
            if ($null -eq $config.enabledPlugins) {
                $config.enabledPlugins = @()
            }
            elseif ($config.enabledPlugins -is [string]) {
                $config.enabledPlugins = @($config.enabledPlugins)
            }
            
            return $config
        }
        catch {
            Write-Warning "Failed to load plugin config: $($_.Exception.Message)"
        }
    }
    
    # Return a copy of the default config
    $config = New-Object PSObject -Property @{
        enabledPlugins = @()
        pluginSettings = @{}
        lastScan       = $null
        autoDetect     = $true
    }
    return $config
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

# Enhanced plugin detection with metadata
function Get-PluginMetadata {
    param([string]$pluginPath)
    
    $metadata = @{
        Name             = ""
        DisplayName      = ""
        Description      = ""
        Version          = "1.0.0"
        Author           = "Unknown"
        Abbreviation     = ""
        Category         = "Card Game"
        Dependencies     = @()
        Features         = @()
        CardSize         = "standard"
        SupportedFormats = @()
        HasGUI           = $false
        HasCLI           = $false
        HasAPI           = $false
        HasScraper       = $false
        IsEnabled        = $true
        LastUpdated      = (Get-Date)
        Priority         = 100
    }
    
    # Get plugin name from directory
    $pluginName = Split-Path $pluginPath -Leaf
    $metadata.Name = $pluginName
    
    # Try to read README.md for metadata
    $readmePath = Join-Path $pluginPath "README.md"
    if (Test-Path $readmePath) {
        try {
            $readmeContent = Get-Content $readmePath -Raw
            
            # Extract title (first # line)
            $titleMatch = [regex]::Match($readmeContent, '(?m)^#\s*(.+)$')
            if ($titleMatch.Success) {
                $metadata.DisplayName = $titleMatch.Groups[1].Value.Trim()
            }
            
            # Extract description (first paragraph after title)
            $descMatch = [regex]::Match($readmeContent, '(?m)^#\s*.+?\n\n(.+?)(?:\n\n|\n#)', [System.Text.RegularExpressions.RegexOptions]::Singleline)
            if ($descMatch.Success) {
                $metadata.Description = $descMatch.Groups[1].Value.Trim()
            }
            
            # Extract version
            $versionMatch = [regex]::Match($readmeContent, '(?i)version[:\s]+([0-9.]+)')
            if ($versionMatch.Success) {
                $metadata.Version = $versionMatch.Groups[1].Value.Trim()
            }
            
            # Extract author
            $authorMatch = [regex]::Match($readmeContent, '(?i)author[:\s]+(.+)')
            if ($authorMatch.Success) {
                $metadata.Author = $authorMatch.Groups[1].Value.Trim()
            }
        }
        catch {
            Write-Warning "Failed to parse README for $pluginName`: $($_.Exception.Message)"
        }
    }
    
    # Fallback to directory name if no display name found
    if (-not $metadata.DisplayName) {
        $metadata.DisplayName = [System.Globalization.CultureInfo]::CurrentCulture.TextInfo.ToTitleCase($metadata.DisplayName.ToLower())
    }
    
    # Set abbreviation and expand common ones
    switch ($pluginName.ToLower()) {
        "mtg" { 
            $metadata.DisplayName = "Magic: The Gathering"
            $metadata.Abbreviation = "MTG"
        }
        "pokemon" { $metadata.Abbreviation = "PKM" }
        "yugioh" { $metadata.Abbreviation = "YGO" }
        "ccgtrader" { $metadata.Abbreviation = "CCGT" }
    }
    
    # Check for plugin files
    $files = Get-ChildItem -Path $pluginPath -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $fileName = $file.Name.ToLower()
        if ($fileName -like "*_gui*" -or $fileName -like "*gui_integration*") { $metadata.HasGUI = $true }
        if ($fileName -like "*_cli*") { $metadata.HasCLI = $true }
        if ($fileName -like "*_api*") { $metadata.HasAPI = $true }
        if ($fileName -like "*_scraper*") { $metadata.HasScraper = $true }
    }
    
    # Determine card size based on plugin name
    switch -Wildcard ($pluginName.ToLower()) {
        "*yugioh*" { $metadata.CardSize = "japanese" }
        "*weiss*" { $metadata.CardSize = "japanese" }
        "*pokemon*" { $metadata.CardSize = "standard" }
        "*magic*" { $metadata.CardSize = "standard" }
        "*mtg*" { $metadata.CardSize = "standard" }
        default { $metadata.CardSize = "standard" }
    }
    
    # Set priority based on popularity/importance
    switch ($pluginName.ToLower()) {
        "mtg" { $metadata.Priority = 1 }
        "magic" { $metadata.Priority = 1 }
        "yugioh" { $metadata.Priority = 2 }
        "pokemon" { $metadata.Priority = 3 }
        "weiss_schwarz" { $metadata.Priority = 4 }
        "weiss" { $metadata.Priority = 4 }
        "ccgtrader" { $metadata.Priority = 5 }
        default { $metadata.Priority = 50 }
    }
    
    return $metadata
}

# Discover all available plugins and games
function Get-AllPlugins {
    param(
        [string]$pluginsPath,
        [bool]$includeGames = $true
    )
    
    # If no path provided, calculate it relative to this script
    if ([string]::IsNullOrEmpty($pluginsPath)) {
        # Assumes script is in /scripts/ and plugins are in /plugins/
        $pluginsPath = Join-Path (Split-Path -Parent $PSScriptRoot) "plugins"
    }
    
    $plugins = @()
    
    # 1. First, get physical plugins (scrapers)
    if (Test-Path $pluginsPath) {
        $pluginDirectories = Get-ChildItem -Path $pluginsPath -Directory -ErrorAction SilentlyContinue
        
        foreach ($pluginDir in $pluginDirectories) {
            # Skip hidden directories
            if ($pluginDir.Name.StartsWith('.')) { continue }
            
            # Check if it's a valid plugin directory
            $hasValidFiles = $false
            $files = Get-ChildItem -Path $pluginDir.FullName -File -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                $fileName = $file.Name.ToLower()
                if ($fileName -like "*_cli*" -or $fileName -like "*_api*" -or $fileName -like "*_scraper*" -or $fileName -like "*_gui*") {
                    $hasValidFiles = $true
                    break
                }
            }
            
            if ($hasValidFiles) {
                $metadata = Get-PluginMetadata -pluginPath $pluginDir.FullName
                $plugins += $metadata
            }
        }
    }

    # 2. Then, get games from games_index.json if requested
    if ($includeGames) {
        $gamesIndexPath = Join-Path (Split-Path -Parent $PSScriptRoot) "data\games_index.json"
        if (Test-Path $gamesIndexPath) {
            try {
                $jsonContent = Get-Content $gamesIndexPath -Raw -Encoding UTF8
                $gamesIndex = $jsonContent | ConvertFrom-Json
                
                foreach ($prop in $gamesIndex.PSObject.Properties) {
                    $gameName = $prop.Name
                    if ($gameName -eq "Mtg") { $gameName = "Magic: The Gathering" }
                    
                    $gameData = $prop.Value
                    
                    # Skip if this game is already in the list as a plugin
                    if ($plugins.Name -contains $gameName -or $plugins.DisplayName -contains $gameName) { continue }
                    
                    # Create generic metadata for the game
                    $metadata = @{
                        Name             = $gameName
                        DisplayName      = $gameName
                        Description      = "Game profile using the $($gameData.plugin) scraper."
                        Version          = "N/A"
                        Author           = "Internal"
                        Abbreviation     = ""
                        Category         = "Game Profile"
                        Dependencies     = @($gameData.plugin)
                        Features         = @("Scraper")
                        CardSize         = "standard"
                        SupportedFormats = @()
                        HasGUI           = $false
                        HasCLI           = $true
                        HasAPI           = $false
                        HasScraper       = $true
                        IsEnabled        = $true
                        LastUpdated      = (Get-Date)
                        Priority         = 100
                    }

                    # Set abbreviation for game profiles
                    if ($gameName.ToLower() -match "magic|mtg") { $metadata.Abbreviation = "MTG" }
                    if ($gameName.ToLower() -match "pokemon") { $metadata.Abbreviation = "PKM" }
                    if ($gameName.ToLower() -match "yugioh") { $metadata.Abbreviation = "YGO" }
                    if ($gameName.ToLower() -match "one piece") { $metadata.Abbreviation = "OP" }
                    if ($gameName.ToLower() -match "lorcana") { $metadata.Abbreviation = "LOR" }
                    if ($gameName.ToLower() -match "flesh and blood") { $metadata.Abbreviation = "FAB" }
                    
                    # Set card size based on name if possible
                    switch -Wildcard ($gameName.ToLower()) {
                        "*yugioh*" { $metadata.CardSize = "japanese" }
                        "*weiss*" { $metadata.CardSize = "japanese" }
                        default { $metadata.CardSize = "standard" }
                    }
                    
                    $plugins += New-Object PSObject -Property $metadata
                }
            }
            catch {
                Write-Warning "Failed to load games for plugin list: $($_.Exception.Message)"
            }
        }
    }
    
    # Sort by priority, then by name
    return $plugins | Sort-Object Priority, DisplayName
}

# Get enabled plugins
function Get-EnabledPlugins {
    $config = Import-PluginConfig
    $allPlugins = Get-AllPlugins
    
    if ($config.enabledPlugins.Count -eq 0) {
        # If no plugins are explicitly enabled, enable all by default
        return $allPlugins
    }
    
    $enabledPlugins = @()
    foreach ($plugin in $allPlugins) {
        if ($config.enabledPlugins -contains $plugin.Name) {
            $enabledPlugins += $plugin
        }
    }
    
    return $enabledPlugins
}

# Enable a plugin
function Enable-Plugin {
    param([string]$pluginName)
    
    $config = Import-PluginConfig
    if ($config.enabledPlugins -notcontains $pluginName) {
        $config.enabledPlugins += $pluginName
        Save-PluginConfig -config $config
        return $true
    }
    return $false
}

# Disable a plugin
function Disable-Plugin {
    param([string]$pluginName)
    
    $config = Import-PluginConfig
    if ($config.enabledPlugins -contains $pluginName) {
        $config.enabledPlugins = $config.enabledPlugins | Where-Object { $_ -ne $pluginName }
        Save-PluginConfig -config $config
        return $true
    }
    return $false
}

# Toggle plugin enabled state
function Update-PluginState {
    param([string]$pluginName)
    
    $config = Import-PluginConfig
    if ($config.enabledPlugins -contains $pluginName) {
        return Disable-Plugin -pluginName $pluginName
    }
    else {
        return Enable-Plugin -pluginName $pluginName
    }
}

# Get plugin settings
function Get-PluginSettings {
    param([string]$pluginName)
    
    $config = Import-PluginConfig
    if ($config.pluginSettings.ContainsKey($pluginName)) {
        return $config.pluginSettings[$pluginName]
    }
    return @{}
}

# Set plugin settings
function Set-PluginSettings {
    param(
        [string]$pluginName,
        [hashtable]$settings
    )
    
    $config = Import-PluginConfig
    
    # Handle both Hashtable and PSCustomObject
    if ($config.pluginSettings -is [hashtable]) {
        $config.pluginSettings[$pluginName] = $settings
    }
    else {
        # Fallback for PSCustomObject
        $config.pluginSettings | Add-Member -MemberType NoteProperty -Name $pluginName -Value $settings -Force
    }
    
    Save-PluginConfig -config $config
}

# Validate plugin dependencies
function Test-PluginDependencies {
    param([hashtable]$plugin)
    
    $missingDeps = @()
    
    foreach ($dep in $plugin.Dependencies) {
        # Check if dependency is available
        $depPlugin = Get-AllPlugins | Where-Object { $_.Name -eq $dep }
        if (-not $depPlugin) {
            $missingDeps += $dep
        }
    }
    
    return $missingDeps
}

# Get plugin statistics
function Get-PluginStats {
    $allPlugins = Get-AllPlugins
    $enabledPlugins = Get-EnabledPlugins
    $config = Import-PluginConfig
    
    return @{
        TotalPlugins    = $allPlugins.Count
        EnabledPlugins  = $enabledPlugins.Count
        DisabledPlugins = $allPlugins.Count - $enabledPlugins.Count
        Categories      = ($allPlugins | Group-Object Category | Select-Object Name, Count)
        LastScan        = $config.lastScan
        AutoDetect      = $config.autoDetect
    }
}

# Export plugin list for GUI
function Export-PluginListForGUI {
    $gamesIndexPath = Join-Path (Split-Path -Parent $PSScriptRoot) "data\games_index.json"
    $config = Import-PluginConfig
    $hasExplicitConfigs = $config.enabledPlugins.Count -gt 0
    
    if (Test-Path $gamesIndexPath) {
        try {
            $jsonContent = Get-Content $gamesIndexPath -Raw -Encoding UTF8
            $gamesIndex = $jsonContent | ConvertFrom-Json
            
            # Get all game names (keys of the PSCustomObject)
            $gameNames = $gamesIndex.PSObject.Properties.Name | Sort-Object
            
            $pluginNames = @('-- Select a Game Plugin --')
            
            foreach ($name in $gameNames) {
                # If we have explicit configs, only include enabled ones
                # Otherwise include all by default
                if (-not $hasExplicitConfigs -or ($config.enabledPlugins -contains $name)) {
                    # Also check if the underlying scraper plugin is enabled?
                    # For now, let's keep it simple: individual game enablement
                    $pluginNames += $name
                }
            }
            
            return $pluginNames
        }
        catch {
            Write-Warning "Failed to read games index: $($_.Exception.Message)"
        }
    }

    # Fallback to old method if index doesn't exist
    $enabledPlugins = Get-EnabledPlugins
    $pluginNames = @('-- Select a Game Plugin --')
    
    foreach ($plugin in $enabledPlugins) {
        $pluginNames += $plugin.DisplayName
    }
    
    return $pluginNames
}

# Initialize plugin system
function Initialize-PluginSystem {
    $config = Import-PluginConfig
    $config.lastScan = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Save-PluginConfig -config $config | Out-Null
    
    $plugins = Get-AllPlugins
    Write-Host "Plugin system initialized. Found $($plugins.Count) plugins."
}

# Get the CLI script path for a plugin
function Get-PluginCLIScript {
    param(
        [string]$pluginName,
        [string]$installRoot
    )
    
    # 1. Try to resolve from games_index.json
    $gamesIndexPath = Join-Path $installRoot "data\games_index.json"
    $pluginFolder = $pluginName # Default fallback
    
    if (Test-Path $gamesIndexPath) {
        try {
            $jsonContent = Get-Content $gamesIndexPath -Raw -Encoding UTF8
            $gamesIndex = $jsonContent | ConvertFrom-Json
            if ($gamesIndex.PSObject.Properties.Name -contains $pluginName) {
                $pluginFolder = $gamesIndex.$pluginName.plugin
            }
        }
        catch {
            Write-Warning "Could not resolve plugin for game '$pluginName' from index"
        }
    }
    
    # 2. Check for standard CLI script naming: [plugin_folder]_cli.py
    $cliScript = Join-Path $installRoot "plugins\$pluginFolder\$($pluginFolder)_cli.py"
    if (Test-Path $cliScript) {
        return $cliScript
    }
    
    # 3. Check for legacy fetch.py
    $legacyFetch = Join-Path $installRoot "plugins\$pluginFolder\fetch.py"
    if (Test-Path $legacyFetch) {
        return $legacyFetch
    }
    
    # 4. Special case for CCGTrader
    if ($pluginFolder -eq "ccgtrader") {
        $ccgtCli = Join-Path $installRoot "plugins\ccgtrader\ccgt_cli.py"
        if (Test-Path $ccgtCli) { return $ccgtCli }
    }
    
    # 5. Fallback to CCGTrader for any other game if it's in the registry
    # (This assumes CCGTrader is the universal scraper)
    $ccgtCli = Join-Path $installRoot "plugins\ccgtrader\ccgt_cli.py"
    if (Test-Path $ccgtCli) {
        return $ccgtCli
    }
    
    return $null
}

# Functions are available for direct use when script is dot-sourced
