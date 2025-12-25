Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Import plugin management system
. "$PSScriptRoot\plugin_manager.ps1"
. "$PSScriptRoot\plugin_options_tab.ps1"

# Create the main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "Silhouette Card Maker - Plugin Manager"
$form.Size = New-Object System.Drawing.Size(750, 680)
$form.BackColor = [System.Drawing.Color]::FromArgb(45, 45, 48)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false

# Variables to store file info
$script:selectedFile = $null
$script:originalPath = ""
$script:targetFolder = ""
$script:detectedFormat = ""
$script:decklistBaseName = ""  # Store the base name for PDF renaming
$script:defaultDecklistFolders = @{}  # Hash table to store per-plugin default folders
$script:generalDecklistLocation = ""  # General location where all decklists are stored
$script:backImages = @{}  # Hash table to store per-plugin back images
$script:outputPath = ""  # Custom output path for PDFs
$script:pluginOptions = @{}  # Hash table to store per-plugin checkbox states
$script:xOffset = ""
$script:yOffset = ""
$script:loadOffset = $false
$script:isUpdatingOffsetUI = $false

# Settings file path
$script:settingsFile = Join-Path $env:APPDATA "SilhouetteCardMaker\settings.json"

# Function to import settings
function Import-Settings {
    if (Test-Path $script:settingsFile) {
        try {
            $settings = Get-Content $script:settingsFile -Raw | ConvertFrom-Json
            $script:defaultDecklistFolders = $settings.defaultDecklistFolders
            $script:targetFolder = $settings.targetFolder
            $script:generalDecklistLocation = $settings.generalDecklistLocation
            $script:backImages = $settings.backImages
            $script:outputPath = $settings.outputPath
            $script:xOffset = $settings.xOffset
            $script:yOffset = $settings.yOffset
            $script:loadOffset = $settings.loadOffset
            $script:pluginOptions = $settings.pluginOptions
            return $settings
        }
        catch {
            return $null
        }
    }
    return $null
}

# Function to save settings
function Save-Settings {
    param(
        [hashtable]$defaultDecklistFolders,
        [string]$targetFolder,
        [string]$generalDecklistLocation,
        [hashtable]$backImages,
        [string]$outputPath,
        [string]$xOffset,
        [string]$yOffset,
        [bool]$loadOffset,
        [hashtable]$pluginOptions
    )
    
    try {
        $settingsDir = Split-Path $script:settingsFile -Parent
        if (-not (Test-Path $settingsDir)) {
            New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
        }
        
        $settings = @{
            defaultDecklistFolders  = $defaultDecklistFolders
            targetFolder            = $targetFolder
            generalDecklistLocation = $generalDecklistLocation
            backImages              = $backImages
            outputPath              = $outputPath
            xOffset                 = $xOffset
            yOffset                 = $yOffset
            loadOffset              = $loadOffset
            pluginOptions           = $pluginOptions
        }
        
        $settings | ConvertTo-Json -Depth 3 | Set-Content $script:settingsFile -Encoding UTF8
    }
    catch {
        # Silently fail if we can't save settings
    }
}

# Function to auto-detect Silhouette Card Maker folder on Windows
function Find-SilhouetteCardMaker {
    # Key files that identify a Silhouette Card Maker installation
    $keyFiles = @("src\create_pdf.py", "venv", "plugins")
    
    # FIRST: Check the current directory where the GUI script is located
    $currentDir = Split-Path -Parent $PSCommandPath
    if ($currentDir) {
        # Check if current directory is the installation
        $validInstallation = $true
        foreach ($keyFile in $keyFiles) {
            if (-not (Test-Path (Join-Path $currentDir $keyFile))) {
                $validInstallation = $false
                break
            }
        }
        
        if ($validInstallation) {
            $pluginsPath = Join-Path $currentDir "plugins"
            if (Test-Path $pluginsPath) {
                $pluginCount = (Get-ChildItem -Path $pluginsPath -Directory -ErrorAction SilentlyContinue).Count
                if ($pluginCount -gt 0) {
                    return $currentDir
                }
            }
        }
        
        # Check parent directory (in case GUI is in a subdirectory)
        $parentDir = Split-Path -Parent $currentDir
        if ($parentDir) {
            $validInstallation = $true
            foreach ($keyFile in $keyFiles) {
                if (-not (Test-Path (Join-Path $parentDir $keyFile))) {
                    $validInstallation = $false
                    break
                }
            }
            
            if ($validInstallation) {
                $pluginsPath = Join-Path $parentDir "plugins"
                if (Test-Path $pluginsPath) {
                    $pluginCount = (Get-ChildItem -Path $pluginsPath -Directory -ErrorAction SilentlyContinue).Count
                    if ($pluginCount -gt 0) {
                        return $parentDir
                    }
                }
            }
        }
    }
    
    # SECOND: Get all available drives and search them
    $drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 } | Select-Object -ExpandProperty Root

    # Search each drive for Silhouette Card Maker installations
    foreach ($drive in $drives) {
        if ($drive -notmatch "^[A-Z]:\\?$") { continue }

        try {
            # Look for create_pdf.py files (most unique identifier) - deeper search
            $createPdfFiles = Get-ChildItem -Path $drive -Filter "create_pdf.py" -Recurse -ErrorAction SilentlyContinue -Depth 6

            foreach ($pdfFile in $createPdfFiles) {
                $foundDir = Split-Path $pdfFile.FullName -Parent
                # If found in src, check parent dir
                if ((Split-Path $foundDir -Leaf) -eq "src") {
                    $installPath = Split-Path $foundDir -Parent
                }
                else {
                    $installPath = $foundDir
                }

                # Verify this is a valid installation by checking for other key files
                $validInstallation = $true
                foreach ($keyFile in $keyFiles) {
                    if (-not (Test-Path (Join-Path $installPath $keyFile))) {
                        $validInstallation = $false
                        break
                    }
                }

                if ($validInstallation) {
                    # Additional check: make sure plugins directory has content
                    $pluginsPath = Join-Path $installPath "plugins"
                    if (Test-Path $pluginsPath) {
                        $pluginCount = (Get-ChildItem -Path $pluginsPath -Directory -ErrorAction SilentlyContinue).Count
                        if ($pluginCount -gt 0) {
                            return $installPath
                        }
                    }
                }
            }

            # Also search for directories with silhouette-related names that contain the key files - deeper search
            $candidateDirs = Get-ChildItem -Path $drive -Directory -Recurse -ErrorAction SilentlyContinue -Depth 5 |
            Where-Object { $_.Name -like "*silhouette*" -or $_.Name -like "*card*maker*" -or $_.Name -like "*mtg*" } |
            Where-Object { $_.Name -notlike "*node_modules*" -and $_.Name -notlike "*.git*" -and $_.Name -notlike "*backup*" }

            foreach ($dir in $candidateDirs) {
                $validInstallation = $true
                foreach ($keyFile in $keyFiles) {
                    if (-not (Test-Path (Join-Path $dir.FullName $keyFile))) {
                        $validInstallation = $false
                        break
                    }
                }

                if ($validInstallation) {
                    # Verify plugins directory has actual plugin folders
                    $pluginsPath = Join-Path $dir.FullName "plugins"
                    if (Test-Path $pluginsPath) {
                        $pluginFolders = Get-ChildItem -Path $pluginsPath -Directory -ErrorAction SilentlyContinue
                        if ($pluginFolders -and $pluginFolders.Count -gt 0) {
                            return $dir.FullName
                        }
                    }
                }
            }
        }
        catch {
            # Continue searching other drives if there's an error
            continue
        }
    }

    # Last resort: search in user profile areas more thoroughly
    $userPaths = @(
        $env:USERPROFILE,
        "$env:USERPROFILE\Documents",
        "$env:USERPROFILE\Desktop",
        "$env:USERPROFILE\Downloads",
        "$env:USERPROFILE\OneDrive"
    )

    foreach ($userPath in $userPaths) {
        if (Test-Path $userPath) {
            try {
                # Look for any Python virtual environments in user areas
                $venvDirs = Get-ChildItem -Path $userPath -Filter "venv" -Directory -Recurse -ErrorAction SilentlyContinue -Depth 4

                foreach ($venvDir in $venvDirs) {
                    $parentPath = Split-Path $venvDir.FullName -Parent

                    # Check if this looks like our target installation
                    $hasCreatePdf = Test-Path (Join-Path $parentPath "create_pdf.py")
                    $hasPlugins = Test-Path (Join-Path $parentPath "plugins")

                    if ($hasCreatePdf -and $hasPlugins) {
                        # Verify plugins has content
                        $pluginsPath = Join-Path $parentPath "plugins"
                        $pluginCount = (Get-ChildItem -Path $pluginsPath -Directory -ErrorAction SilentlyContinue).Count
                        if ($pluginCount -gt 0) {
                            return $parentPath
                        }
                    }
                }
            }
            catch {
                continue
            }
        }
    }

    return $null
}

# Function to get decklist format from file content
function Get-DecklistFormat {
    param([string]$filePath)

    if (-not (Test-Path $filePath)) {
        return "unknown"
    }

    try {
        # Special-case: .dek files from supported platforms use MTGO-style syntax (quantity + card name)
        # Special-case: .dek files 
        $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
        
        $content = Get-Content -Path $filePath -Raw -ErrorAction Stop
        
        if ($ext -eq ".dek" -and $content.Trim().StartsWith("<")) {
            return "dek"
        }

        # TappedOut format detection (MTG)
        # TappedOut uses MTGO-like format but may have specific markers
        # - Contains "TappedOut.net" or "tappedout.net" URL
        # - Or has MTGO format with sections like "Sideboard:" or "Maybeboard:"
        if ($content -match "TappedOut\.net" -or $content -match "tappedout\.net") {
            return "tappedout"
        }

        # MTGA format detection
        if ($content -match "Deck" -and $content -match "Sideboard" -and $content -match "\d+\s+[A-Za-z].*") {
            return "mtga"
        }

        # MTGO format detection (also used by TappedOut .txt exports)
        # Format: quantity card_name
        if ($content -match "^\d+\s+[A-Za-z].*" -and $content -notmatch "Deck|Sideboard") {
            return "mtgo"
        }

        # Moxfield format detection
        if ($content -match "Moxfield\.com" -or $content -match "moxfield\.com") {
            return "moxfield"
        }

        # Archidekt format detection
        if ($content -match "Archidekt\.com" -or $content -match "archidekt\.com") {
            return "archidekt"
        }

        # Scryfall JSON format detection
        if ($content -match '"name":' -and $content -match '"type_line":') {
            return "scryfall_json"
        }

        # Simple format detection (just card names, one per line)
        $lines = $content -split "`n" | Where-Object { $_.Trim() -ne "" }
        $cardLikeLines = 0
        foreach ($line in $lines) {
            $trimmed = $line.Trim()
            if ($trimmed -match "^[A-Za-z].*" -and $trimmed -notmatch "Sideboard|Deck|Commander|Main") {
                $cardLikeLines++
            }
        }
        if ($cardLikeLines -gt 3) {
            return "simple"
        }

        # YDK format detection (Yu-Gi-Oh!)
        if ($content -match "^\d+$" -and (Select-String -Path $filePath -Pattern "^\d+$" -Encoding UTF8).Count -gt 10) {
            return "ydk"
        }

        return "unknown"
    }
    catch {
        return "unknown"
    }
}

# Main Tab Control
$mainTabControl = New-Object System.Windows.Forms.TabControl
$mainTabControl.Location = New-Object System.Drawing.Point(10, 10)
$mainTabControl.Size = New-Object System.Drawing.Size(710, 450)
$form.Controls.Add($mainTabControl)

# ===== TAB 1: CARD FETCHING =====
$cardFetchTab = New-Object System.Windows.Forms.TabPage
$cardFetchTab.Text = "Card Fetching"
$cardFetchTab.BackColor = [System.Drawing.Color]::FromArgb(37, 37, 38)
$mainTabControl.Controls.Add($cardFetchTab)

# Silhouette Card Maker Folder
$targetLabel = New-Object System.Windows.Forms.Label
$targetLabel.Location = New-Object System.Drawing.Point(10, 8)
$targetLabel.Size = New-Object System.Drawing.Size(530, 18)
$targetLabel.Text = "Silhouette Card Maker Folder:"
$targetLabel.ForeColor = [System.Drawing.Color]::White
$cardFetchTab.Controls.Add($targetLabel)

$targetTextBox = New-Object System.Windows.Forms.TextBox
$targetTextBox.Location = New-Object System.Drawing.Point(10, 28)
$targetTextBox.Size = New-Object System.Drawing.Size(430, 22)
$targetTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$targetTextBox.ForeColor = [System.Drawing.Color]::White
$targetTextBox.BorderStyle = 'FixedSingle'
$cardFetchTab.Controls.Add($targetTextBox)

$autoDetectButton = New-Object System.Windows.Forms.Button
$autoDetectButton.Location = New-Object System.Drawing.Point(450, 27)
$autoDetectButton.Size = New-Object System.Drawing.Size(100, 23)
$autoDetectButton.Text = "Auto-Detect"
$autoDetectButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$autoDetectButton.ForeColor = [System.Drawing.Color]::White
$autoDetectButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($autoDetectButton)

$targetButton = New-Object System.Windows.Forms.Button
$targetButton.Location = New-Object System.Drawing.Point(560, 27)
$targetButton.Size = New-Object System.Drawing.Size(130, 23)
$targetButton.Text = "Browse..."
$targetButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$targetButton.ForeColor = [System.Drawing.Color]::White
$targetButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($targetButton)

# General Decklist Location Section
$generalLocationLabel = New-Object System.Windows.Forms.Label
$generalLocationLabel.Location = New-Object System.Drawing.Point(10, 56)
$generalLocationLabel.Size = New-Object System.Drawing.Size(530, 18)
$generalLocationLabel.Text = "General Decklists Location (optional):"
$generalLocationLabel.ForeColor = [System.Drawing.Color]::White
$cardFetchTab.Controls.Add($generalLocationLabel)

$generalLocationTextBox = New-Object System.Windows.Forms.TextBox
$generalLocationTextBox.Location = New-Object System.Drawing.Point(10, 76)
$generalLocationTextBox.Size = New-Object System.Drawing.Size(430, 25)
$generalLocationTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$generalLocationTextBox.ForeColor = [System.Drawing.Color]::White
$generalLocationTextBox.BorderStyle = 'FixedSingle'
$generalLocationTextBox.ReadOnly = $true
$cardFetchTab.Controls.Add($generalLocationTextBox)

$generalLocationButton = New-Object System.Windows.Forms.Button
$generalLocationButton.Location = New-Object System.Drawing.Point(450, 75)
$generalLocationButton.Size = New-Object System.Drawing.Size(100, 23)
$generalLocationButton.Text = "Browse..."
$generalLocationButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$generalLocationButton.ForeColor = [System.Drawing.Color]::White
$generalLocationButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($generalLocationButton)

$clearGeneralButton = New-Object System.Windows.Forms.Button
$clearGeneralButton.Location = New-Object System.Drawing.Point(560, 75)
$clearGeneralButton.Size = New-Object System.Drawing.Size(130, 23)
$clearGeneralButton.Text = "Clear"
$clearGeneralButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$clearGeneralButton.ForeColor = [System.Drawing.Color]::White
$clearGeneralButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($clearGeneralButton)

# Plugin Selection
$pluginLabel = New-Object System.Windows.Forms.Label
$pluginLabel.Location = New-Object System.Drawing.Point(10, 104)
$pluginLabel.Size = New-Object System.Drawing.Size(120, 18)
$pluginLabel.Text = "Select Game Plugin:"
$pluginLabel.ForeColor = [System.Drawing.Color]::White
$cardFetchTab.Controls.Add($pluginLabel)

