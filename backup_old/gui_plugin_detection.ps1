# Function to scan for available plugins
function Get-AvailablePlugins {
    param([string]$pluginsPath)

    $plugins = @()
    $pluginDirectories = Get-ChildItem -Path $pluginsPath -Directory -ErrorAction SilentlyContinue

    foreach ($pluginDir in $pluginDirectories) {
        # Check if plugin has required files
        $hasScraper = Test-Path (Join-Path $pluginDir.FullName "*_scraper.py")
        $hasAPI = Test-Path (Join-Path $pluginDir.FullName "*_api.py")
        $hasCLI = Test-Path (Join-Path $pluginDir.FullName "*_cli.py")

        if ($hasScraper -or $hasAPI -or $hasCLI) {
            # Try to get plugin name from README or directory name
            $readmePath = Join-Path $pluginDir.FullName "README.md"
            $pluginName = $pluginDir.Name

            if (Test-Path $readmePath) {
                try {
                    $readmeContent = Get-Content $readmePath -Raw
                    # Look for title in README (usually first line after #)
                    $titleMatch = [regex]::Match($readmeContent, '(?m)^#\s*(.+)$')
                    if ($titleMatch.Success) {
                        $pluginName = $titleMatch.Groups[1].Value.Trim()
                    }
                }
                catch {
                    # Use directory name as fallback
                }
            }

            $plugins += $pluginName
        }
    }

    return $plugins
}
