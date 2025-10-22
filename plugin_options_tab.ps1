# Plugin Options Tab for Silhouette Card Maker GUI
# ================================================
# This module creates the Plugin Options tab for managing plugins

# Import plugin manager
. "$PSScriptRoot\plugin_manager.ps1"

# Create Plugin Options Tab
function Create-PluginOptionsTab {
    param([System.Windows.Forms.TabControl]$tabControl)
    
    # Create the Plugin Options tab
    $pluginOptionsTab = New-Object System.Windows.Forms.TabPage
    $pluginOptionsTab.Text = "Plugin Options"
    $pluginOptionsTab.BackColor = [System.Drawing.Color]::FromArgb(45, 45, 48)
    $tabControl.TabPages.Add($pluginOptionsTab)
    
    # Main container panel
    $mainPanel = New-Object System.Windows.Forms.Panel
    $mainPanel.Location = New-Object System.Drawing.Point(10, 10)
    $mainPanel.Size = New-Object System.Drawing.Size(720, 620)
    $mainPanel.BackColor = [System.Drawing.Color]::FromArgb(45, 45, 48)
    $mainPanel.AutoScroll = $true
    $pluginOptionsTab.Controls.Add($mainPanel)
    
    # Title
    $titleLabel = New-Object System.Windows.Forms.Label
    $titleLabel.Location = New-Object System.Drawing.Point(10, 10)
    $titleLabel.Size = New-Object System.Drawing.Size(700, 30)
    $titleLabel.Text = "Plugin Management"
    $titleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
    $titleLabel.ForeColor = [System.Drawing.Color]::White
    $mainPanel.Controls.Add($titleLabel)
    
    # Description
    $descLabel = New-Object System.Windows.Forms.Label
    $descLabel.Location = New-Object System.Drawing.Point(10, 45)
    $descLabel.Size = New-Object System.Drawing.Size(700, 40)
    $descLabel.Text = "Enable or disable plugins to customize your Silhouette Card Maker experience. Disabled plugins will not appear in the main interface."
    $descLabel.ForeColor = [System.Drawing.Color]::FromArgb(200, 200, 200)
    $descLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $mainPanel.Controls.Add($descLabel)
    
    # Statistics panel
    $statsPanel = New-Object System.Windows.Forms.Panel
    $statsPanel.Location = New-Object System.Drawing.Point(10, 95)
    $statsPanel.Size = New-Object System.Drawing.Size(700, 60)
    $statsPanel.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
    $statsPanel.BorderStyle = 'FixedSingle'
    $mainPanel.Controls.Add($statsPanel)
    
    # Statistics labels
    $statsTitleLabel = New-Object System.Windows.Forms.Label
    $statsTitleLabel.Location = New-Object System.Drawing.Point(10, 10)
    $statsTitleLabel.Size = New-Object System.Drawing.Size(100, 20)
    $statsTitleLabel.Text = "Statistics:"
    $statsTitleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
    $statsTitleLabel.ForeColor = [System.Drawing.Color]::White
    $statsPanel.Controls.Add($statsTitleLabel)
    
    $statsLabel = New-Object System.Windows.Forms.Label
    $statsLabel.Location = New-Object System.Drawing.Point(10, 30)
    $statsLabel.Size = New-Object System.Drawing.Size(680, 25)
    $statsLabel.Text = "Loading plugin statistics..."
    $statsLabel.ForeColor = [System.Drawing.Color]::FromArgb(200, 200, 200)
    $statsLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $statsPanel.Controls.Add($statsLabel)
    
    # Search box
    $searchLabel = New-Object System.Windows.Forms.Label
    $searchLabel.Location = New-Object System.Drawing.Point(10, 170)
    $searchLabel.Size = New-Object System.Drawing.Size(100, 20)
    $searchLabel.Text = "Search Plugins:"
    $searchLabel.ForeColor = [System.Drawing.Color]::White
    $mainPanel.Controls.Add($searchLabel)
    
    $searchTextBox = New-Object System.Windows.Forms.TextBox
    $searchTextBox.Location = New-Object System.Drawing.Point(120, 168)
    $searchTextBox.Size = New-Object System.Drawing.Size(200, 25)
    $searchTextBox.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
    $searchTextBox.ForeColor = [System.Drawing.Color]::White
    $searchTextBox.BorderStyle = 'FixedSingle'
    $mainPanel.Controls.Add($searchTextBox)
    
    # Filter buttons
    $filterAllButton = New-Object System.Windows.Forms.Button
    $filterAllButton.Location = New-Object System.Drawing.Point(330, 168)
    $filterAllButton.Size = New-Object System.Drawing.Size(60, 25)
    $filterAllButton.Text = "All"
    $filterAllButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
    $filterAllButton.ForeColor = [System.Drawing.Color]::White
    $filterAllButton.FlatStyle = 'Flat'
    $mainPanel.Controls.Add($filterAllButton)
    
    $filterEnabledButton = New-Object System.Windows.Forms.Button
    $filterEnabledButton.Location = New-Object System.Drawing.Point(395, 168)
    $filterEnabledButton.Size = New-Object System.Drawing.Size(70, 25)
    $filterEnabledButton.Text = "Enabled"
    $filterEnabledButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
    $filterEnabledButton.ForeColor = [System.Drawing.Color]::White
    $filterEnabledButton.FlatStyle = 'Flat'
    $mainPanel.Controls.Add($filterEnabledButton)
    
    $filterDisabledButton = New-Object System.Windows.Forms.Button
    $filterDisabledButton.Location = New-Object System.Drawing.Point(470, 168)
    $filterDisabledButton.Size = New-Object System.Drawing.Size(70, 25)
    $filterDisabledButton.Text = "Disabled"
    $filterDisabledButton.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
    $filterDisabledButton.ForeColor = [System.Drawing.Color]::White
    $filterDisabledButton.FlatStyle = 'Flat'
    $mainPanel.Controls.Add($filterDisabledButton)
    
    # Refresh button
    $refreshButton = New-Object System.Windows.Forms.Button
    $refreshButton.Location = New-Object System.Drawing.Point(550, 168)
    $refreshButton.Size = New-Object System.Drawing.Size(80, 25)
    $refreshButton.Text = "Refresh"
    $refreshButton.BackColor = [System.Drawing.Color]::FromArgb(0, 120, 215)
    $refreshButton.ForeColor = [System.Drawing.Color]::White
    $refreshButton.FlatStyle = 'Flat'
    $mainPanel.Controls.Add($refreshButton)
    
    # Plugin list view
    $pluginListView = New-Object System.Windows.Forms.ListView
    $pluginListView.Location = New-Object System.Drawing.Point(10, 200)
    $pluginListView.Size = New-Object System.Drawing.Size(700, 350)
    $pluginListView.View = 'Details'
    $pluginListView.FullRowSelect = $true
    $pluginListView.GridLines = $true
    $pluginListView.BackColor = [System.Drawing.Color]::FromArgb(51, 51, 55)
    $pluginListView.ForeColor = [System.Drawing.Color]::White
    $pluginListView.BorderStyle = 'FixedSingle'
    $mainPanel.Controls.Add($pluginListView)
    
    # Add columns to list view
    $pluginListView.Columns.Add("Plugin", 200)
    $pluginListView.Columns.Add("Status", 80)
    $pluginListView.Columns.Add("Version", 80)
    $pluginListView.Columns.Add("Category", 100)
    $pluginListView.Columns.Add("Card Size", 80)
    $pluginListView.Columns.Add("Features", 150)
    
    # Action buttons panel
    $actionPanel = New-Object System.Windows.Forms.Panel
    $actionPanel.Location = New-Object System.Drawing.Point(10, 560)
    $actionPanel.Size = New-Object System.Drawing.Size(700, 50)
    $actionPanel.BackColor = [System.Drawing.Color]::FromArgb(45, 45, 48)
    $mainPanel.Controls.Add($actionPanel)
    
    # Enable/Disable button
    $toggleButton = New-Object System.Windows.Forms.Button
    $toggleButton.Location = New-Object System.Drawing.Point(10, 10)
    $toggleButton.Size = New-Object System.Drawing.Size(120, 30)
    $toggleButton.Text = "Toggle Selected"
    $toggleButton.BackColor = [System.Drawing.Color]::FromArgb(0, 120, 215)
    $toggleButton.ForeColor = [System.Drawing.Color]::White
    $toggleButton.FlatStyle = 'Flat'
    $toggleButton.Enabled = $false
    $actionPanel.Controls.Add($toggleButton)
    
    # Enable All button
    $enableAllButton = New-Object System.Windows.Forms.Button
    $enableAllButton.Location = New-Object System.Drawing.Point(140, 10)
    $enableAllButton.Size = New-Object System.Drawing.Size(100, 30)
    $enableAllButton.Text = "Enable All"
    $enableAllButton.BackColor = [System.Drawing.Color]::FromArgb(0, 150, 0)
    $enableAllButton.ForeColor = [System.Drawing.Color]::White
    $enableAllButton.FlatStyle = 'Flat'
    $actionPanel.Controls.Add($enableAllButton)
    
    # Disable All button
    $disableAllButton = New-Object System.Windows.Forms.Button
    $disableAllButton.Location = New-Object System.Drawing.Point(250, 10)
    $disableAllButton.Size = New-Object System.Drawing.Size(100, 30)
    $disableAllButton.Text = "Disable All"
    $disableAllButton.BackColor = [System.Drawing.Color]::FromArgb(200, 0, 0)
    $disableAllButton.ForeColor = [System.Drawing.Color]::White
    $disableAllButton.FlatStyle = 'Flat'
    $actionPanel.Controls.Add($disableAllButton)
    
    # Reset to Defaults button
    $resetButton = New-Object System.Windows.Forms.Button
    $resetButton.Location = New-Object System.Drawing.Point(360, 10)
    $resetButton.Size = New-Object System.Drawing.Size(120, 30)
    $resetButton.Text = "Reset to Defaults"
    $resetButton.BackColor = [System.Drawing.Color]::FromArgb(120, 120, 120)
    $resetButton.ForeColor = [System.Drawing.Color]::White
    $resetButton.FlatStyle = 'Flat'
    $actionPanel.Controls.Add($resetButton)
    
    # Plugin details panel
    $detailsPanel = New-Object System.Windows.Forms.Panel
    $detailsPanel.Location = New-Object System.Drawing.Point(720, 10)
    $detailsPanel.Size = New-Object System.Drawing.Size(300, 600)
    $detailsPanel.BackColor = [System.Drawing.Color]::FromArgb(62, 62, 66)
    $detailsPanel.BorderStyle = 'FixedSingle'
    $detailsPanel.Visible = $false
    $pluginOptionsTab.Controls.Add($detailsPanel)
    
    # Plugin details title
    $detailsTitleLabel = New-Object System.Windows.Forms.Label
    $detailsTitleLabel.Location = New-Object System.Drawing.Point(10, 10)
    $detailsTitleLabel.Size = New-Object System.Drawing.Size(280, 25)
    $detailsTitleLabel.Text = "Plugin Details"
    $detailsTitleLabel.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
    $detailsTitleLabel.ForeColor = [System.Drawing.Color]::White
    $detailsPanel.Controls.Add($detailsTitleLabel)
    
    # Plugin details text
    $detailsLabel = New-Object System.Windows.Forms.Label
    $detailsLabel.Location = New-Object System.Drawing.Point(10, 40)
    $detailsLabel.Size = New-Object System.Drawing.Size(280, 550)
    $detailsLabel.Text = "Select a plugin to view details"
    $detailsLabel.ForeColor = [System.Drawing.Color]::FromArgb(200, 200, 200)
    $detailsLabel.Font = New-Object System.Drawing.Font("Segoe UI", 9)
    $detailsLabel.AutoSize = $false
    $detailsPanel.Controls.Add($detailsLabel)
    
    # Store references for event handlers
    $script:pluginOptionsTab = $pluginOptionsTab
    $script:pluginListView = $pluginListView
    $script:statsLabel = $statsLabel
    $script:searchTextBox = $searchTextBox
    $script:toggleButton = $toggleButton
    $script:detailsPanel = $detailsPanel
    $script:detailsLabel = $detailsLabel
    $script:currentFilter = "All"
    
    # Load initial data
    Update-PluginList
    Update-PluginStats
    
    # Event handlers
    $pluginListView.Add_SelectedIndexChanged({
        Update-PluginDetails
        $script:toggleButton.Enabled = ($script:pluginListView.SelectedItems.Count -gt 0)
    })
    
    $searchTextBox.Add_TextChanged({
        Update-PluginList
    })
    
    $filterAllButton.Add_Click({
        $script:currentFilter = "All"
        Update-PluginList
    })
    
    $filterEnabledButton.Add_Click({
        $script:currentFilter = "Enabled"
        Update-PluginList
    })
    
    $filterDisabledButton.Add_Click({
        $script:currentFilter = "Disabled"
        Update-PluginList
    })
    
    $refreshButton.Add_Click({
        Update-PluginList
        Update-PluginStats
    })
    
    $toggleButton.Add_Click({
        Toggle-SelectedPlugin
    })
    
    $enableAllButton.Add_Click({
        Enable-AllPlugins
    })
    
    $disableAllButton.Add_Click({
        Disable-AllPlugins
    })
    
    $resetButton.Add_Click({
        Reset-ToDefaults
    })
    
    return $pluginOptionsTab
}