$pluginCombo = New-Object System.Windows.Forms.ComboBox
$pluginCombo.Location = New-Object System.Drawing.Point(140, 102)
$pluginCombo.Size = New-Object System.Drawing.Size(200, 25)
$pluginCombo.DropDownStyle = 'DropDownList'
$pluginCombo.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$pluginCombo.ForeColor = [System.Drawing.Color]::White
$pluginCombo.FlatStyle = 'Flat'
# Initialize plugin system and populate plugin combo
try {
    Initialize-PluginSystem
    $enabledPluginNames = Export-PluginListForGUI
    if ($enabledPluginNames -and $enabledPluginNames.Count -gt 1) {
        $pluginCombo.Items.AddRange($enabledPluginNames)
    }
    else {
        # Fallback to scanning plugins directory if index system fails
        $allPlugins = Get-AllPlugins
        if ($allPlugins.Count -gt 0) {
            $pluginCombo.Items.Add('-- Select a Game Plugin --')
            foreach ($p in $allPlugins) {
                $pluginCombo.Items.Add($p.DisplayName)
            }
        }
        else {
            # Absolute fallback
            $fallbackPlugins = @('-- Select a Game Plugin --', 'Magic: The Gathering', 'Yu-Gi-Oh!', 'Pokemon', 'CCGTrader')
            $pluginCombo.Items.AddRange($fallbackPlugins)
        }
    }
}
catch {
    Write-Warning "Failed to initialize plugin system: $($_.Exception.Message)"
    # Fallback to hardcoded list
    $fallbackPlugins = @('-- Select a Game Plugin --', 'Magic: The Gathering', 'Yu-Gi-Oh!', 'Altered', 'Cards Against Humanity', 'CCGTrader', 'CF Vanguard', 'Digimon', 'Dragon Ball Super', 'Flesh and Blood', 'Fluxx', 'Force of Will', 'Grand Archive', 'Gundam', 'Lorcana', 'Marvel Champions', 'MetaZoo', 'Munchkin', 'Netrunner', 'One Piece', 'Pokemon', 'Riftbound', 'Shadowverse Evolve', 'Star Realms', 'Star Wars Unlimited', 'Union Arena', 'Universus', 'Weiss Schwarz')
    $pluginCombo.Items.AddRange($fallbackPlugins)
}
$pluginCombo.SelectedIndex = 0
$cardFetchTab.Controls.Add($pluginCombo)

# Default Decklist Folder Section (per-game)
$defaultFolderLabel = New-Object System.Windows.Forms.Label
$defaultFolderLabel.Location = New-Object System.Drawing.Point(10, 132)
$defaultFolderLabel.Size = New-Object System.Drawing.Size(530, 18)
$defaultFolderLabel.Text = "Game-Specific Folder (optional):"
$defaultFolderLabel.ForeColor = [System.Drawing.Color]::White
$cardFetchTab.Controls.Add($defaultFolderLabel)

$defaultFolderTextBox = New-Object System.Windows.Forms.TextBox
$defaultFolderTextBox.Location = New-Object System.Drawing.Point(10, 152)
$defaultFolderTextBox.Size = New-Object System.Drawing.Size(430, 25)
$defaultFolderTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$defaultFolderTextBox.ForeColor = [System.Drawing.Color]::White
$defaultFolderTextBox.BorderStyle = 'FixedSingle'
$defaultFolderTextBox.ReadOnly = $true
$cardFetchTab.Controls.Add($defaultFolderTextBox)

$defaultFolderButton = New-Object System.Windows.Forms.Button
$defaultFolderButton.Location = New-Object System.Drawing.Point(450, 151)
$defaultFolderButton.Size = New-Object System.Drawing.Size(100, 23)
$defaultFolderButton.Text = "Browse..."
$defaultFolderButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$defaultFolderButton.ForeColor = [System.Drawing.Color]::White
$defaultFolderButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($defaultFolderButton)

$clearDefaultButton = New-Object System.Windows.Forms.Button
$clearDefaultButton.Location = New-Object System.Drawing.Point(560, 151)
$clearDefaultButton.Size = New-Object System.Drawing.Size(130, 23)
$clearDefaultButton.Text = "Clear"
$clearDefaultButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$clearDefaultButton.ForeColor = [System.Drawing.Color]::White
$clearDefaultButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($clearDefaultButton)

# Back Image Selection (per-game)
$backImageLabel = New-Object System.Windows.Forms.Label
$backImageLabel.Location = New-Object System.Drawing.Point(10, 180)
$backImageLabel.Size = New-Object System.Drawing.Size(530, 18)
$backImageLabel.Text = "Card Back Image (optional):"
$backImageLabel.ForeColor = [System.Drawing.Color]::White
$cardFetchTab.Controls.Add($backImageLabel)

$backImageTextBox = New-Object System.Windows.Forms.TextBox
$backImageTextBox.Location = New-Object System.Drawing.Point(10, 200)
$backImageTextBox.Size = New-Object System.Drawing.Size(430, 25)
$backImageTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$backImageTextBox.ForeColor = [System.Drawing.Color]::White
$backImageTextBox.BorderStyle = 'FixedSingle'
$backImageTextBox.ReadOnly = $true
$cardFetchTab.Controls.Add($backImageTextBox)

$backImageButton = New-Object System.Windows.Forms.Button
$backImageButton.Location = New-Object System.Drawing.Point(450, 199)
$backImageButton.Size = New-Object System.Drawing.Size(100, 23)
$backImageButton.Text = "Browse..."
$backImageButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$backImageButton.ForeColor = [System.Drawing.Color]::White
$backImageButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($backImageButton)

$clearBackImageButton = New-Object System.Windows.Forms.Button
$clearBackImageButton.Location = New-Object System.Drawing.Point(560, 199)
$clearBackImageButton.Size = New-Object System.Drawing.Size(130, 23)
$clearBackImageButton.Text = "Clear"
$clearBackImageButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$clearBackImageButton.ForeColor = [System.Drawing.Color]::White
$clearBackImageButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($clearBackImageButton)

# File Selection
$fileLabel = New-Object System.Windows.Forms.Label
$fileLabel.Location = New-Object System.Drawing.Point(10, 228)
$fileLabel.Size = New-Object System.Drawing.Size(530, 18)
$fileLabel.Text = "Select Decklist File:"
$fileLabel.ForeColor = [System.Drawing.Color]::White
$cardFetchTab.Controls.Add($fileLabel)

$fileButton = New-Object System.Windows.Forms.Button
$fileButton.Location = New-Object System.Drawing.Point(10, 248)
$fileButton.Size = New-Object System.Drawing.Size(100, 23)
$fileButton.Text = "Browse..."
$fileButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$fileButton.ForeColor = [System.Drawing.Color]::White
$fileButton.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($fileButton)

$filePathLabel = New-Object System.Windows.Forms.Label
$filePathLabel.Location = New-Object System.Drawing.Point(120, 248)
$filePathLabel.Size = New-Object System.Drawing.Size(580, 23)
$filePathLabel.ForeColor = [System.Drawing.Color]::LightGray
$filePathLabel.Text = "No file selected"
$filePathLabel.AutoSize = $false
$cardFetchTab.Controls.Add($filePathLabel)

# General location button handlers
$generalLocationButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        $folderBrowser.Description = "Select general decklists location (parent folder containing all game folders)"
    
        # Set initial path if one exists
        if ($script:generalDecklistLocation -and (Test-Path $script:generalDecklistLocation)) {
            $folderBrowser.SelectedPath = $script:generalDecklistLocation
        }
    
        if ($folderBrowser.ShowDialog() -eq 'OK') {
            $script:generalDecklistLocation = $folderBrowser.SelectedPath
            $generalLocationTextBox.Text = $folderBrowser.SelectedPath
        
            # Save settings
            Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath -xOffset $xOffsetTextBox.Text -yOffset $yOffsetTextBox.Text -loadOffset $loadOffsetCheck.Checked -pluginOptions $script:pluginOptions
        
            $statusLabel.Text = "General decklists location set to: $($folderBrowser.SelectedPath)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Green
        }
    })

$clearGeneralButton.Add_Click({
        $script:generalDecklistLocation = ""
        $generalLocationTextBox.Text = ""
    
        # Save settings
        Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation "" -backImages $script:backImages -outputPath $script:outputPath
    
        $statusLabel.Text = "General decklists location cleared"
        $statusLabel.ForeColor = [System.Drawing.Color]::Green
    })

# Default folder button handlers
$defaultFolderButton.Add_Click({
        $currentPlugin = $pluginCombo.SelectedItem
    
        if ($currentPlugin -eq '-- Select a Game Plugin --') {
            $statusLabel.Text = "Please select a game plugin first"
            $statusLabel.ForeColor = [System.Drawing.Color]::Orange
            return
        }
    
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        $folderBrowser.Description = "Select default decklist folder for $currentPlugin"
    
        # Set initial path - prefer plugin-specific, fall back to general location
        if ($script:defaultDecklistFolders.ContainsKey($currentPlugin) -and (Test-Path $script:defaultDecklistFolders[$currentPlugin])) {
            $folderBrowser.SelectedPath = $script:defaultDecklistFolders[$currentPlugin]
        }
        elseif ($script:generalDecklistLocation -and (Test-Path $script:generalDecklistLocation)) {
            $folderBrowser.SelectedPath = $script:generalDecklistLocation
        }
    
        if ($folderBrowser.ShowDialog() -eq 'OK') {
            $script:defaultDecklistFolders[$currentPlugin] = $folderBrowser.SelectedPath
            $defaultFolderTextBox.Text = $folderBrowser.SelectedPath
        
            # Save settings
            Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath -xOffset $xOffsetTextBox.Text -yOffset $yOffsetTextBox.Text -loadOffset $loadOffsetCheck.Checked -pluginOptions $script:pluginOptions
        
            $statusLabel.Text = "Default decklist folder for $currentPlugin set to: $($folderBrowser.SelectedPath)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Green
        }
    })

$clearDefaultButton.Add_Click({
        $currentPlugin = $pluginCombo.SelectedItem
    
        if ($script:defaultDecklistFolders.ContainsKey($currentPlugin)) {
            $script:defaultDecklistFolders.Remove($currentPlugin)
        }
        $defaultFolderTextBox.Text = ""
    
        # Save settings
        Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath
    
        $statusLabel.Text = "Default decklist folder for $currentPlugin cleared"
        $statusLabel.ForeColor = [System.Drawing.Color]::Green
    })

# Back image button handlers
$backImageButton.Add_Click({
        $currentPlugin = $pluginCombo.SelectedItem
    
        if ($currentPlugin -eq '-- Select a Game Plugin --') {
            $statusLabel.Text = "Please select a game plugin first"
            $statusLabel.ForeColor = [System.Drawing.Color]::Orange
            return
        }
    
        $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
        $openFileDialog.Filter = "Image files (*.png;*.jpg;*.jpeg;*.webp)|*.png;*.jpg;*.jpeg;*.webp|All files (*.*)|*.*"
        $openFileDialog.Title = "Select Card Back Image for $currentPlugin"
    
        if ($openFileDialog.ShowDialog() -eq 'OK') {
            $script:backImages[$currentPlugin] = $openFileDialog.FileName
            $backImageTextBox.Text = $openFileDialog.FileName
        
            # Save settings
            Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath -xOffset $xOffsetTextBox.Text -yOffset $yOffsetTextBox.Text -loadOffset $loadOffsetCheck.Checked -pluginOptions $script:pluginOptions
        
            $statusLabel.Text = "Card back image set for $currentPlugin"
            $statusLabel.ForeColor = [System.Drawing.Color]::Green
        }
    })

$clearBackImageButton.Add_Click({
        $currentPlugin = $pluginCombo.SelectedItem
    
        if ($script:backImages.ContainsKey($currentPlugin)) {
            $script:backImages.Remove($currentPlugin)
        }
        $backImageTextBox.Text = ""
    
        # Save settings
        Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath
    
        $statusLabel.Text = "Card back image for $currentPlugin cleared"
        $statusLabel.ForeColor = [System.Drawing.Color]::Green
    })

$fileButton.Add_Click({
        $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
        # Include .dek as a supported decklist extension
        $openFileDialog.Filter = "Decklist files (*.txt;*.csv;*.ydk;*.dek)|*.txt;*.csv;*.ydk;*.dek|All files (*.*)|*.*"
        $openFileDialog.Title = "Select Decklist File"
    
        # Set initial directory - priority: plugin-specific > general location
        $currentPlugin = $pluginCombo.SelectedItem
        if ($script:defaultDecklistFolders.ContainsKey($currentPlugin) -and (Test-Path $script:defaultDecklistFolders[$currentPlugin])) {
            $openFileDialog.InitialDirectory = $script:defaultDecklistFolders[$currentPlugin]
        }
        elseif ($script:generalDecklistLocation -and (Test-Path $script:generalDecklistLocation)) {
            $openFileDialog.InitialDirectory = $script:generalDecklistLocation
        }

        if ($openFileDialog.ShowDialog() -eq 'OK') {
            $script:selectedFile = $openFileDialog.FileName
            $script:originalPath = Split-Path $script:selectedFile -Parent
            $filePathLabel.Text = $script:selectedFile
            $form.Refresh()

            # Auto-detect format when file is selected
            $detectedFormat = Get-DecklistFormat -filePath $script:selectedFile
            $script:detectedFormat = $detectedFormat

            # Update format combo if MTG is selected
            if ($pluginCombo.SelectedItem -eq 'Magic: The Gathering') {
                $formatIndex = $formatCombo.Items.IndexOf($detectedFormat)
                if ($formatIndex -ge 0) {
                    $formatCombo.SelectedIndex = $formatIndex
                    $statusLabel.Text = "File selected: $(Split-Path $script:selectedFile -Leaf) (Format auto-detected: $detectedFormat)"
                }
                else {
                    $statusLabel.Text = "File selected: $(Split-Path $script:selectedFile -Leaf) (Format: $detectedFormat - not in current plugin's supported formats)"
                }
            }
            else {
                $statusLabel.Text = "File selected: $(Split-Path $script:selectedFile -Leaf) (Detected format: $detectedFormat)"
            }

            $statusLabel.ForeColor = [System.Drawing.Color]::Green
            $form.Refresh()
        }
    })


$targetButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        $folderBrowser.Description = "Select silhouette-card-maker folder"

        if ($folderBrowser.ShowDialog() -eq 'OK') {
            $targetTextBox.Text = $folderBrowser.SelectedPath
            $script:targetFolder = $folderBrowser.SelectedPath
        
            # Save settings
            Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $script:targetFolder -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath
        }
    })

$autoDetectButton.Add_Click({
        $statusLabel.Text = "Auto-detecting Silhouette Card Maker folder..."
        $statusLabel.ForeColor = [System.Drawing.Color]::Blue
        $form.Refresh()

        $detectedPath = Find-SilhouetteCardMaker

        if ($detectedPath) {
            $targetTextBox.Text = $detectedPath
            $script:targetFolder = $detectedPath
        
            # Save settings
            Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $detectedPath -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath
        
            $statusLabel.Text = "Auto-detected: $detectedPath"
            $statusLabel.ForeColor = [System.Drawing.Color]::Green
        }
        else {
            $statusLabel.Text = "Auto-detection failed. Please browse manually."
            $statusLabel.ForeColor = [System.Drawing.Color]::Orange
        }
    })

# Format Selection (conditional visibility)
$formatLabel = New-Object System.Windows.Forms.Label
$formatLabel.Location = New-Object System.Drawing.Point(10, 280)
$formatLabel.Size = New-Object System.Drawing.Size(120, 18)
$formatLabel.Text = "Decklist Format:"
$formatLabel.ForeColor = [System.Drawing.Color]::White
$cardFetchTab.Controls.Add($formatLabel)

$formatCombo = New-Object System.Windows.Forms.ComboBox
$formatCombo.Location = New-Object System.Drawing.Point(140, 278)
$formatCombo.Size = New-Object System.Drawing.Size(200, 25)
$formatCombo.DropDownStyle = 'DropDownList'
$formatCombo.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$formatCombo.ForeColor = [System.Drawing.Color]::White
$formatCombo.FlatStyle = 'Flat'
$cardFetchTab.Controls.Add($formatCombo)

# Options Group Box
$optionsGroup = New-Object System.Windows.Forms.GroupBox
$optionsGroup.Location = New-Object System.Drawing.Point(10, 308)
$optionsGroup.Size = New-Object System.Drawing.Size(680, 110)
$optionsGroup.Text = "Plugin Options"
$optionsGroup.ForeColor = [System.Drawing.Color]::White
$cardFetchTab.Controls.Add($optionsGroup)

# MTG Options
$mtgOption1 = New-Object System.Windows.Forms.CheckBox
$mtgOption1.Location = New-Object System.Drawing.Point(20, 25)
$mtgOption1.Size = New-Object System.Drawing.Size(250, 20)
$mtgOption1.Text = "Ignore set/collector number (-i)"
$mtgOption1.ForeColor = [System.Drawing.Color]::White
$optionsGroup.Controls.Add($mtgOption1)

