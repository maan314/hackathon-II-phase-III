param([switch]$Json)

# Determine the feature branch from git
$branch = $(git branch --show-current)

# If we can't determine the branch from git, default to a known pattern
if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "1-todo-backend-api"
}

# Set up paths based on the branch
$specsDir = "specs/$branch"
$featureSpec = "$specsDir/spec.md"
$implPlan = "$specsDir/plan.md"

# Create the output object
$result = @{
    FEATURE_SPEC = $featureSpec
    IMPL_PLAN = $implPlan
    SPECS_DIR = $specsDir
    BRANCH = $branch
}

if ($Json) {
    $result | ConvertTo-Json
} else {
    Write-Output "Feature Spec: $($result.FEATURE_SPEC)"
    Write-Output "Impl Plan: $($result.IMPL_PLAN)"
    Write-Output "Specs Dir: $($result.SPECS_DIR)"
    Write-Output "Branch: $($result.BRANCH)"
}