# Update plugin list view
function Update-PluginList {
    $script:pluginListView.Items.Clear()
    
    $allPlugins = Get-AllPlugins
    $enabledPlugins = Get-EnabledPlugins
    $searchText = $script:searchTextBox.Text.ToLower()
    
    foreach ($plugin in $allPlugins) {
        # Apply search filter
        if ($searchText -and $plugin.DisplayName.ToLower() -notlike "*$searchText*" -and $plugin.Description.ToLower() -notlike "*$searchText*") {
            continue
        }
        
        # Apply status filter
        $isEnabled = $enabledPlugins.Name -contains $plugin.Name
        switch ($script:currentFilter) {
            "Enabled" { if (-not $isEnabled) { continue } }
            "Disabled" { if ($isEnabled) { continue } }
        }
        
        # Create list view item
        $item = New-Object System.Windows.Forms.ListViewItem($plugin.DisplayName)
        $statusText = if ($isEnabled) { "Enabled" } else { "Disabled" }
        $item.SubItems.Add($statusText)
        $item.SubItems.Add($plugin.Version)
        $item.SubItems.Add($plugin.Category)
        $item.SubItems.Add($plugin.CardSize)
        
        $features = @()
        if ($plugin.HasGUI) { $features += "GUI" }
        if ($plugin.HasCLI) { $features += "CLI" }
        if ($plugin.HasAPI) { $features += "API" }
        if ($plugin.HasScraper) { $features += "Scraper" }
        $item.SubItems.Add($features -join ", ")
        
        $item.Tag = $plugin
        $item.BackColor = if ($isEnabled) { [System.Drawing.Color]::FromArgb(0, 100, 0) } else { [System.Drawing.Color]::FromArgb(100, 0, 0) }
        
        $script:pluginListView.Items.Add($item)
    }
}