$mtgOption2 = New-Object System.Windows.Forms.CheckBox
$mtgOption2.Location = New-Object System.Drawing.Point(290, 25)
$mtgOption2.Size = New-Object System.Drawing.Size(250, 20)
$mtgOption2.Text = "Prefer older sets"
$mtgOption2.ForeColor = [System.Drawing.Color]::White
$optionsGroup.Controls.Add($mtgOption2)

$mtgOption3 = New-Object System.Windows.Forms.CheckBox
$mtgOption3.Location = New-Object System.Drawing.Point(20, 55)
$mtgOption3.Size = New-Object System.Drawing.Size(250, 20)
$mtgOption3.Text = "Prefer showcase treatment"
$mtgOption3.ForeColor = [System.Drawing.Color]::White
$optionsGroup.Controls.Add($mtgOption3)

$mtgOption4 = New-Object System.Windows.Forms.CheckBox
$mtgOption4.Location = New-Object System.Drawing.Point(290, 55)
$mtgOption4.Size = New-Object System.Drawing.Size(250, 20)
$mtgOption4.Text = "Prefer full/borderless/extended art"
$mtgOption4.ForeColor = [System.Drawing.Color]::White
$optionsGroup.Controls.Add($mtgOption4)

$preferSetLabel = New-Object System.Windows.Forms.Label
$preferSetLabel.Location = New-Object System.Drawing.Point(20, 85)
$preferSetLabel.Size = New-Object System.Drawing.Size(150, 20)
$preferSetLabel.Text = "Preferred set (optional):"
$preferSetLabel.ForeColor = [System.Drawing.Color]::White
$optionsGroup.Controls.Add($preferSetLabel)

$preferSetTextBox = New-Object System.Windows.Forms.TextBox
$preferSetTextBox.Location = New-Object System.Drawing.Point(180, 83)
$preferSetTextBox.Size = New-Object System.Drawing.Size(100, 25)
$preferSetTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$preferSetTextBox.ForeColor = [System.Drawing.Color]::White
$preferSetTextBox.BorderStyle = 'FixedSingle'
$optionsGroup.Controls.Add($preferSetTextBox)

# YuGiOh Options
$yugiohOption1 = New-Object System.Windows.Forms.CheckBox
$yugiohOption1.Location = New-Object System.Drawing.Point(20, 25)
$yugiohOption1.Size = New-Object System.Drawing.Size(250, 20)
$yugiohOption1.Text = "Ignore art version (--ignore_art_ver)"
$yugiohOption1.Visible = $false
$optionsGroup.Controls.Add($yugiohOption1)

$yugiohOption2 = New-Object System.Windows.Forms.CheckBox
$yugiohOption2.Location = New-Object System.Drawing.Point(290, 25)
$yugiohOption2.Size = New-Object System.Drawing.Size(250, 20)
$yugiohOption2.Text = "Include proxies (--include_proxy)"
$yugiohOption2.Visible = $false
$optionsGroup.Controls.Add($yugiohOption2)

$yugiohOption3 = New-Object System.Windows.Forms.CheckBox
$yugiohOption3.Location = New-Object System.Drawing.Point(20, 55)
$yugiohOption3.Size = New-Object System.Drawing.Size(250, 20)
$yugiohOption3.Text = "Prefer older art (--prefer_older_art)"
$yugiohOption3.Visible = $false
$optionsGroup.Controls.Add($yugiohOption3)

$yugiohOption4 = New-Object System.Windows.Forms.CheckBox
$yugiohOption4.Location = New-Object System.Drawing.Point(290, 55)
$yugiohOption4.Size = New-Object System.Drawing.Size(250, 20)
$yugiohOption4.Text = "Skip errata (--skip_errata)"
$yugiohOption4.Visible = $false
$optionsGroup.Controls.Add($yugiohOption4)

# Lorcana Options
$lorcanaOption1 = New-Object System.Windows.Forms.CheckBox
$lorcanaOption1.Location = New-Object System.Drawing.Point(20, 25)
$lorcanaOption1.Size = New-Object System.Drawing.Size(250, 20)
$lorcanaOption1.Text = "Include enchanted (-e)"
$lorcanaOption1.Visible = $false
$optionsGroup.Controls.Add($lorcanaOption1)

# Riftbound Options
$riftboundOption1 = New-Object System.Windows.Forms.CheckBox
$riftboundOption1.Location = New-Object System.Drawing.Point(20, 25)
$riftboundOption1.Size = New-Object System.Drawing.Size(250, 20)
$riftboundOption1.Text = "Include enchanted (-e)"
$riftboundOption1.Visible = $false
$optionsGroup.Controls.Add($riftboundOption1)

# Digimon Options
$digimonOption1 = New-Object System.Windows.Forms.CheckBox
$digimonOption1.Location = New-Object System.Drawing.Point(20, 25)
$digimonOption1.Size = New-Object System.Drawing.Size(250, 20)
$digimonOption1.Text = "Include alternate art (-a)"
$digimonOption1.Visible = $false
$optionsGroup.Controls.Add($digimonOption1)

# Gundam Options
$gundamOption1 = New-Object System.Windows.Forms.CheckBox
$gundamOption1.Location = New-Object System.Drawing.Point(20, 25)
$gundamOption1.Size = New-Object System.Drawing.Size(250, 20)
$gundamOption1.Text = "Include alternate art (-a)"
$gundamOption1.Visible = $false
$optionsGroup.Controls.Add($gundamOption1)

# Star Wars Options
$swuOption1 = New-Object System.Windows.Forms.CheckBox
$swuOption1.Location = New-Object System.Drawing.Point(20, 25)
$swuOption1.Size = New-Object System.Drawing.Size(250, 20)
$swuOption1.Text = "Include hyperspace art (-h)"
$optionsGroup.Controls.Add($swuOption1)

# Info label
$infoLabel = New-Object System.Windows.Forms.Label
$infoLabel.Location = New-Object System.Drawing.Point(20, 120)
$infoLabel.Size = New-Object System.Drawing.Size(520, 50)
$infoLabel.Text = ""
$optionsGroup.Controls.Add($infoLabel)

# Helper function to save current plugin options
function Save-CurrentPluginOptions {
    param([string]$pluginName)
    
    if ($pluginName -eq '-- Select a Game Plugin --') { return }
    
    $options = @{}
    switch ($pluginName) {
        'Magic: The Gathering' {
            $options = @{
                option1   = $mtgOption1.Checked
                option2   = $mtgOption2.Checked
                option3   = $mtgOption3.Checked
                option4   = $mtgOption4.Checked
                preferSet = $preferSetTextBox.Text
            }
        }
        'Yu-Gi-Oh!' {
            $options = @{
                option1 = $yugiohOption1.Checked
                option2 = $yugiohOption2.Checked
                option3 = $yugiohOption3.Checked
                option4 = $yugiohOption4.Checked
            }
        }
        'Lorcana' {
            $options = @{ option1 = $lorcanaOption1.Checked }
        }
        'Riftbound' {
            $options = @{ option1 = $riftboundOption1.Checked }
        }
        'Digimon' {
            $options = @{ option1 = $digimonOption1.Checked }
        }
        'Gundam' {
            $options = @{ option1 = $gundamOption1.Checked }
        }
        'Star Wars Unlimited' {
            $options = @{ option1 = $swuOption1.Checked }
        }
    }
    
    if ($options.Count -gt 0) {
        $script:pluginOptions[$pluginName] = $options
        Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath -xOffset $xOffsetTextBox.Text -yOffset $yOffsetTextBox.Text -loadOffset $loadOffsetCheck.Checked -pluginOptions $script:pluginOptions
    }
}

# Helper function to load plugin options
function Get-PluginOptions {
    param([string]$pluginName)
    
    if ($pluginName -eq '-- Select a Game Plugin --') { return }
    if (-not $script:pluginOptions -or -not $script:pluginOptions.ContainsKey($pluginName)) { return }
    
    $options = $script:pluginOptions[$pluginName]
    
    switch ($pluginName) {
        'Magic: The Gathering' {
            if ($options.PSObject.Properties.Name -contains 'option1') { $mtgOption1.Checked = $options.option1 }
            if ($options.PSObject.Properties.Name -contains 'option2') { $mtgOption2.Checked = $options.option2 }
            if ($options.PSObject.Properties.Name -contains 'option3') { $mtgOption3.Checked = $options.option3 }
            if ($options.PSObject.Properties.Name -contains 'option4') { $mtgOption4.Checked = $options.option4 }
            if ($options.PSObject.Properties.Name -contains 'preferSet') { $preferSetTextBox.Text = $options.preferSet }
        }
        'Yu-Gi-Oh!' {
            if ($options.PSObject.Properties.Name -contains 'option1') { $yugiohOption1.Checked = $options.option1 }
            if ($options.PSObject.Properties.Name -contains 'option2') { $yugiohOption2.Checked = $options.option2 }
            if ($options.PSObject.Properties.Name -contains 'option3') { $yugiohOption3.Checked = $options.option3 }
            if ($options.PSObject.Properties.Name -contains 'option4') { $yugiohOption4.Checked = $options.option4 }
        }
        'Lorcana' {
            if ($options.PSObject.Properties.Name -contains 'option1') { $lorcanaOption1.Checked = $options.option1 }
        }
        'Riftbound' {
            if ($options.PSObject.Properties.Name -contains 'option1') { $riftboundOption1.Checked = $options.option1 }
        }
        'Digimon' {
            if ($options.PSObject.Properties.Name -contains 'option1') { $digimonOption1.Checked = $options.option1 }
        }
        'Gundam' {
            if ($options.PSObject.Properties.Name -contains 'option1') { $gundamOption1.Checked = $options.option1 }
        }
        'Star Wars Unlimited' {
            if ($options.PSObject.Properties.Name -contains 'option1') { $swuOption1.Checked = $options.option1 }
        }
    }
}

# Update UI based on plugin selection
$pluginCombo.Add_SelectedIndexChanged({
        $plugin = $pluginCombo.SelectedItem
    
        # Update default folder textbox for current plugin
        if ($script:defaultDecklistFolders.ContainsKey($plugin)) {
            $defaultFolderTextBox.Text = $script:defaultDecklistFolders[$plugin]
        }
        else {
            $defaultFolderTextBox.Text = ""
        }
    
        # Update back image textbox for current plugin
        if ($script:backImages.ContainsKey($plugin)) {
            $backImageTextBox.Text = $script:backImages[$plugin]
        }
        else {
            $backImageTextBox.Text = ""
        }
    
        # Hide all options first
        $mtgOption1.Visible = $false
        $mtgOption2.Visible = $false
        $mtgOption3.Visible = $false
        $mtgOption4.Visible = $false
        $preferSetLabel.Visible = $false
        $preferSetTextBox.Visible = $false
        $yugiohOption1.Visible = $false
        $yugiohOption2.Visible = $false
        $yugiohOption3.Visible = $false
        $yugiohOption4.Visible = $false
        $lorcanaOption1.Visible = $false
        $riftboundOption1.Visible = $false
        $digimonOption1.Visible = $false
        $gundamOption1.Visible = $false
        $swuOption1.Visible = $false
    
        switch ($plugin) {
            '-- Select a Game Plugin --' {
                # Hide format and options when placeholder is selected
                $formatLabel.Visible = $false
                $formatCombo.Visible = $false
                $optionsGroup.Visible = $false
                $defaultFolderLabel.Text = "Game-Specific Folder (optional):"
            }
            'Magic: The Gathering' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('simple', 'mtga', 'mtgo', 'dek', 'tappedout', 'archidekt', 'deckstats', 'moxfield', 'scryfall_json'))
                $formatCombo.SelectedIndex = 1
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true

                # Auto-select detected format if available
                if ($script:selectedFile -and $script:detectedFormat) {
                    $detectedIndex = $formatCombo.Items.IndexOf($script:detectedFormat)
                    if ($detectedIndex -ge 0) {
                        $formatCombo.SelectedIndex = $detectedIndex
                    }
                }

                $mtgOption1.Visible = $true
                $mtgOption2.Visible = $true
                $mtgOption3.Visible = $true
                $mtgOption4.Visible = $true
                $preferSetLabel.Visible = $true
                $preferSetTextBox.Visible = $true

                $defaultFolderLabel.Text = "MTG-Specific Folder (optional):"
                $infoLabel.Text = "MTG plugin fetches card images from Scryfall and organizes them for printing. Supports TappedOut format!"
            }
            'Yu-Gi-Oh!' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('ydk', 'ydke'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $yugiohOption1.Visible = $true
                $yugiohOption2.Visible = $true
                $yugiohOption3.Visible = $true
                $yugiohOption4.Visible = $true
            
                $defaultFolderLabel.Text = "Yu-Gi-Oh!-Specific Folder (optional):"
                $infoLabel.Text = "Yu-Gi-Oh! plugin supports YDK and YDKE decklist formats."
            }
            'Altered' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('ajordat'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Altered-Specific Folder (optional):"
                $infoLabel.Text = "Altered plugin supports Ajordat decklist format."
            }
            'Digimon' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('tts', 'digimoncardio', 'digimoncarddev', 'digimoncardapp', 'digimonmeta', 'untap'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $digimonOption1.Visible = $true
            
                $defaultFolderLabel.Text = "Digimon-Specific Folder (optional):"
                $infoLabel.Text = "Digimon plugin supports TTS, Digimoncard.io, Digimoncard.dev, Digimoncard.app, DigimonMeta, and Untap formats."
            }
            'Dragon Ball Super' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('deckplanet'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Dragon Ball Super-Specific Folder (optional):"
                $infoLabel.Text = "Dragon Ball Super plugin uses DeckPlanet format (same as Gundam)."
            }
            'Flesh and Blood' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('fabrary'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Flesh and Blood-Specific Folder (optional):"
                $infoLabel.Text = "Flesh and Blood plugin supports Fabrary format."
            }
            'Grand Archive' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('omnideck'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Grand Archive-Specific Folder (optional):"
                $infoLabel.Text = "Grand Archive plugin supports Omnideck format."
            }
            'Gundam' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('deckplanet', 'limitless', 'egman', 'exburst'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $gundamOption1.Visible = $true
            
                $defaultFolderLabel.Text = "Gundam-Specific Folder (optional):"
                $infoLabel.Text = "Gundam plugin supports DeckPlanet, Limitless, Egman, and ExBurst formats."
            }
            'Lorcana' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('dreamborn'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $lorcanaOption1.Visible = $true
            
                $defaultFolderLabel.Text = "Lorcana-Specific Folder (optional):"
                $infoLabel.Text = "Lorcana plugin supports Dreamborn decklist format."
            }
            'Netrunner' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('text', 'bbcode', 'markdown', 'plain_text', 'jinteki'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Netrunner-Specific Folder (optional):"
                $infoLabel.Text = "Netrunner plugin supports text, bbCode, markdown, plain text, and Jinteki formats."
            }
            'One Piece' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('optcgsim', 'egman'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "One Piece-Specific Folder (optional):"
                $infoLabel.Text = "One Piece plugin supports OPTCG Simulator and Egman formats."
            }
            'Riftbound' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('tts', 'pixelborn', 'piltover_archive'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $riftboundOption1.Visible = $true
            
                $defaultFolderLabel.Text = "Riftbound-Specific Folder (optional):"
                $infoLabel.Text = "Riftbound plugin supports Tabletop Simulator, Pixelborn, and Piltover Archive formats."
            }
            'Star Wars Unlimited' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('swudb_json', 'melee', 'picklist'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $swuOption1.Visible = $true
            
                $defaultFolderLabel.Text = "Star Wars Unlimited-Specific Folder (optional):"
                $infoLabel.Text = "Star Wars Unlimited plugin supports SWUDB JSON, Melee, and Picklist formats."
            }
            'Cards Against Humanity' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('cah_api', 'cah_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Cards Against Humanity-Specific Folder (optional):"
                $infoLabel.Text = "Cards Against Humanity plugin supports CAH API and scraper formats."
            }
            'CCGTrader' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('universal', 'cross_game', 'popular_games'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "CCGTrader-Specific Folder (optional):"
                $infoLabel.Text = "CCGTrader plugin supports universal CCG card scraping from multiple games."
            }
            'CF Vanguard' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('cfv_api', 'cfv_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "CF Vanguard-Specific Folder (optional):"
                $infoLabel.Text = "CF Vanguard plugin supports CF Vanguard API and scraper formats."
            }
            'Fluxx' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('looney', 'fluxx_api', 'fluxx_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Fluxx-Specific Folder (optional):"
                $infoLabel.Text = "Fluxx plugin supports Looney Labs, Fluxx API, and scraper formats."
            }
            'Force of Will' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('fow_api', 'fow_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Force of Will-Specific Folder (optional):"
                $infoLabel.Text = "Force of Will plugin supports FOW API and scraper formats."
            }
            'Marvel Champions' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('mc_api', 'mc_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Marvel Champions-Specific Folder (optional):"
                $infoLabel.Text = "Marvel Champions plugin supports MC API and scraper formats."
            }
            'MetaZoo' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('mz_api', 'mz_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "MetaZoo-Specific Folder (optional):"
                $infoLabel.Text = "MetaZoo plugin supports MZ API and scraper formats."
            }
            'Munchkin' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('munchkin_api', 'munchkin_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Munchkin-Specific Folder (optional):"
                $infoLabel.Text = "Munchkin plugin supports Munchkin API and scraper formats."
            }
            'Pokemon' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('pokemon_api', 'pokemon_scraper', 'limitless'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Pokemon-Specific Folder (optional):"
                $infoLabel.Text = "Pokemon plugin supports Pokemon API, scraper, and Limitless formats."
            }
            'Shadowverse Evolve' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('sve_api', 'sve_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Shadowverse Evolve-Specific Folder (optional):"
                $infoLabel.Text = "Shadowverse Evolve plugin supports SVE API and scraper formats."
            }
            'Star Realms' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('sr_api', 'sr_scraper', 'official_gallery', 'boardgamegeek', 'tier_list'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Star Realms-Specific Folder (optional):"
                $infoLabel.Text = "Star Realms plugin supports SR API, scraper, official gallery, BoardGameGeek, and tier list formats."
            }
            'Union Arena' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('ua_api', 'ua_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Union Arena-Specific Folder (optional):"
                $infoLabel.Text = "Union Arena plugin supports UA API and scraper formats."
            }
            'Universus' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('uvs_api', 'uvs_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Universus-Specific Folder (optional):"
                $infoLabel.Text = "Universus plugin supports UVS API and scraper formats."
            }
            'Weiss Schwarz' {
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('ws_api', 'ws_scraper'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $true
            
                $defaultFolderLabel.Text = "Weiss Schwarz-Specific Folder (optional):"
                $infoLabel.Text = "Weiss Schwarz plugin supports WS API and scraper formats."
            }
            default {
                # Generic fallback for games discovered via games_index.json or folders
                $formatCombo.Items.Clear()
                $formatCombo.Items.AddRange(@('simple', 'mtga', 'mtgo', 'archidekt', 'deckstats', 'moxfield', 'scryfall_json'))
                $formatCombo.SelectedIndex = 0
                $formatLabel.Visible = $true
                $formatCombo.Visible = $true
                $optionsGroup.Visible = $false
                
                $defaultFolderLabel.Text = "$plugin-Specific Folder (optional):"
                $infoLabel.Text = "$plugin plugin detected. Using standard formats."
            }
        }
    
        # Load saved options for the selected plugin
        Get-PluginOptions -pluginName $plugin
    })

