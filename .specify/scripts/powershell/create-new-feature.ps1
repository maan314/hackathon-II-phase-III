param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$FeatureDescription,

    [int]$Number = 1,

    [string]$ShortName = "feature",

    [switch]$Json
)

# Join the feature description array into a single string
$featureText = ($FeatureDescription -join " ").Trim()

# Create branch name
$branchName = "${Number}-${ShortName}"

# Create spec directory if it doesn't exist
$specDir = "specs/${branchName}"
if (!(Test-Path $specDir)) {
    New-Item -ItemType Directory -Path $specDir -Force | Out-Null
}

# Create the spec file
$specFile = "${specDir}/spec.md"

# Output JSON result
$result = @{
    BRANCH_NAME = $branchName
    SPEC_FILE = $specFile
    FEATURE_DIR = $specDir
}

if ($Json) {
    $result | ConvertTo-Json
} else {
    Write-Host "Branch: $($result.BRANCH_NAME)"
    Write-Host "Spec File: $($result.SPEC_FILE)"
    Write-Host "Feature Dir: $($result.FEATURE_DIR)"
}