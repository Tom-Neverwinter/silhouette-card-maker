# Plugin Management System for Silhouette Card Maker
# ===================================================
# This module handles plugin discovery, loading, and management

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

# Enhanced plugin detection with metadata
function Get-PluginMetadata {
    param([string]$pluginPath)
    
    $metadata = @{
        Name = ""
        DisplayName = ""
        Description = ""
        Version = "1.0.0"
        Author = "Unknown"
        Category = "Card Game"
        Dependencies = @()
        Features = @()
        CardSize = "standard"
        SupportedFormats = @()
        HasGUI = $false
        HasCLI = $false
        HasAPI = $false
        HasScraper = $false
        IsEnabled = $true
        LastUpdated = (Get-Date)
        Priority = 100
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
        $metadata.DisplayName = $pluginName -replace '_', ' ' -replace '-', ' '
        $metadata.DisplayName = [System.Globalization.CultureInfo]::CurrentCulture.TextInfo.ToTitleCase($metadata.DisplayName.ToLower())
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
        default { $metadata.Priority = 50 }
    }
    
    return $metadata
}

# Discover all available plugins
function Get-AllPlugins {
    param([string]$pluginsPath = "plugins")
    
    $plugins = @()
    
    if (-not (Test-Path $pluginsPath)) {
        Write-Warning "Plugins directory not found: $pluginsPath"
        return $plugins
    }
    
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
    
    # Sort by priority, then by name
    return $plugins | Sort-Object Priority, DisplayName
}

# Get enabled plugins
function Get-EnabledPlugins {
    $config = Load-PluginConfig
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
    
    $config = Load-PluginConfig
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
    
    $config = Load-PluginConfig
    if ($config.enabledPlugins -contains $pluginName) {
        $config.enabledPlugins = $config.enabledPlugins | Where-Object { $_ -ne $pluginName }
        Save-PluginConfig -config $config
        return $true
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

# Get plugin settings
function Get-PluginSettings {
    param([string]$pluginName)
    
    $config = Load-PluginConfig
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
    
    $config = Load-PluginConfig
    $config.pluginSettings[$pluginName] = $settings
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
    $config = Load-PluginConfig
    
    return @{
        TotalPlugins = $allPlugins.Count
        EnabledPlugins = $enabledPlugins.Count
        DisabledPlugins = $allPlugins.Count - $enabledPlugins.Count
        Categories = ($allPlugins | Group-Object Category | Select-Object Name, Count)
        LastScan = $config.lastScan
        AutoDetect = $config.autoDetect
    }
}

# Export plugin list for GUI
function Export-PluginListForGUI {
    $enabledPlugins = Get-EnabledPlugins
    $pluginNames = @('-- Select a Game Plugin --')
    
    foreach ($plugin in $enabledPlugins) {
        $pluginNames += $plugin.DisplayName
    }
    
    return $pluginNames
}

# Initialize plugin system
function Initialize-PluginSystem {
    $config = Load-PluginConfig
    $config.lastScan = Get-Date
    Save-PluginConfig -config $config
    
    Write-Host "Plugin system initialized. Found $(Get-AllPlugins).Count plugins."
}

# Functions are available for direct use when script is dot-sourced