# Add event handlers to all plugin option checkboxes to save when changed
$mtgOption1.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Magic: The Gathering' })
$mtgOption2.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Magic: The Gathering' })
$mtgOption3.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Magic: The Gathering' })
$mtgOption4.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Magic: The Gathering' })
$preferSetTextBox.Add_TextChanged({ Save-CurrentPluginOptions -pluginName 'Magic: The Gathering' })

$yugiohOption1.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Yu-Gi-Oh!' })
$yugiohOption2.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Yu-Gi-Oh!' })
$yugiohOption3.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Yu-Gi-Oh!' })
$yugiohOption4.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Yu-Gi-Oh!' })

$lorcanaOption1.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Lorcana' })
$riftboundOption1.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Riftbound' })
$digimonOption1.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Digimon' })
$gundamOption1.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Gundam' })
$swuOption1.Add_CheckedChanged({ Save-CurrentPluginOptions -pluginName 'Star Wars Unlimited' })

# Function to update main plugin list
function Update-MainPluginList {
    try {
        $enabledPluginNames = Export-PluginListForGUI
        $currentSelection = $pluginCombo.SelectedItem
        
        $pluginCombo.Items.Clear()
        if ($enabledPluginNames -and $enabledPluginNames.Count -gt 0) {
            $pluginCombo.Items.AddRange($enabledPluginNames)
            
            # Try to restore previous selection
            $newIndex = $enabledPluginNames.IndexOf($currentSelection)
            if ($newIndex -ge 0) {
                $pluginCombo.SelectedIndex = $newIndex
            }
            else {
                $pluginCombo.SelectedIndex = 0
            }
        }
    }
    catch {
        Write-Warning "Failed to refresh plugin list: $($_.Exception.Message)"
    }
}

# Load saved settings
$savedSettings = Import-Settings
if ($savedSettings) {
    # Load general decklists location
    if ($savedSettings.generalDecklistLocation -and (Test-Path $savedSettings.generalDecklistLocation)) {
        $script:generalDecklistLocation = $savedSettings.generalDecklistLocation
        $generalLocationTextBox.Text = $script:generalDecklistLocation
    }
    
    # Load per-plugin default folders - convert PSCustomObject back to hashtable
    if ($savedSettings.defaultDecklistFolders) {
        $script:defaultDecklistFolders = @{}
        $savedSettings.defaultDecklistFolders.PSObject.Properties | ForEach-Object {
            $script:defaultDecklistFolders[$_.Name] = $_.Value
        }
    }
    
    # Load target folder
    if ($savedSettings.targetFolder -and (Test-Path $savedSettings.targetFolder)) {
        $targetTextBox.Text = $savedSettings.targetFolder
        $script:targetFolder = $savedSettings.targetFolder
    }
    
    # Load per-plugin back images - convert PSCustomObject back to hashtable
    if ($savedSettings.backImages) {
        $script:backImages = @{}
        $savedSettings.backImages.PSObject.Properties | ForEach-Object {
            $script:backImages[$_.Name] = $_.Value
        }
    }
    
    # Load output path
    if ($savedSettings.outputPath) {
        $script:outputPath = $savedSettings.outputPath
    }
    
    # Load per-plugin options - convert PSCustomObject back to hashtable
    if ($savedSettings.pluginOptions) {
        $script:pluginOptions = @{}
        $savedSettings.pluginOptions.PSObject.Properties | ForEach-Object {
            $script:pluginOptions[$_.Name] = $_.Value
        }
    }
}

# Don't trigger initial update - let user select a plugin first
# This ensures the format dropdown and options populate correctly

# ===== TAB 2: PDF OPTIONS =====
$pdfOptionsTab = New-Object System.Windows.Forms.TabPage
$pdfOptionsTab.Text = "PDF Options"
$pdfOptionsTab.BackColor = [System.Drawing.Color]::FromArgb(37, 37, 38)
$mainTabControl.Controls.Add($pdfOptionsTab)

# ===== TAB 3: OFFSET PDF =====
$offsetPdfTab = New-Object System.Windows.Forms.TabPage
$offsetPdfTab.Text = "Offset PDF"
$offsetPdfTab.BackColor = [System.Drawing.Color]::FromArgb(37, 37, 38)
$mainTabControl.Controls.Add($offsetPdfTab)

# ===== TAB 4: BACK IMAGE SCRAPER =====
$backImageScraperTab = New-Object System.Windows.Forms.TabPage
$backImageScraperTab.Text = "Back Image Scraper"
$backImageScraperTab.BackColor = [System.Drawing.Color]::FromArgb(37, 37, 38)
$mainTabControl.Controls.Add($backImageScraperTab)

# Offset PDF Description
$offsetDescLabel = New-Object System.Windows.Forms.Label
$offsetDescLabel.Location = New-Object System.Drawing.Point(10, 10)
$offsetDescLabel.Size = New-Object System.Drawing.Size(680, 75)
$offsetDescLabel.Text = "Offset PDF compensates for printer alignment issues when printing double-sided cards.`n`nCalibration: Print a calibration sheet from the 'calibration' folder double-sided. Hold it up to light and see which grid marks align with the back marks. The aligned coordinates (e.g., 10,0) are your offset values in millimeters.`n`nEnter those values below to adjust ALL pages in your PDF at once."
$offsetDescLabel.ForeColor = [System.Drawing.Color]::LightGray
$offsetPdfTab.Controls.Add($offsetDescLabel)

# X Offset
$xOffsetLabel = New-Object System.Windows.Forms.Label
$xOffsetLabel.Location = New-Object System.Drawing.Point(10, 100)
$xOffsetLabel.Size = New-Object System.Drawing.Size(120, 18)
$xOffsetLabel.Text = "X Offset (mm):"
$xOffsetLabel.ForeColor = [System.Drawing.Color]::White
$offsetPdfTab.Controls.Add($xOffsetLabel)

$xOffsetTextBox = New-Object System.Windows.Forms.TextBox
$xOffsetTextBox.Location = New-Object System.Drawing.Point(140, 98)
$xOffsetTextBox.Size = New-Object System.Drawing.Size(80, 22)
$xOffsetTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$xOffsetTextBox.ForeColor = [System.Drawing.Color]::White
$xOffsetTextBox.BorderStyle = 'FixedSingle'
$xOffsetTextBox.Text = "0"
$offsetPdfTab.Controls.Add($xOffsetTextBox)

# Y Offset
$yOffsetLabel = New-Object System.Windows.Forms.Label
$yOffsetLabel.Location = New-Object System.Drawing.Point(240, 100)
$yOffsetLabel.Size = New-Object System.Drawing.Size(100, 18)
$yOffsetLabel.Text = "Y Offset (mm):"
$yOffsetLabel.ForeColor = [System.Drawing.Color]::White
$offsetPdfTab.Controls.Add($yOffsetLabel)

$yOffsetTextBox = New-Object System.Windows.Forms.TextBox
$yOffsetTextBox.Location = New-Object System.Drawing.Point(350, 98)
$yOffsetTextBox.Size = New-Object System.Drawing.Size(80, 22)
$yOffsetTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$yOffsetTextBox.ForeColor = [System.Drawing.Color]::White
$yOffsetTextBox.BorderStyle = 'FixedSingle'
$yOffsetTextBox.Text = "0"
$offsetPdfTab.Controls.Add($yOffsetTextBox)

$xOffsetPixelsLabel = New-Object System.Windows.Forms.Label
$xOffsetPixelsLabel.Location = New-Object System.Drawing.Point(10, 130)
$xOffsetPixelsLabel.Size = New-Object System.Drawing.Size(120, 18)
$xOffsetPixelsLabel.Text = "X Offset (px):"
$xOffsetPixelsLabel.ForeColor = [System.Drawing.Color]::White
$offsetPdfTab.Controls.Add($xOffsetPixelsLabel)

$xOffsetPixelsTextBox = New-Object System.Windows.Forms.TextBox
$xOffsetPixelsTextBox.Location = New-Object System.Drawing.Point(140, 128)
$xOffsetPixelsTextBox.Size = New-Object System.Drawing.Size(80, 22)
$xOffsetPixelsTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$xOffsetPixelsTextBox.ForeColor = [System.Drawing.Color]::White
$xOffsetPixelsTextBox.BorderStyle = 'FixedSingle'
$xOffsetPixelsTextBox.Text = "0"
$offsetPdfTab.Controls.Add($xOffsetPixelsTextBox)

$yOffsetPixelsLabel = New-Object System.Windows.Forms.Label
$yOffsetPixelsLabel.Location = New-Object System.Drawing.Point(240, 130)
$yOffsetPixelsLabel.Size = New-Object System.Drawing.Size(100, 18)
$yOffsetPixelsLabel.Text = "Y Offset (px):"
$yOffsetPixelsLabel.ForeColor = [System.Drawing.Color]::White
$offsetPdfTab.Controls.Add($yOffsetPixelsLabel)

$yOffsetPixelsTextBox = New-Object System.Windows.Forms.TextBox
$yOffsetPixelsTextBox.Location = New-Object System.Drawing.Point(350, 128)
$yOffsetPixelsTextBox.Size = New-Object System.Drawing.Size(80, 22)
$yOffsetPixelsTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$yOffsetPixelsTextBox.ForeColor = [System.Drawing.Color]::White
$yOffsetPixelsTextBox.BorderStyle = 'FixedSingle'
$yOffsetPixelsTextBox.Text = "0"
$offsetPdfTab.Controls.Add($yOffsetPixelsTextBox)

# Save Offset Checkbox
$saveOffsetCheck = New-Object System.Windows.Forms.CheckBox
$saveOffsetCheck.Location = New-Object System.Drawing.Point(450, 130)
$saveOffsetCheck.Size = New-Object System.Drawing.Size(200, 18)
$saveOffsetCheck.Text = "Save offset for future use"
$saveOffsetCheck.ForeColor = [System.Drawing.Color]::White
$offsetPdfTab.Controls.Add($saveOffsetCheck)

# Load Saved Offsets (for create_pdf.py)
$loadOffsetCheck = New-Object System.Windows.Forms.CheckBox
$loadOffsetCheck.Location = New-Object System.Drawing.Point(10, 160)
$loadOffsetCheck.Size = New-Object System.Drawing.Size(680, 18)
$loadOffsetCheck.Text = "Auto-apply saved offset when creating PDFs (--load_offset)"
$offsetPdfTab.Controls.Add($loadOffsetCheck)

# Helper function to save offset to both GUI settings and Python JSON file
function Save-OffsetData {
    # Save to GUI settings
    Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath -xOffset $xOffsetTextBox.Text -yOffset $yOffsetTextBox.Text -loadOffset $loadOffsetCheck.Checked -pluginOptions $script:pluginOptions
	
    # Also save to data/offset_data.json for Python scripts
    if ($targetTextBox.Text) {
        try {
            # Parse offset values, default to 0 if empty or invalid (allow fractional mm)
            $xOffset = 0.0
            $yOffset = 0.0
			
            if ($xOffsetTextBox.Text -and [double]::TryParse($xOffsetTextBox.Text, [ref]$xOffset)) {
                # Successfully parsed X offset (can be fractional)
            }
            else {
                $xOffset = 0.0
            }
			
            if ($yOffsetTextBox.Text -and [double]::TryParse($yOffsetTextBox.Text, [ref]$yOffset)) {
                # Successfully parsed Y offset (can be fractional)
            }
            else {
                $yOffset = 0.0
            }
			
            $dataDir = Join-Path $targetTextBox.Text "data"
            if (-not (Test-Path $dataDir)) {
                New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
            }
			
            # Create JSON with numeric values (UTF8 without BOM)
            $offsetFile = Join-Path $dataDir "offset_data.json"
            $jsonContent = "{`"x_offset`":$xOffset,`"y_offset`":$yOffset}"
            $utf8NoBom = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($offsetFile, $jsonContent, $utf8NoBom)
        }
        catch {
            # Silently continue if offset file can't be saved
        }
    }
}

# Event handlers for offset controls to save settings
$xOffsetTextBox.Add_TextChanged({
        if ($script:isUpdatingOffsetUI) { return }
        $script:isUpdatingOffsetUI = $true
        try {
            $ppi = 300.0
            if ($ppiTextBox -and $ppiTextBox.Text) {
                [double]::TryParse($ppiTextBox.Text, [ref]$ppi) | Out-Null
                if ($ppi -le 0) { $ppi = 300.0 }
            }

            $xMm = 0.0
            if ($xOffsetTextBox.Text -and [double]::TryParse($xOffsetTextBox.Text, [ref]$xMm)) {
                $xPx = [Math]::Round(($xMm / 25.4) * $ppi, 2)
                if ($xOffsetPixelsTextBox) { $xOffsetPixelsTextBox.Text = $xPx.ToString() }
            }
            else {
                if ($xOffsetPixelsTextBox) { $xOffsetPixelsTextBox.Text = "" }
            }

            if ($saveOffsetCheck.Checked) {
                Save-OffsetData
            }
        }
        finally {
            $script:isUpdatingOffsetUI = $false
        }
    })

$yOffsetTextBox.Add_TextChanged({
        if ($script:isUpdatingOffsetUI) { return }
        $script:isUpdatingOffsetUI = $true
        try {
            $ppi = 300.0
            if ($ppiTextBox -and $ppiTextBox.Text) {
                [double]::TryParse($ppiTextBox.Text, [ref]$ppi) | Out-Null
                if ($ppi -le 0) { $ppi = 300.0 }
            }

            $yMm = 0.0
            if ($yOffsetTextBox.Text -and [double]::TryParse($yOffsetTextBox.Text, [ref]$yMm)) {
                $yPx = [Math]::Round(($yMm / 25.4) * $ppi, 2)
                if ($yOffsetPixelsTextBox) { $yOffsetPixelsTextBox.Text = $yPx.ToString() }
            }
            else {
                if ($yOffsetPixelsTextBox) { $yOffsetPixelsTextBox.Text = "" }
            }

            if ($saveOffsetCheck.Checked) {
                Save-OffsetData
            }
        }
        finally {
            $script:isUpdatingOffsetUI = $false
        }
    })