# Update plugin statistics
function Update-PluginStats {
    $stats = Get-PluginStats
    $statsText = "Total: $($stats.TotalPlugins) | Enabled: $($stats.EnabledPlugins) | Disabled: $($stats.DisabledPlugins)"
    if ($stats.LastScan) {
        $statsText += " | Last Scan: $($stats.LastScan.ToString('MM/dd/yyyy HH:mm'))"
    }
    $script:statsLabel.Text = $statsText
}

# Update plugin details
function Update-PluginDetails {
    if ($script:pluginListView.SelectedItems.Count -eq 0) {
        $script:detailsPanel.Visible = $false
        return
    }
    
    $plugin = $script:pluginListView.SelectedItems[0].Tag
    $enabledPlugins = Get-EnabledPlugins
    $isEnabled = $enabledPlugins.Name -contains $plugin.Name
    
    $detailsText = @"
Name: $($plugin.DisplayName)
Version: $($plugin.Version)
Author: $($plugin.Author)
Category: $($plugin.Category)
Card Size: $($plugin.CardSize)
Status: $(if ($isEnabled) { "Enabled" } else { "Disabled" })

Description:
$($plugin.Description)

Features:
$(if ($plugin.HasGUI) { "• GUI Integration" })
$(if ($plugin.HasCLI) { "• Command Line Interface" })
$(if ($plugin.HasAPI) { "• API Access" })
$(if ($plugin.HasScraper) { "• Web Scraping" })

Supported Formats:
$($plugin.SupportedFormats -join ", ")

Dependencies:
$($plugin.Dependencies -join ", ")

Last Updated: $($plugin.LastUpdated.ToString('MM/dd/yyyy HH:mm'))
Priority: $($plugin.Priority)
"@
    
    $script:detailsLabel.Text = $detailsText
    $script:detailsPanel.Visible = $true
}

