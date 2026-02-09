#!/bin/bash

# Determine the feature branch from git
BRANCH=$(git branch --show-current 2>/dev/null)

# If we can't determine the branch from git, default to a known pattern
if [ -z "$BRANCH" ] || [ "$BRANCH" = "" ]; then
    BRANCH="1-todo-backend-api"
fi

# Set up paths based on the branch
SPECS_DIR="specs/$BRANCH"
FEATURE_SPEC="$SPECS_DIR/spec.md"
IMPL_PLAN="$SPECS_DIR/plan.md"

# Create the output JSON
cat <<EOF
{
  "FEATURE_SPEC": "$FEATURE_SPEC",
  "IMPL_PLAN": "$IMPL_PLAN",
  "SPECS_DIR": "$SPECS_DIR",
  "BRANCH": "$BRANCH"
}
EOF