$xOffsetPixelsTextBox.Add_TextChanged({
        if ($script:isUpdatingOffsetUI) { return }
        $script:isUpdatingOffsetUI = $true
        try {
            $ppi = 300.0
            if ($ppiTextBox -and $ppiTextBox.Text) {
                [double]::TryParse($ppiTextBox.Text, [ref]$ppi) | Out-Null
                if ($ppi -le 0) { $ppi = 300.0 }
            }

            $xPx = 0.0
            if ($xOffsetPixelsTextBox.Text -and [double]::TryParse($xOffsetPixelsTextBox.Text, [ref]$xPx) -and $ppi -gt 0) {
                $xMm = [Math]::Round(($xPx / $ppi) * 25.4, 2)
                $xOffsetTextBox.Text = $xMm.ToString()
            }

            if ($saveOffsetCheck.Checked) {
                Save-OffsetData
            }
        }
        finally {
            $script:isUpdatingOffsetUI = $false
        }
    })

$yOffsetPixelsTextBox.Add_TextChanged({
        if ($script:isUpdatingOffsetUI) { return }
        $script:isUpdatingOffsetUI = $true
        try {
            $ppi = 300.0
            if ($ppiTextBox -and $ppiTextBox.Text) {
                [double]::TryParse($ppiTextBox.Text, [ref]$ppi) | Out-Null
                if ($ppi -le 0) { $ppi = 300.0 }
            }

            $yPx = 0.0
            if ($yOffsetPixelsTextBox.Text -and [double]::TryParse($yOffsetPixelsTextBox.Text, [ref]$yPx) -and $ppi -gt 0) {
                $yMm = [Math]::Round(($yPx / $ppi) * 25.4, 2)
                $yOffsetTextBox.Text = $yMm.ToString()
            }

            if ($saveOffsetCheck.Checked) {
                Save-OffsetData
            }
        }
        finally {
            $script:isUpdatingOffsetUI = $false
        }
    })

$saveOffsetCheck.Add_CheckedChanged({
        if ($saveOffsetCheck.Checked) {
            Save-OffsetData
        }
    })

$loadOffsetCheck.Add_CheckedChanged({
        Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath -xOffset $xOffsetTextBox.Text -yOffset $yOffsetTextBox.Text -loadOffset $loadOffsetCheck.Checked -pluginOptions $script:pluginOptions
    })

# Load offset values from saved settings (must be done after controls are created)
if ($savedSettings) {
    if ($savedSettings.xOffset) {
        $xOffsetTextBox.Text = $savedSettings.xOffset
    }
    if ($savedSettings.yOffset) {
        $yOffsetTextBox.Text = $savedSettings.yOffset
    }
    if ($savedSettings.PSObject.Properties.Name -contains 'loadOffset') {
        $loadOffsetCheck.Checked = $savedSettings.loadOffset
    }
}

# Back Image Scraper Tab Content
$backImageScraperTitle = New-Object System.Windows.Forms.Label
$backImageScraperTitle.Location = New-Object System.Drawing.Point(10, 10)
$backImageScraperTitle.Size = New-Object System.Drawing.Size(680, 25)
$backImageScraperTitle.Text = "Card Back Image Scraper"
$backImageScraperTitle.Font = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
$backImageScraperTitle.ForeColor = [System.Drawing.Color]::White
$backImageScraperTab.Controls.Add($backImageScraperTitle)

$backImageScraperDesc = New-Object System.Windows.Forms.Label
$backImageScraperDesc.Location = New-Object System.Drawing.Point(10, 40)
$backImageScraperDesc.Size = New-Object System.Drawing.Size(680, 50)
$backImageScraperDesc.Text = "Download official card back images from various TCG sources.`nThese images can be used for double-sided card printing."
$backImageScraperDesc.ForeColor = [System.Drawing.Color]::LightGray
$backImageScraperTab.Controls.Add($backImageScraperDesc)

# Output Directory
$backOutputLabel = New-Object System.Windows.Forms.Label
$backOutputLabel.Location = New-Object System.Drawing.Point(10, 100)
$backOutputLabel.Size = New-Object System.Drawing.Size(200, 18)
$backOutputLabel.Text = "Output Directory:"
$backOutputLabel.ForeColor = [System.Drawing.Color]::White
$backImageScraperTab.Controls.Add($backOutputLabel)

$backOutputTextBox = New-Object System.Windows.Forms.TextBox
$backOutputTextBox.Location = New-Object System.Drawing.Point(10, 120)
$backOutputTextBox.Size = New-Object System.Drawing.Size(500, 22)
$backOutputTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$backOutputTextBox.ForeColor = [System.Drawing.Color]::White
$backOutputTextBox.BorderStyle = 'FixedSingle'
$backOutputTextBox.Text = "out/back"
$backImageScraperTab.Controls.Add($backOutputTextBox)

$backOutputButton = New-Object System.Windows.Forms.Button
$backOutputButton.Location = New-Object System.Drawing.Point(520, 119)
$backOutputButton.Size = New-Object System.Drawing.Size(100, 23)
$backOutputButton.Text = "Browse..."
$backOutputButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$backOutputButton.ForeColor = [System.Drawing.Color]::White
$backOutputButton.FlatStyle = 'Flat'
$backImageScraperTab.Controls.Add($backOutputButton)

# Game Selection
$backGameLabel = New-Object System.Windows.Forms.Label
$backGameLabel.Location = New-Object System.Drawing.Point(10, 150)
$backGameLabel.Size = New-Object System.Drawing.Size(200, 18)
$backGameLabel.Text = "Select Game (optional):"
$backGameLabel.ForeColor = [System.Drawing.Color]::White
$backImageScraperTab.Controls.Add($backGameLabel)

$backGameCombo = New-Object System.Windows.Forms.ComboBox
$backGameCombo.Location = New-Object System.Drawing.Point(10, 170)
$backGameCombo.Size = New-Object System.Drawing.Size(300, 25)
$backGameCombo.DropDownStyle = 'DropDownList'
$backGameCombo.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$backGameCombo.ForeColor = [System.Drawing.Color]::White
$backGameCombo.FlatStyle = 'Flat'
$backGameCombo.Items.AddRange(@('-- All Games --', 'Magic: The Gathering', 'Pokemon TCG', 'Yu-Gi-Oh!', 'Lorcana', 'Flesh and Blood', 'Digimon TCG', 'One Piece TCG', 'Gundam TCG', 'Star Wars Unlimited', 'Altered TCG'))
$backGameCombo.SelectedIndex = 0
$backImageScraperTab.Controls.Add($backGameCombo)

# Scrape Buttons
$scrapeSpecificButton = New-Object System.Windows.Forms.Button
$scrapeSpecificButton.Location = New-Object System.Drawing.Point(10, 210)
$scrapeSpecificButton.Size = New-Object System.Drawing.Size(150, 30)
$scrapeSpecificButton.Text = "Scrape Selected Game"
$scrapeSpecificButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$scrapeSpecificButton.ForeColor = [System.Drawing.Color]::White
$scrapeSpecificButton.FlatStyle = 'Flat'
$backImageScraperTab.Controls.Add($scrapeSpecificButton)

$scrapeAllButton = New-Object System.Windows.Forms.Button
$scrapeAllButton.Location = New-Object System.Drawing.Point(170, 210)
$scrapeAllButton.Size = New-Object System.Drawing.Size(150, 30)
$scrapeAllButton.Text = "Scrape All Games"
$scrapeAllButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$scrapeAllButton.ForeColor = [System.Drawing.Color]::White
$scrapeAllButton.FlatStyle = 'Flat'
$backImageScraperTab.Controls.Add($scrapeAllButton)

$listGamesButton = New-Object System.Windows.Forms.Button
$listGamesButton.Location = New-Object System.Drawing.Point(330, 210)
$listGamesButton.Size = New-Object System.Drawing.Size(120, 30)
$listGamesButton.Text = "List Games"
$listGamesButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$listGamesButton.ForeColor = [System.Drawing.Color]::White
$listGamesButton.FlatStyle = 'Flat'
$backImageScraperTab.Controls.Add($listGamesButton)

# Status and Results
$backStatusLabel = New-Object System.Windows.Forms.Label
$backStatusLabel.Location = New-Object System.Drawing.Point(10, 250)
$backStatusLabel.Size = New-Object System.Drawing.Size(680, 20)
$backStatusLabel.Text = "Ready to scrape back images..."
$backStatusLabel.ForeColor = [System.Drawing.Color]::Green
$backImageScraperTab.Controls.Add($backStatusLabel)

$backResultsTextBox = New-Object System.Windows.Forms.TextBox
$backResultsTextBox.Location = New-Object System.Drawing.Point(10, 280)
$backResultsTextBox.Size = New-Object System.Drawing.Size(680, 150)
$backResultsTextBox.BackColor = [System.Drawing.Color]::FromArgb(30, 30, 30)
$backResultsTextBox.ForeColor = [System.Drawing.Color]::White
$backResultsTextBox.BorderStyle = 'FixedSingle'
$backResultsTextBox.Multiline = $true
$backResultsTextBox.ScrollBars = 'Vertical'
$backResultsTextBox.ReadOnly = $true
$backImageScraperTab.Controls.Add($backResultsTextBox)

# Back Image Scraper Event Handlers
$backOutputButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        $folderBrowser.Description = "Select output directory for back images"
    
        if ($folderBrowser.ShowDialog() -eq 'OK') {
            $backOutputTextBox.Text = $folderBrowser.SelectedPath
        }
    })

$scrapeSpecificButton.Add_Click({
        $selectedGame = $backGameCombo.SelectedItem
        if ($selectedGame -eq '-- All Games --') {
            $backStatusLabel.Text = "Error: Please select a specific game"
            $backStatusLabel.ForeColor = [System.Drawing.Color]::Red
            return
        }
    
        $backStatusLabel.Text = "Scraping back image for $selectedGame..."
        $backStatusLabel.ForeColor = [System.Drawing.Color]::Blue
        $form.Refresh()
    
        $outputDir = $backOutputTextBox.Text
        if (-not $outputDir) {
            $outputDir = "out/back"
        }
    
        $pythonArgs = "back_image_scraper.py scrape --game `"$selectedGame`" --output-dir `"$outputDir`""
    
        $backResultsTextBox.Text = "Running: python $pythonArgs`n`n"
        $form.Refresh()
    
        try {
            $processInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processInfo.FileName = "python"
            $processInfo.Arguments = $pythonArgs
            $processInfo.RedirectStandardOutput = $true
            $processInfo.RedirectStandardError = $true
            $processInfo.UseShellExecute = $false
            $processInfo.CreateNoWindow = $true
        
            $process = New-Object System.Diagnostics.Process
            $process.StartInfo = $processInfo
            $process.Start() | Out-Null
        
            $output = $process.StandardOutput.ReadToEnd()
            $stdErr = $process.StandardError.ReadToEnd()
            $process.WaitForExit()
        
            $backResultsTextBox.Text += $output
            if ($stdErr) {
                $backResultsTextBox.Text += "`nErrors:`n$stdErr"
            }
        
            if ($process.ExitCode -eq 0) {
                $backStatusLabel.Text = "Successfully scraped $selectedGame back image"
                $backStatusLabel.ForeColor = [System.Drawing.Color]::Green
            }
            else {
                $backStatusLabel.Text = "Error scraping $selectedGame back image"
                $backStatusLabel.ForeColor = [System.Drawing.Color]::Red
            }
        }
        catch {
            $backStatusLabel.Text = "Error running back image scraper: $($_.Exception.Message)"
            $backStatusLabel.ForeColor = [System.Drawing.Color]::Red
            $backResultsTextBox.Text += "`nError: $($_.Exception.Message)"
        }
    })

$scrapeAllButton.Add_Click({
        $backStatusLabel.Text = "Scraping back images for all games..."
        $backStatusLabel.ForeColor = [System.Drawing.Color]::Blue
        $form.Refresh()
    
        $outputDir = $backOutputTextBox.Text
        if (-not $outputDir) {
            $outputDir = "out/back"
        }
    
        $pythonArgs = "back_image_scraper.py scrape --all-games --output-dir `"$outputDir`" --create-index"
    
        $backResultsTextBox.Text = "Running: python $pythonArgs`n`n"
        $form.Refresh()
    
        try {
            $processInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processInfo.FileName = "python"
            $processInfo.Arguments = $pythonArgs
            $processInfo.RedirectStandardOutput = $true
            $processInfo.RedirectStandardError = $true
            $processInfo.UseShellExecute = $false
            $processInfo.CreateNoWindow = $true
        
            $process = New-Object System.Diagnostics.Process
            $process.StartInfo = $processInfo
            $process.Start() | Out-Null
        
            $output = $process.StandardOutput.ReadToEnd()
            $stdErr = $process.StandardError.ReadToEnd()
            $process.WaitForExit()
        
            $backResultsTextBox.Text += $output
            if ($stdErr) {
                $backResultsTextBox.Text += "`nErrors:`n$stdErr"
            }
        
            if ($process.ExitCode -eq 0) {
                $backStatusLabel.Text = "Successfully scraped all back images"
                $backStatusLabel.ForeColor = [System.Drawing.Color]::Green
            }
            else {
                $backStatusLabel.Text = "Error scraping back images"
                $backStatusLabel.ForeColor = [System.Drawing.Color]::Red
            }
        }
        catch {
            $backStatusLabel.Text = "Error running back image scraper: $($_.Exception.Message)"
            $backStatusLabel.ForeColor = [System.Drawing.Color]::Red
            $backResultsTextBox.Text += "`nError: $($_.Exception.Message)"
        }
    })

$listGamesButton.Add_Click({
        $backStatusLabel.Text = "Listing supported games..."
        $backStatusLabel.ForeColor = [System.Drawing.Color]::Blue
        $form.Refresh()
    
        $pythonArgs = "back_image_scraper.py list-games"
    
        $backResultsTextBox.Text = "Running: python $pythonArgs`n`n"
        $form.Refresh()
    
        try {
            $processInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processInfo.FileName = "python"
            $processInfo.Arguments = $pythonArgs
            $processInfo.RedirectStandardOutput = $true
            $processInfo.RedirectStandardError = $true
            $processInfo.UseShellExecute = $false
            $processInfo.CreateNoWindow = $true
        
            $process = New-Object System.Diagnostics.Process
            $process.StartInfo = $processInfo
            $process.Start() | Out-Null
        
            $output = $process.StandardOutput.ReadToEnd()
            $stdErr = $process.StandardError.ReadToEnd()
            $process.WaitForExit()
        
            $backResultsTextBox.Text += $output
            if ($stdErr) {
                $backResultsTextBox.Text += "`nErrors:`n$stdErr"
            }
        
            $backStatusLabel.Text = "Games list updated"
            $backStatusLabel.ForeColor = [System.Drawing.Color]::Green
        }
        catch {
            $backStatusLabel.Text = "Error listing games: $($_.Exception.Message)"
            $backStatusLabel.ForeColor = [System.Drawing.Color]::Red
            $backResultsTextBox.Text += "`nError: $($_.Exception.Message)"
        }
    })

# ===== TAB 5: DECKLISTS =====
$decklistsTab = New-Object System.Windows.Forms.TabPage
$decklistsTab.Text = "Decklists"
$decklistsTab.BackColor = [System.Drawing.Color]::FromArgb(37, 37, 38)
$mainTabControl.Controls.Add($decklistsTab)

# ===== TAB 6: PLUGIN OPTIONS =====
[void](New-PluginOptionsTab -tabControl $mainTabControl)

# Add tab change event handler to refresh plugin list and options
$mainTabControl.Add_SelectedIndexChanged({
        if ($mainTabControl.SelectedTab.Text -eq "Plugin Options") {
            # Refresh using the improved function from plugin_options_tab.ps1
            if (Get-Command Update-PluginList -ErrorAction SilentlyContinue) {
                Update-PluginList
                Update-PluginStats
            }
        }
        # Also always refresh the main plugin selection list
        Update-MainPluginList
    })