# Toggle selected plugin
function Toggle-SelectedPlugin {
    if ($script:pluginListView.SelectedItems.Count -eq 0) { return }
    
    $plugin = $script:pluginListView.SelectedItems[0].Tag
    $result = Toggle-Plugin -pluginName $plugin.Name
    
    if ($result) {
        Update-PluginList
        Update-PluginStats
        Write-Host "Toggled plugin: $($plugin.DisplayName)"
    }
}

# Enable all plugins
function Enable-AllPlugins {
    $allPlugins = Get-AllPlugins
    $config = Load-PluginConfig
    $config.enabledPlugins = $allPlugins.Name
    Save-PluginConfig -config $config
    
    Update-PluginList
    Update-PluginStats
    Write-Host "Enabled all plugins"
}

# Disable all plugins
function Disable-AllPlugins {
    $config = Load-PluginConfig
    $config.enabledPlugins = @()
    Save-PluginConfig -config $config
    
    Update-PluginList
    Update-PluginStats
    Write-Host "Disabled all plugins"
}

# Reset to defaults
function Reset-ToDefaults {
    $config = $script:defaultPluginConfig
    Save-PluginConfig -config $config
    
    Update-PluginList
    Update-PluginStats
    Write-Host "Reset plugin settings to defaults"
}

# Functions are available for direct use when script is dot-sourced
