param (
    [string]$name
)

# Paths to .csproj and Plugin.cs
$csprojPath = "$name\$name.csproj"
$pluginPath = "$name\Plugin.cs"

# Read the .csproj file as XML
[xml]$xml = Get-Content -Path $csprojPath

# Modify or add the <Product> element
$productNode = $xml.Project.PropertyGroup.Product
if ($productNode) {
    $productNode.InnerText = "remghoost"
} else {
    $propertyGroupNode = $xml.Project.PropertyGroup
    $productNode = $xml.CreateElement("Product")
    $productNode.InnerText = "remghoost"
    $propertyGroupNode.AppendChild($productNode)
}

# Create a new <ItemGroup> for the two DLL references
$itemGroup = $xml.CreateElement("ItemGroup")

# Define the DLL references with the new structure
$dllReferences = @(
    @{
        Include = "PerfectRandom.Sulfur.Core"
        HintPath = "E:\Games\Steam\steamapps\common\SULFUR\Sulfur_Data\Managed\PerfectRandom.Sulfur.Core.dll"
    },
    @{
        Include = "PerfectRandom.Sulfur.Gameplay"
        HintPath = "E:\Games\Steam\steamapps\common\SULFUR\Sulfur_Data\Managed\PerfectRandom.Sulfur.Gameplay.dll"
    }
)

# Add each DLL as a <Reference> inside the <ItemGroup>
foreach ($dll in $dllReferences) {
    $reference = $xml.CreateElement("Reference")
    $reference.SetAttribute("Include", $dll.Include)

    $hintPath = $xml.CreateElement("HintPath")
    $hintPath.InnerText = $dll.HintPath

    $reference.AppendChild($hintPath)
    $itemGroup.AppendChild($reference)
}

# Append the new <ItemGroup> to the project file
$xml.Project.AppendChild($itemGroup)

# Save the modified .csproj file
$xml.Save($csprojPath)

# Modify Plugin.cs
if (Test-Path $pluginPath) {
    # Read content of Plugin.cs
    $pluginContent = Get-Content -Path $pluginPath -Raw

    # Add using statements at the top only if they don’t already exist
    $usingStatements = @"
using PerfectRandom.Sulfur.Core;
using PerfectRandom.Sulfur.Gameplay;

"@

    if ($pluginContent -notmatch "using\s+PerfectRandom\.Sulfur\.Core;" -and $pluginContent -notmatch "using\s+PerfectRandom\.Sulfur\.Gameplay;") {
        $pluginContent = $usingStatements + "`n" + $pluginContent
    }

    # Replace class name with project name
    $pluginContent = $pluginContent -replace "public class Plugin", "public class $name"

    # Write updated content to Plugin.cs, preserving original formatting
    Set-Content -Path $pluginPath -Value $pluginContent
} else {
    Write-Host "Plugin.cs file not found at $pluginPath"
}