# Decklists Title
$decklistsTitleLabel = New-Object System.Windows.Forms.Label
$decklistsTitleLabel.Location = New-Object System.Drawing.Point(10, 10)
$decklistsTitleLabel.Size = New-Object System.Drawing.Size(680, 25)
$decklistsTitleLabel.Text = "Supported Decklist Formats & Websites"
$decklistsTitleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$decklistsTitleLabel.ForeColor = [System.Drawing.Color]::White
$decklistsTab.Controls.Add($decklistsTitleLabel)

# Create a scrollable panel for the decklist info
$decklistsPanel = New-Object System.Windows.Forms.Panel
$decklistsPanel.Location = New-Object System.Drawing.Point(10, 40)
$decklistsPanel.Size = New-Object System.Drawing.Size(680, 380)
$decklistsPanel.AutoScroll = $true
$decklistsPanel.BackColor = [System.Drawing.Color]::FromArgb(30, 30, 30)
$decklistsPanel.BorderStyle = 'FixedSingle'
$decklistsTab.Controls.Add($decklistsPanel)

# Decklist information for each game with clickable links (up to 3 per game)
$yPos = 10
$games = @(
    @{Name = "Magic: The Gathering"; Formats = "MTGA, MTGO, TappedOut, Moxfield, Archidekt, Scryfall JSON"; Links = @(
            @{Url = "https://moxfield.com"; Text = "Moxfield" }
            @{Url = "https://www.archidekt.com/"; Text = "Archidekt" }
            @{Url = "https://tappedout.net/"; Text = "TappedOut" }
        )
    }
    @{Name = "Yu-Gi-Oh!"; Formats = "YDK, YDKE"; Links = @(
            @{Url = "https://ygoprodeck.com/deck-builder/"; Text = "YGOPRODeck Builder" }
            @{Url = "https://www.duellinksmeta.com/deck-tester"; Text = "Duel Links Meta" }
        )
    }
    @{Name = "Altered"; Formats = "Ajordat"; Links = @(
            @{Url = "https://www.altered.gg/"; Text = "Altered Official Site" }
        )
    }
    @{Name = "Digimon"; Formats = "TTS, Digimoncard.io, Digimoncard.dev, Digimoncard.app, DigimonMeta, Untap"; Links = @(
            @{Url = "https://digimonmeta.com/deck-builder/"; Text = "DigimonMeta" }
            @{Url = "https://digimoncard.io/"; Text = "Digimoncard.io" }
            @{Url = "https://digimoncard.dev/"; Text = "Digimoncard.dev" }
        )
    }
    @{Name = "Dragon Ball Super"; Formats = "DeckPlanet"; Links = @(
            @{Url = "https://www.dbs-deckplanet.com/"; Text = "DBS DeckPlanet" }
        )
    }
    @{Name = "Flesh and Blood"; Formats = "Fabrary"; Links = @(
            @{Url = "https://fabrary.net/"; Text = "Fabrary" }
            @{Url = "https://fabtcg.com/"; Text = "Official Site" }
        )
    }
    @{Name = "Grand Archive"; Formats = "Omnideck"; Links = @(
            @{Url = "https://www.gatcg.com/"; Text = "Grand Archive Official" }
            @{Url = "https://index.gatcg.com/"; Text = "GA Index" }
        )
    }
    @{Name = "Gundam"; Formats = "DeckPlanet, Limitless, Egman, ExBurst"; Links = @(
            @{Url = "https://gundamcardgame.com/deckbuilder/"; Text = "Official Deck Builder" }
            @{Url = "https://play.limitlesstcg.com/gundam"; Text = "Limitless" }
        )
    }
    @{Name = "Lorcana"; Formats = "Dreamborn"; Links = @(
            @{Url = "https://dreamborn.ink/"; Text = "Dreamborn" }
            @{Url = "https://www.disneylorcana.com/"; Text = "Official Site" }
        )
    }
    @{Name = "Netrunner"; Formats = "Text, bbCode, Markdown, Plain Text, Jinteki"; Links = @(
            @{Url = "https://jinteki.net/"; Text = "Jinteki.net" }
            @{Url = "https://netrunnerdb.com/"; Text = "NetrunnerDB" }
        )
    }
    @{Name = "One Piece"; Formats = "OPTCG Simulator, Egman"; Links = @(
            @{Url = "https://onepiece-cardgame.com/"; Text = "Official Site" }
            @{Url = "https://onepiecetopdecks.com/"; Text = "One Piece Top Decks" }
        )
    }
    @{Name = "Riftbound"; Formats = "Tabletop Simulator, Pixelborn, Piltover Archive"; Links = @(
            @{Url = "https://www.riftbound.com/"; Text = "Riftbound Official" }
        )
    }
    @{Name = "Star Wars Unlimited"; Formats = "SWUDB JSON, Melee, Picklist"; Links = @(
            @{Url = "https://www.swudb.com/"; Text = "SWUDB" }
            @{Url = "https://play.limitlesstcg.com/swu"; Text = "Limitless" }
        )
    }
)

foreach ($game in $games) {
    # Game name
    $gameLabel = New-Object System.Windows.Forms.Label
    $gameLabel.Location = New-Object System.Drawing.Point(10, $yPos)
    $gameLabel.Size = New-Object System.Drawing.Size(640, 20)
    $gameLabel.Text = $game.Name
    $gameLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $gameLabel.ForeColor = [System.Drawing.Color]::FromArgb(100, 181, 246)
    $decklistsPanel.Controls.Add($gameLabel)
    $yPos += 22
    
    # Formats
    $formatsLabel = New-Object System.Windows.Forms.Label
    $formatsLabel.Location = New-Object System.Drawing.Point(20, $yPos)
    $formatsLabel.Size = New-Object System.Drawing.Size(620, 20)
    $formatsLabel.Text = "Formats: $($game.Formats)"
    $formatsLabel.ForeColor = [System.Drawing.Color]::LightGray
    $decklistsPanel.Controls.Add($formatsLabel)
    $yPos += 22
    
    # Clickable links (up to 3)
    foreach ($link in $game.Links) {
        $linkLabel = New-Object System.Windows.Forms.LinkLabel
        $linkLabel.Location = New-Object System.Drawing.Point(20, $yPos)
        $linkLabel.Size = New-Object System.Drawing.Size(620, 20)
        $linkLabel.Text = ">> $($link.Text)"
        $linkLabel.LinkColor = [System.Drawing.Color]::FromArgb(100, 181, 246)
        $linkLabel.ActiveLinkColor = [System.Drawing.Color]::FromArgb(144, 202, 249)
        $linkLabel.VisitedLinkColor = [System.Drawing.Color]::FromArgb(79, 195, 247)
        $linkLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
        $linkLabel.Tag = $link.Url
        $linkLabel.Add_LinkClicked({
                param($Source, $e)
                Start-Process $Source.Tag
            })
        $decklistsPanel.Controls.Add($linkLabel)
        $yPos += 20
    }
    
    $yPos += 10
}

# Card Size
$cardSizeLabel = New-Object System.Windows.Forms.Label
$cardSizeLabel.Location = New-Object System.Drawing.Point(10, 12)
$cardSizeLabel.Size = New-Object System.Drawing.Size(120, 18)
$cardSizeLabel.Text = "Card Size:"
$cardSizeLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($cardSizeLabel)

$cardSizeCombo = New-Object System.Windows.Forms.ComboBox
$cardSizeCombo.Location = New-Object System.Drawing.Point(140, 10)
$cardSizeCombo.Size = New-Object System.Drawing.Size(150, 25)
$cardSizeCombo.DropDownStyle = 'DropDownList'
$cardSizeCombo.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$cardSizeCombo.ForeColor = [System.Drawing.Color]::White
$cardSizeCombo.FlatStyle = 'Flat'
$cardSizeCombo.Items.AddRange(@('standard', 'standard_double', 'japanese', 'poker', 'poker_half', 'bridge', 'bridge_square', 'tarot', 'domino', 'domino_square'))
$cardSizeCombo.SelectedIndex = 0
$pdfOptionsTab.Controls.Add($cardSizeCombo)

# Paper Size
$paperSizeLabel = New-Object System.Windows.Forms.Label
$paperSizeLabel.Location = New-Object System.Drawing.Point(310, 12)
$paperSizeLabel.Size = New-Object System.Drawing.Size(80, 18)
$paperSizeLabel.Text = "Paper Size:"
$paperSizeLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($paperSizeLabel)

$paperSizeCombo = New-Object System.Windows.Forms.ComboBox
$paperSizeCombo.Location = New-Object System.Drawing.Point(400, 10)
$paperSizeCombo.Size = New-Object System.Drawing.Size(130, 25)
$paperSizeCombo.DropDownStyle = 'DropDownList'
$paperSizeCombo.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$paperSizeCombo.ForeColor = [System.Drawing.Color]::White
$paperSizeCombo.FlatStyle = 'Flat'
$paperSizeCombo.Items.AddRange(@('letter', 'tabloid', 'a4', 'a3', 'archb'))
$paperSizeCombo.SelectedIndex = 0
$pdfOptionsTab.Controls.Add($paperSizeCombo)

# Registration
$registrationLabel = New-Object System.Windows.Forms.Label
$registrationLabel.Location = New-Object System.Drawing.Point(10, 40)
$registrationLabel.Size = New-Object System.Drawing.Size(120, 18)
$registrationLabel.Text = "Registration:"
$registrationLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($registrationLabel)

$registrationCombo = New-Object System.Windows.Forms.ComboBox
$registrationCombo.Location = New-Object System.Drawing.Point(140, 38)
$registrationCombo.Size = New-Object System.Drawing.Size(80, 25)
$registrationCombo.DropDownStyle = 'DropDownList'
$registrationCombo.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$registrationCombo.ForeColor = [System.Drawing.Color]::White
$registrationCombo.FlatStyle = 'Flat'
$registrationCombo.Items.AddRange(@('3', '4'))
$registrationCombo.SelectedIndex = 0
$pdfOptionsTab.Controls.Add($registrationCombo)

# Only Fronts
$onlyFrontsCheck = New-Object System.Windows.Forms.CheckBox
$onlyFrontsCheck.Location = New-Object System.Drawing.Point(240, 40)
$onlyFrontsCheck.Size = New-Object System.Drawing.Size(150, 18)
$onlyFrontsCheck.Text = "Only Fronts (no backs)"
$onlyFrontsCheck.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($onlyFrontsCheck)

# Output Images
$outputImagesCheck = New-Object System.Windows.Forms.CheckBox
$outputImagesCheck.Location = New-Object System.Drawing.Point(400, 40)
$outputImagesCheck.Size = New-Object System.Drawing.Size(130, 18)
$outputImagesCheck.Text = "Output as Images"
$outputImagesCheck.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($outputImagesCheck)

# PDF Name
$pdfNameLabel = New-Object System.Windows.Forms.Label
$pdfNameLabel.Location = New-Object System.Drawing.Point(10, 65)
$pdfNameLabel.Size = New-Object System.Drawing.Size(120, 18)
$pdfNameLabel.Text = "PDF Label (optional):"
$pdfNameLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($pdfNameLabel)

$pdfNameTextBox = New-Object System.Windows.Forms.TextBox
$pdfNameTextBox.Location = New-Object System.Drawing.Point(140, 63)
$pdfNameTextBox.Size = New-Object System.Drawing.Size(350, 22)
$pdfNameTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$pdfNameTextBox.ForeColor = [System.Drawing.Color]::White
$pdfNameTextBox.BorderStyle = 'FixedSingle'
$pdfOptionsTab.Controls.Add($pdfNameTextBox)

# Output Path
$outputPathLabel = New-Object System.Windows.Forms.Label
$outputPathLabel.Location = New-Object System.Drawing.Point(10, 93)
$outputPathLabel.Size = New-Object System.Drawing.Size(120, 18)
$outputPathLabel.Text = "Output Path (optional):"
$outputPathLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($outputPathLabel)

$outputPathTextBox = New-Object System.Windows.Forms.TextBox
$outputPathTextBox.Location = New-Object System.Drawing.Point(140, 91)
$outputPathTextBox.Size = New-Object System.Drawing.Size(350, 22)
$outputPathTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$outputPathTextBox.ForeColor = [System.Drawing.Color]::White
$outputPathTextBox.BorderStyle = 'FixedSingle'
$outputPathTextBox.ReadOnly = $true
$pdfOptionsTab.Controls.Add($outputPathTextBox)

$outputPathButton = New-Object System.Windows.Forms.Button
$outputPathButton.Location = New-Object System.Drawing.Point(500, 90)
$outputPathButton.Size = New-Object System.Drawing.Size(80, 23)
$outputPathButton.Text = "Browse..."
$outputPathButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$outputPathButton.ForeColor = [System.Drawing.Color]::White
$outputPathButton.FlatStyle = 'Flat'
$pdfOptionsTab.Controls.Add($outputPathButton)

$clearOutputPathButton = New-Object System.Windows.Forms.Button
$clearOutputPathButton.Location = New-Object System.Drawing.Point(590, 90)
$clearOutputPathButton.Size = New-Object System.Drawing.Size(80, 23)
$clearOutputPathButton.Text = "Clear"
$clearOutputPathButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
$clearOutputPathButton.ForeColor = [System.Drawing.Color]::White
$clearOutputPathButton.FlatStyle = 'Flat'
$pdfOptionsTab.Controls.Add($clearOutputPathButton)

# PPI
$ppiLabel = New-Object System.Windows.Forms.Label
$ppiLabel.Location = New-Object System.Drawing.Point(10, 125)
$ppiLabel.Size = New-Object System.Drawing.Size(120, 18)
$ppiLabel.Text = "PPI (Pixels/Inch):"
$ppiLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($ppiLabel)

$ppiTextBox = New-Object System.Windows.Forms.TextBox
$ppiTextBox.Location = New-Object System.Drawing.Point(140, 123)
$ppiTextBox.Size = New-Object System.Drawing.Size(80, 22)
$ppiTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$ppiTextBox.ForeColor = [System.Drawing.Color]::White
$ppiTextBox.BorderStyle = 'FixedSingle'
$ppiTextBox.Text = "300"
$pdfOptionsTab.Controls.Add($ppiTextBox)

# Quality
$qualityLabel = New-Object System.Windows.Forms.Label
$qualityLabel.Location = New-Object System.Drawing.Point(240, 125)
$qualityLabel.Size = New-Object System.Drawing.Size(100, 18)
$qualityLabel.Text = "Quality (0-100):"
$qualityLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($qualityLabel)

$qualityTextBox = New-Object System.Windows.Forms.TextBox
$qualityTextBox.Location = New-Object System.Drawing.Point(350, 123)
$qualityTextBox.Size = New-Object System.Drawing.Size(80, 22)
$qualityTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$qualityTextBox.ForeColor = [System.Drawing.Color]::White
$qualityTextBox.BorderStyle = 'FixedSingle'
$qualityTextBox.Text = "100"
$pdfOptionsTab.Controls.Add($qualityTextBox)

# Crop
$cropLabel = New-Object System.Windows.Forms.Label
$cropLabel.Location = New-Object System.Drawing.Point(10, 153)
$cropLabel.Size = New-Object System.Drawing.Size(120, 18)
$cropLabel.Text = "Crop (e.g. 3mm):"
$cropLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($cropLabel)

$cropTextBox = New-Object System.Windows.Forms.TextBox
$cropTextBox.Location = New-Object System.Drawing.Point(140, 151)
$cropTextBox.Size = New-Object System.Drawing.Size(80, 22)
$cropTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$cropTextBox.ForeColor = [System.Drawing.Color]::White
$cropTextBox.BorderStyle = 'FixedSingle'
$pdfOptionsTab.Controls.Add($cropTextBox)

# Extend Corners
$extendCornersLabel = New-Object System.Windows.Forms.Label
$extendCornersLabel.Location = New-Object System.Drawing.Point(240, 153)
$extendCornersLabel.Size = New-Object System.Drawing.Size(100, 18)
$extendCornersLabel.Text = "Extend Corners:"
$extendCornersLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($extendCornersLabel)

$extendCornersTextBox = New-Object System.Windows.Forms.TextBox
$extendCornersTextBox.Location = New-Object System.Drawing.Point(350, 151)
$extendCornersTextBox.Size = New-Object System.Drawing.Size(80, 22)
$extendCornersTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$extendCornersTextBox.ForeColor = [System.Drawing.Color]::White
$extendCornersTextBox.BorderStyle = 'FixedSingle'
$extendCornersTextBox.Text = "0"
$pdfOptionsTab.Controls.Add($extendCornersTextBox)

# Skip Card Index
$skipLabel = New-Object System.Windows.Forms.Label
$skipLabel.Location = New-Object System.Drawing.Point(10, 181)
$skipLabel.Size = New-Object System.Drawing.Size(120, 18)
$skipLabel.Text = "Skip Card Index:"
$skipLabel.ForeColor = [System.Drawing.Color]::White
$pdfOptionsTab.Controls.Add($skipLabel)

$skipTextBox = New-Object System.Windows.Forms.TextBox
$skipTextBox.Location = New-Object System.Drawing.Point(140, 179)
$skipTextBox.Size = New-Object System.Drawing.Size(80, 22)
$skipTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
$skipTextBox.ForeColor = [System.Drawing.Color]::White
$skipTextBox.BorderStyle = 'FixedSingle'
$pdfOptionsTab.Controls.Add($skipTextBox)

# Output path button handlers
$outputPathButton.Add_Click({
        $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
        $folderBrowser.Description = "Select output folder for PDFs"
    
        if ($script:outputPath -and (Test-Path $script:outputPath)) {
            $folderBrowser.SelectedPath = $script:outputPath
        }
    
        if ($folderBrowser.ShowDialog() -eq 'OK') {
            $script:outputPath = $folderBrowser.SelectedPath
            $outputPathTextBox.Text = $folderBrowser.SelectedPath
        
            # Save settings
            Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath -xOffset $xOffsetTextBox.Text -yOffset $yOffsetTextBox.Text -loadOffset $loadOffsetCheck.Checked -pluginOptions $script:pluginOptions
        
            $statusLabel.Text = "Output path set to: $($folderBrowser.SelectedPath)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Green
        }
    })

$clearOutputPathButton.Add_Click({
        $script:outputPath = ""
        $outputPathTextBox.Text = ""
    
        # Save settings
        Save-Settings -defaultDecklistFolders $script:defaultDecklistFolders -targetFolder $targetTextBox.Text -generalDecklistLocation $script:generalDecklistLocation -backImages $script:backImages -outputPath $script:outputPath
    
        $statusLabel.Text = "Output path cleared - will use default location"
        $statusLabel.ForeColor = [System.Drawing.Color]::Green
    })

# Load output path from settings
if ($script:outputPath) {
    $outputPathTextBox.Text = $script:outputPath
}

# Action Buttons (below main tabs)
$fetchCardsButton = New-Object System.Windows.Forms.Button
$fetchCardsButton.Location = New-Object System.Drawing.Point(10, 470)
$fetchCardsButton.Size = New-Object System.Drawing.Size(345, 32)
$fetchCardsButton.Text = "1. Fetch Card Images"
$fetchCardsButton.BackColor = [System.Drawing.Color]::FromArgb(0, 122, 204)
$fetchCardsButton.ForeColor = [System.Drawing.Color]::White
$fetchCardsButton.FlatStyle = 'Flat'
$form.Controls.Add($fetchCardsButton)

$createPdfButton = New-Object System.Windows.Forms.Button
$createPdfButton.Location = New-Object System.Drawing.Point(365, 470)
$createPdfButton.Size = New-Object System.Drawing.Size(355, 32)
$createPdfButton.Text = "2. Create PDF"
$createPdfButton.BackColor = [System.Drawing.Color]::FromArgb(106, 153, 85)
$createPdfButton.ForeColor = [System.Drawing.Color]::White
$createPdfButton.FlatStyle = 'Flat'
$form.Controls.Add($createPdfButton)

# Clear Game Folders Button
$clearFoldersButton = New-Object System.Windows.Forms.Button
$clearFoldersButton.Location = New-Object System.Drawing.Point(10, 507)
$clearFoldersButton.Size = New-Object System.Drawing.Size(710, 25)
$clearFoldersButton.Text = "Clear Game Folders (front, back, double_sided, output, decklist)"
$clearFoldersButton.BackColor = [System.Drawing.Color]::FromArgb(192, 57, 43)
$clearFoldersButton.ForeColor = [System.Drawing.Color]::White
$clearFoldersButton.FlatStyle = 'Flat'
$clearFoldersButton.Font = New-Object System.Drawing.Font("Segoe UI", 8)
$form.Controls.Add($clearFoldersButton)

# Status Label (now a scrollable textbox)
$statusLabel = New-Object System.Windows.Forms.TextBox
$statusLabel.Location = New-Object System.Drawing.Point(10, 537)
$statusLabel.Size = New-Object System.Drawing.Size(710, 40)
$statusLabel.Text = "Ready - Select a plugin and decklist to begin"
$statusLabel.BackColor = [System.Drawing.Color]::FromArgb(30, 30, 30)
$statusLabel.ForeColor = [System.Drawing.Color]::White
$statusLabel.BorderStyle = 'FixedSingle'
$statusLabel.Multiline = $true
$statusLabel.ScrollBars = 'Vertical'
$statusLabel.ReadOnly = $true
$statusLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$form.Controls.Add($statusLabel)

# Command Preview (now a scrollable textbox)
$commandLabel = New-Object System.Windows.Forms.TextBox
$commandLabel.Location = New-Object System.Drawing.Point(10, 582)
$commandLabel.Size = New-Object System.Drawing.Size(710, 35)
$commandLabel.Text = ""
$commandLabel.BackColor = [System.Drawing.Color]::FromArgb(30, 30, 30)
$commandLabel.ForeColor = [System.Drawing.Color]::LightGreen
$commandLabel.BorderStyle = 'FixedSingle'
$commandLabel.Multiline = $true
$commandLabel.ScrollBars = 'Vertical'
$commandLabel.ReadOnly = $true
$commandLabel.Font = New-Object System.Drawing.Font("Consolas", 8)
$commandLabel.WordWrap = $true
$form.Controls.Add($commandLabel)

# Helper function to clean up old decklist files
function Remove-OldDecklists {
    param([string]$targetFolder)
    
    $decklistDir = Join-Path $targetFolder "out\decklist"
    if (Test-Path $decklistDir) {
        try {
            Get-ChildItem -Path $decklistDir -File | Remove-Item -Force -ErrorAction SilentlyContinue
            return $true
        }
        catch {
            return $false
        }
    }
    return $true
}

# Fetch Cards Button Click
$fetchCardsButton.Add_Click({
        if (-not $script:selectedFile) {
            $statusLabel.Text = "Error: Please select a decklist file first"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            return
        }
    
        $script:targetFolder = $targetTextBox.Text
        if (-not $script:targetFolder) {
            $statusLabel.Text = "Error: Please enter target folder path"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            return
        }
    
        if (-not (Test-Path $script:targetFolder)) {
            $statusLabel.Text = "Error: Target folder does not exist"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            return
        }
    
        try {
            # Clear out old card images before fetching new ones
            $statusLabel.Text = "Clearing old card images..."
            $statusLabel.ForeColor = [System.Drawing.Color]::Blue
            $form.Refresh()
        
            $foldersToClean = @(
                "out\front",
                "out\back",
                "out\double_sided"
            )
        
            foreach ($folder in $foldersToClean) {
                $fullPath = Join-Path $script:targetFolder $folder
                if (Test-Path $fullPath) {
                    try {
                        Get-ChildItem -Path $fullPath -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
                    }
                    catch {
                        # Continue even if some files can't be deleted
                    }
                }
            }
        
            # Clean up any old decklist files
            $statusLabel.Text = "Cleaning up old decklists..."
            $statusLabel.ForeColor = [System.Drawing.Color]::Blue
            $form.Refresh()
        
            Remove-OldDecklists -targetFolder $script:targetFolder
        
            $fileName = Split-Path $script:selectedFile -Leaf
            # Save the base name for PDF renaming later
            $script:decklistBaseName = [System.IO.Path]::GetFileNameWithoutExtension($script:selectedFile)
        
            # Create out/decklist directory if it doesn't exist
            $decklistDir = Join-Path $script:targetFolder "out\decklist"
            if (-not (Test-Path $decklistDir)) {
                New-Item -ItemType Directory -Path $decklistDir -Force | Out-Null
            }
        
            $destination = Join-Path $decklistDir $fileName
            Copy-Item -Path $script:selectedFile -Destination $destination -Force
            $statusLabel.Text = "File copied. Now fetching card images..."
            $statusLabel.ForeColor = [System.Drawing.Color]::Blue
            $form.Refresh()
        }
        catch {
            $statusLabel.Text = "Error: Failed to copy file`n$($_.Exception.Message)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            return
        }
    
        # Now fetch the cards
        if (-not $script:selectedFile) {
            $statusLabel.Text = "Error: Please select a decklist file first"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            return
        }

        # Determine which plugin to use
        $selectedGame = $pluginCombo.SelectedItem
        $installRoot = Split-Path -Parent $PSScriptRoot
        
        # Use the central plugin manager to resolve the CLI script
        $cliScript = Get-PluginCLIScript -pluginName $selectedGame -installRoot $installRoot
        
        if ($null -eq $cliScript) {
            $statusLabel.Text = "Error: Could not find CLI script for plugin '$selectedGame'"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            return
        }

        # Determine the plugin folder name for relative paths
        $pluginFolder = Split-Path (Split-Path $cliScript -Parent) -Leaf
    
        $script:targetFolder = $targetTextBox.Text
        if (-not $script:targetFolder) {
            $statusLabel.Text = "Error: Please enter target folder path"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            return
        }
    
        try {
            $statusLabel.Text = "Running script... Please wait"
            $statusLabel.ForeColor = [System.Drawing.Color]::Blue
            $form.Refresh()
        
            # Check if venv exists - always base on the folder containing this GUI script
            $installRoot = Split-Path -Parent $PSScriptRoot
            $venvPath = Join-Path $installRoot "venv"
            $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
        
            if (-not (Test-Path $activateScript)) {
                $statusLabel.Text = "Error: Virtual environment not found at $venvPath`nPlease run the installation instructions first"
                $statusLabel.ForeColor = [System.Drawing.Color]::Red
                return
            }
        
            # Build command based on plugin
            $fileName = Split-Path $script:selectedFile -Leaf
            $decklistDir = Join-Path $script:targetFolder "out\decklist"
            $decklistFullPath = Join-Path $decklistDir $fileName
            $decklistPath = $decklistFullPath -replace '\\', '/'  # Use forward slashes for Python compatibility (used by some plugins)
            $plugin = $pluginCombo.SelectedItem
        
            # Check if a valid plugin is selected
            if ($plugin -eq '-- Select a Game Plugin --') {
                $statusLabel.Text = "Error: Please select a game plugin first"
                $statusLabel.ForeColor = [System.Drawing.Color]::Red
                return
            }
        
            $format = $formatCombo.SelectedItem
        
            $pythonArgs = ""
        
            # Dynamic plugin execution
            if ($pluginFolder -eq "ccgtrader") {
                # CCGTrader Universal Plugin
                if ($script:selectedFile.EndsWith(".json")) {
                    $pythonArgs = "$cliScript load-collection --input-file `"$($script:selectedFile)`" --fetch-images --output-dir `"$($script:targetFolder)\out\front`""
                }
                else {
                    $pythonArgs = "$cliScript import-decklist `"$($script:selectedFile)`" --game `"$selectedGame`" --output-dir `"$($script:targetFolder)\out\front`" --fetch-images"
                }
            }
            else {
                # Legacy/Specialized Plugins
                switch ($plugin) {
                    'Magic: The Gathering' {
                        # TappedOut uses MTGO format for the Python script
                        $actualFormat = if ($format -eq 'tappedout') { 'mtgo' } else { $format }
                        # Use the actual deck file path so MTG plugin sees the real file (including .dek)
                        $pythonArgs = "plugins/mtg/fetch.py `"$($script:selectedFile)`" $actualFormat "
                        if ($mtgOption1.Checked) { $pythonArgs += "-i " }
                        if ($mtgOption2.Checked) { $pythonArgs += "--prefer_older_sets " }
                        if ($mtgOption3.Checked) { $pythonArgs += "--prefer_showcase " }
                        if ($mtgOption4.Checked) { $pythonArgs += "--prefer_extra_art " }
                        if ($preferSetTextBox.Text) { $pythonArgs += "-s $($preferSetTextBox.Text) " }
                    }
                    'Yu-Gi-Oh!' {
                        $pythonArgs = "plugins/yugioh/fetch.py `"$decklistPath`" $format "
                        if ($yugiohOption1.Checked) { $pythonArgs += "--ignore_art_ver " }
                        if ($yugiohOption2.Checked) { $pythonArgs += "--include_proxy " }
                        if ($yugiohOption3.Checked) { $pythonArgs += "--prefer_older_art " }
                        if ($yugiohOption4.Checked) { $pythonArgs += "--skip_errata " }
                    }
                    'Altered' {
                        $pythonArgs = "plugins/altered/fetch.py `"$decklistPath`" $format "
                    }
                    'Digimon' {
                        $pythonArgs = "plugins/digimon/fetch.py `"$decklistPath`" $format "
                    }
                    'Dragon Ball Super' {
                        $pythonArgs = "plugins/dbs/fetch.py `"$decklistPath`" $format "
                    }
                    'Flesh and Blood' {
                        $pythonArgs = "plugins/flesh_and_blood/fetch.py `"$decklistPath`" $format "
                    }
                    'Grand Archive' {
                        $pythonArgs = "plugins/grand_archive/fetch.py `"$decklistPath`" $format "
                    }
                    'Gundam' {
                        $pythonArgs = "plugins/gundam/fetch.py `"$decklistPath`" $format "
                    }
                    'Lorcana' {
                        $pythonArgs = "plugins/lorcana/fetch.py `"$decklistPath`" $format "
                    }
                    'Netrunner' {
                        $pythonArgs = "plugins/netrunner/fetch.py `"$decklistPath`" $format "
                        if ($fetchImagesCheck.Checked) { $pythonArgs += "--fetch-images " }
                    }
                    'One Piece' {
                        $pythonArgs = "plugins/one_piece/fetch.py `"$decklistPath`" $format "
                        if ($fetchImagesCheck.Checked) { $pythonArgs += "--fetch-images " }
                    }
                    'Riftbound' {
                        $pythonArgs = "plugins/riftbound/fetch.py `"$decklistPath`" $format "
                        if ($fetchImagesCheck.Checked) { $pythonArgs += "--fetch-images " }
                        if ($riftboundOption1.Checked) { $pythonArgs += "-e " }
                    }
                    'Star Wars Unlimited' {
                        $pythonArgs = "plugins/star_wars_unlimited/fetch.py `"$decklistPath`" $format "
                        if ($fetchImagesCheck.Checked) { $pythonArgs += "--fetch-images " }
                        if ($swuOption1.Checked) { $pythonArgs += "-h " }
                    }
                    'Cards Against Humanity' {
                        $pythonArgs = "plugins/cards_against_humanity/cah_cli.py `"$decklistPath`" $format "
                    }
                    'CCGTrader' {
                        # This case might be redundant if handled by the if block above, but kept for safety
                        $pythonArgs = "plugins/ccgtrader/ccgt_cli.py import-decklist `"$($script:selectedFile)`" --game `"$selectedGame`" --output-dir `"$($script:targetFolder)\out\front`" --fetch-images"
                    }
                    'CF Vanguard' {
                        $pythonArgs = "plugins/cfvanguard/cfv_cli.py "
                        if ($fetchImagesCheck.Checked) { $pythonArgs += "--fetch-images " }
                    }
                    'Fluxx' {
                        $pythonArgs = "plugins/fluxx/fluxx_cli.py `"$decklistPath`" $format "
                    }
                    'Force of Will' {
                        $pythonArgs = "plugins/force_of_will/fow_cli.py `"$decklistPath`" $format "
                    }
                    'Marvel Champions' {
                        $pythonArgs = "plugins/marvel_champions/mc_cli.py import-decklist `"$($script:selectedFile)`" --output-dir `"$($script:targetFolder)\out\front`" --fetch-images"
                    }
                    'MetaZoo' {
                        $pythonArgs = "plugins/metazoo/mz_cli.py `"$decklistPath`" $format "
                    }
                    'Munchkin' {
                        $pythonArgs = "plugins/munchkin/munchkin_cli.py `"$decklistPath`" $format "
                    }
                    'Pokemon' {
                        $pythonArgs = "plugins/Pokemon/pokemon_cli.py import-decklist `"$($script:selectedFile)`" --output-dir `"$($script:targetFolder)\out\front`" --fetch-images"
                    }
                    'Shadowverse Evolve' {
                        $pythonArgs = "plugins/shadowverse_evolve/sve_cli.py `"$decklistPath`" $format "
                    }
                    'Star Realms' {
                        $pythonArgs = "plugins/star_realms/sr_cli.py `"$decklistPath`" $format "
                    }
                    'Union Arena' {
                        $pythonArgs = "plugins/union_arena/ua_cli.py `"$decklistPath`" $format "
                    }
                    'Universus' {
                        $pythonArgs = "plugins/universus/uvs_cli.py `"$decklistPath`" $format "
                    }
                    'Weiss Schwarz' {
                        $pythonArgs = "plugins/weiss_schwarz/ws_cli.py `"$decklistPath`" $format "
                    }
                    default {
                        # Generic fallback logic
                        $standardCli = Join-Path $installRoot "plugins\$pluginFolder\$($pluginFolder)_cli.py"
                        $legacyFetch = Join-Path $installRoot "plugins\$pluginFolder\fetch.py"
                        
                        if (Test-Path $standardCli) {
                            # Use the new standard CLI
                            $pythonArgs = "plugins/$pluginFolder/$($pluginFolder)_cli.py import-decklist `"$($script:selectedFile)`" --output-dir `"$($script:targetFolder)\out\front`" --fetch-images"
                        }
                        elseif (Test-Path $legacyFetch) {
                            # Use legacy fetch.py
                            $actualFormat = if ($format) { $format } else { "simple" }
                            $pythonArgs = "plugins/$pluginFolder/fetch.py `"$decklistPath`" $actualFormat "
                            if ($fetchImagesCheck.Checked) { $pythonArgs += "--fetch-images " }
                        }
                        else {
                            # Fallback to CCGTrader CLI for any other game in the registry
                            $pythonArgs = "plugins/ccgtrader/ccgt_cli.py import-decklist `"$($script:selectedFile)`" --game `"$selectedGame`" --output-dir `"$($script:targetFolder)\out\front`" --fetch-images"
                        }
                    }
                }
            }

        
            $commandLabel.Text = "Command: python $pythonArgs"
        
            # Create a temporary script to activate venv and run command from the install root
            $tempScript = Join-Path $env:TEMP "run_silhouette.ps1"
            # Build the script line by line to avoid here-string issues
            "Set-Location '$installRoot'" | Out-File -FilePath $tempScript -Encoding UTF8
            "& '$activateScript'" | Out-File -FilePath $tempScript -Encoding UTF8 -Append
            "python $pythonArgs" | Out-File -FilePath $tempScript -Encoding UTF8 -Append
            "exit `$LASTEXITCODE" | Out-File -FilePath $tempScript -Encoding UTF8 -Append
        
            $result = Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $tempScript -Wait -PassThru -NoNewWindow
        
            # Temporarily keep the script for debugging - comment out the delete
            # Remove-Item $tempScript -ErrorAction SilentlyContinue
        
            if ($result.ExitCode -eq 0) {
                $statusLabel.Text = "Success: Card images fetched!`nReady to create PDF.`nTemp script: $tempScript"
                $statusLabel.ForeColor = [System.Drawing.Color]::Green
            }
            else {
                $statusLabel.Text = "Warning: Script exited with code $($result.ExitCode)`nTemp script: $tempScript"
                $statusLabel.ForeColor = [System.Drawing.Color]::Orange
            }
        }
        catch {
            $statusLabel.Text = "Error: Failed to run script`n$($_.Exception.Message)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
        }
    })

# Create PDF Button Click
$createPdfButton.Add_Click({
        # Always treat the folder containing this GUI script as the install root for PDF output
        $installRoot = Split-Path -Parent $PSScriptRoot
        $script:targetFolder = $installRoot
    
        try {
            $statusLabel.Text = "Creating PDF... Please wait"
            $statusLabel.ForeColor = [System.Drawing.Color]::Blue
            $form.Refresh()
        
            # Check if venv exists - always base on the folder containing this GUI script
            $installRoot = Split-Path -Parent $PSScriptRoot
            $venvPath = Join-Path $installRoot "venv"
            $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
        
            if (-not (Test-Path $activateScript)) {
                $statusLabel.Text = "Error: Virtual environment not found at $venvPath`nPlease run the installation instructions first"
                $statusLabel.ForeColor = [System.Drawing.Color]::Red
                return
            }
        
            # Build create_pdf.py command with options
            $pdfArgs = "src/create_pdf.py"
        
            # Basic options
            if ($cardSizeCombo.SelectedItem -ne 'standard') {
                $pdfArgs += " --card_size $($cardSizeCombo.SelectedItem)"
            }
            if ($paperSizeCombo.SelectedItem -ne 'letter') {
                $pdfArgs += " --paper_size $($paperSizeCombo.SelectedItem)"
            }
            if ($registrationCombo.SelectedItem -ne '3') {
                $pdfArgs += " --registration $($registrationCombo.SelectedItem)"
            }

            if (-not (Test-Path $script:targetFolder)) {
                $statusLabel.Text = "Error: Target folder does not exist"
                $statusLabel.ForeColor = [System.Drawing.Color]::Red
                return
            }
        
            try {
                $xOffset = 0.0
                $yOffset = 0.0
            
                if ($xOffsetTextBox.Text -and [double]::TryParse($xOffsetTextBox.Text, [ref]$xOffset)) {
                    # Successfully parsed X offset (can be fractional)
                }
                else {
                    $xOffset = 0.0
                }
            
                if ($yOffsetTextBox.Text -and [double]::TryParse($yOffsetTextBox.Text, [ref]$yOffset)) {
                    # Successfully parsed Y offset (can be fractional)
                }
                else {
                    $yOffset = 0.0
                }
            
                $dataDir = Join-Path $script:targetFolder "data"
                if (-not (Test-Path $dataDir)) {
                    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
                }
            
                # Create JSON with proper integer values (UTF8 without BOM)
                $offsetFile = Join-Path $dataDir "offset_data.json"
                $jsonContent = "{`"x_offset`":$xOffset,`"y_offset`":$yOffset}"
                $utf8NoBom = New-Object System.Text.UTF8Encoding $false
                [System.IO.File]::WriteAllText($offsetFile, $jsonContent, $utf8NoBom)
            }
            catch {
                Write-Host "ERROR creating offset file: $($_.Exception.Message)"
            }
            if ($pdfNameTextBox.Text) {
                $pdfArgs += " --name `"$($pdfNameTextBox.Text)`""
            }
        
            # Handle back image - copy to game/back folder if specified
            $selectedGame = $pluginCombo.SelectedItem
            $currentPlugin = $selectedGame # Default fallback

            # Lookup actual plugin folder from registry if available
            $gamesIndexPath = Join-Path (Split-Path -Parent $PSScriptRoot) "data\games_index.json"
            if (Test-Path $gamesIndexPath) {
                try {
                    $jsonContent = Get-Content $gamesIndexPath -Raw -Encoding UTF8
                    $gamesIndex = $jsonContent | ConvertFrom-Json
                    if ($gamesIndex.PSObject.Properties.Name -contains $selectedGame) {
                        $currentPlugin = $gamesIndex.$selectedGame.plugin
                    }
                }
                catch {
                    Write-Host "Warning: Could not resolve plugin for game '$selectedGame'"
                }
            }
            if ($script:backImages.ContainsKey($currentPlugin) -and (Test-Path $script:backImages[$currentPlugin])) {
                $backImageFile = $script:backImages[$currentPlugin]
                $backDir = Join-Path $script:targetFolder "game\back"
            
                # Ensure back directory exists
                if (-not (Test-Path $backDir)) {
                    New-Item -ItemType Directory -Path $backDir -Force | Out-Null
                }
            
                # Clear existing back images and copy the selected one
                Get-ChildItem -Path $backDir -File | Remove-Item -Force -ErrorAction SilentlyContinue
                $backFileName = Split-Path $backImageFile -Leaf
                Copy-Item -Path $backImageFile -Destination (Join-Path $backDir $backFileName) -Force
            }
        
            # Output path: only pass a valid PDF file path to create_pdf.py
            if ($script:outputPath -and (Test-Path $script:outputPath)) {
                if (Test-Path $script:outputPath -PathType Container) {
                    # User selected a directory; append default file name
                    $outputPdf = Join-Path $script:outputPath "game.pdf"
                }
                else {
                    # User provided a full file path
                    $outputPdf = $script:outputPath
                }

                $pdfArgs += " --output_path `"$outputPdf`""
            }
        
            # Advanced options
            if ($ppiTextBox.Text -and $ppiTextBox.Text -ne '300') {
                $pdfArgs += " --ppi $($ppiTextBox.Text)"
            }
            if ($qualityTextBox.Text -and $qualityTextBox.Text -ne '100') {
                $pdfArgs += " --quality $($qualityTextBox.Text)"
            }
            if ($cropTextBox.Text) {
                $pdfArgs += " --crop $($cropTextBox.Text)"
            }
            if ($extendCornersTextBox.Text -and $extendCornersTextBox.Text -ne '0') {
                $pdfArgs += " --extend_corners $($extendCornersTextBox.Text)"
            }
            if ($skipTextBox.Text) {
                $pdfArgs += " --skip $($skipTextBox.Text)"
            }
        
            $commandLabel.Text = "Command: python $pdfArgs"
        
            # Create a temporary script to activate venv and run create_pdf.py from the install root
            $tempScript = Join-Path $env:TEMP "run_create_pdf.ps1"
            @"
Set-Location '$installRoot'
& '$activateScript'
python $pdfArgs
exit `$LASTEXITCODE
"@ | Out-File -FilePath $tempScript -Encoding UTF8
        
            $result = Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $tempScript -Wait -PassThru -NoNewWindow
        
            Remove-Item $tempScript -ErrorAction SilentlyContinue
        
            if ($result.ExitCode -eq 0) {
                # Wait for PDF compilation and offset application to complete
                Start-Sleep -Seconds 10
            
                # Rename PDF to match decklist filename
                $pdfPath = Join-Path $script:targetFolder "game\output\game.pdf"
                $finalPdfPath = $pdfPath
            
                if ($script:decklistBaseName -and (Test-Path $pdfPath)) {
                    try {
                        $outputDir = Join-Path $script:targetFolder "game\output"
                        $newPdfPath = Join-Path $outputDir "$script:decklistBaseName.pdf"
                    
                        Write-Host "[PDF] Renaming output PDF to match decklist name..." -ForegroundColor Cyan
                        Write-Host "[PDF] From: $pdfPath" -ForegroundColor DarkGray
                        Write-Host "[PDF] To:   $newPdfPath" -ForegroundColor DarkGray
                    
                        # Rename the PDF
                        Move-Item -Path $pdfPath -Destination $newPdfPath -Force
                        $finalPdfPath = $newPdfPath
                        Write-Host "[PDF] Rename successful." -ForegroundColor Green
                    
                        # GUI success indicator for rename
                        $statusLabel.Text = "Success: PDF renamed to $script:decklistBaseName.pdf"
                        $statusLabel.ForeColor = [System.Drawing.Color]::Green
                    }
                    catch {
                        Write-Host "[PDF] ERROR renaming PDF: $($_.Exception.Message)" -ForegroundColor Red
                    }
                }
                else {
                    Write-Host "[PDF] Rename skipped - decklistBaseName: $script:decklistBaseName, PDF exists: $(Test-Path $pdfPath)" -ForegroundColor Yellow
                }
            
                # Clean up decklist after successful PDF creation
                if ($script:selectedFile -and $script:originalPath) {
                    try {
                        $fileName = Split-Path $script:selectedFile -Leaf
                        $decklistDir = Join-Path $script:targetFolder "game\decklist"
                        $source = Join-Path $decklistDir $fileName
                    
                        if (Test-Path $source) {
                            $destination = Join-Path $script:originalPath $fileName
                            Move-Item -Path $source -Destination $destination -Force -ErrorAction SilentlyContinue
                        }
                    }
                    catch {
                        # Silently continue if cleanup fails
                    }
                }
            
                $statusLabel.Text = "Success: PDF created!`nLocation: $finalPdfPath`nDecklist cleaned up."
                $statusLabel.ForeColor = [System.Drawing.Color]::Green
            }
            else {
                $statusLabel.Text = "Error: PDF creation failed with exit code $($result.ExitCode)"
                $statusLabel.ForeColor = [System.Drawing.Color]::Red
            }
        }
        catch {
            $statusLabel.Text = "Error: Failed to create PDF`n$($_.Exception.Message)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
        }
    })


# Clear Game Folders Button Handler
$clearFoldersButton.Add_Click({
        # Derive root folder from this GUI script's location (silhouette-card-maker-tom)
        $scriptRoot = Split-Path -Parent $PSScriptRoot
        $script:targetFolder = $scriptRoot
    
        # Confirm with user
        $result = [System.Windows.Forms.MessageBox]::Show(
            "This will delete all files in the following folders:`n`n" +
            "- game/front`n" +
            "- game/back`n" +
            "- game/double_sided`n" +
            "- game/output`n" +
            "- game/decklist`n`n" +
            "Are you sure you want to continue?",
            "Confirm Clear Game Folders",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Warning
        )
    
        if ($result -ne [System.Windows.Forms.DialogResult]::Yes) {
            $statusLabel.Text = "Clear operation cancelled"
            $statusLabel.ForeColor = [System.Drawing.Color]::Orange
            return
        }
    
        try {
            $statusLabel.Text = "Clearing game folders... Please wait"
            $statusLabel.ForeColor = [System.Drawing.Color]::Blue
            Write-Host "[CLEAR] Clearing game folders under: $script:targetFolder" -ForegroundColor Cyan
            $form.Refresh()

            $foldersToClean = @(
                "out/front",
                "out/back",
                "out/double_sided",
                "out/output",
                "out/decklist"
            )

            foreach ($folder in $foldersToClean) {
                $fullPath = Join-Path $script:targetFolder $folder
                $folderDeleted = 0
                $folderErrors = @()

                if (-not (Test-Path $fullPath)) {
                    Write-Host "[CLEAR] ${folder}: folder not found." -ForegroundColor Yellow
                    continue
                }

                try {
                    # Delete all files (recursive)
                    $files = Get-ChildItem -LiteralPath $fullPath -File -Recurse -ErrorAction Stop
                    foreach ($file in $files) {
                        try {
                            if ($file.Attributes -band [System.IO.FileAttributes]::ReadOnly) {
                                $file.Attributes = $file.Attributes -bxor [System.IO.FileAttributes]::ReadOnly
                            }

                            Remove-Item -LiteralPath $file.FullName -Force -ErrorAction Stop
                            $folderDeleted++
                        }
                        catch {
                            $folderErrors += "Failed to delete file $($file.FullName): $($_.Exception.Message)"
                        }
                    }

                    # After deletion, check if folder still has any files
                    $remaining = Get-ChildItem -LiteralPath $fullPath -File -Recurse -ErrorAction SilentlyContinue
                    if (-not ($null -eq $remaining -or $remaining.Count -eq 0)) {
                        $folderErrors += "Folder not empty after clear: $fullPath"
                    }
                }
                catch {
                    $folderErrors += "Failed to clean folder ${fullPath}: $($_.Exception.Message)"
                }

                if ($folderDeleted -eq 0 -and $folderErrors.Count -eq 0) {
                    Write-Host "[CLEAR] ${folder}: nothing to clear." -ForegroundColor Cyan
                }
                elseif ($folderErrors.Count -eq 0) {
                    Write-Host "[CLEAR] ${folder}: $folderDeleted item(s) deleted. Success." -ForegroundColor Green
                }
                else {
                    Write-Host "[CLEAR] ${folder}: failed to delete some items. $folderDeleted item(s) deleted." -ForegroundColor Yellow
                }
            }

            # Simple overall GUI status based on whether any folder had issues
            if ($foldersToClean | ForEach-Object { $true }) {
                $statusLabel.Text = "Clear folders operation completed. See console for per-folder status."
                $statusLabel.ForeColor = [System.Drawing.Color]::Green
            }
        }
        catch {
            $statusLabel.Text = "Error: Failed to clear folders`n$($_.Exception.Message)"
            $statusLabel.ForeColor = [System.Drawing.Color]::Red
            Write-Host "[CLEAR] FATAL error clearing folders: $($_.Exception.Message)" -ForegroundColor Red
        }
    })

# Initialize systems
Initialize-PluginSystem
Update-MainPluginList

# Show the form
[void]$form.ShowDialog()
