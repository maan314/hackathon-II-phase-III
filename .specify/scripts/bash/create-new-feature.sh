#!/bin/bash

NUMBER=1
SHORTNAME=""
FEATURE_DESCRIPTION=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --number|-n)
      NUMBER="$2"
      shift 2
      ;;
    --short-name|-s)
      SHORTNAME="$2"
      shift 2
      ;;
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    *)
      FEATURE_DESCRIPTION="$*"
      break
      ;;
  esac
done

# Create branch name
BRANCH_NAME="${NUMBER}-${SHORTNAME}"

# Create spec directory if it doesn't exist
SPEC_DIR="specs/${BRANCH_NAME}"
mkdir -p "$SPEC_DIR"

# Create the spec file
SPEC_FILE="${SPEC_DIR}/spec.md"

# Create feature directory
FEATURE_DIR="$SPEC_DIR"

# Output JSON result
if [ "$JSON_OUTPUT" = true ]; then
  cat <<EOF
{
  "BRANCH_NAME": "$BRANCH_NAME",
  "SPEC_FILE": "$SPEC_FILE",
  "FEATURE_DIR": "$FEATURE_DIR"
}
EOF
else
  echo "Branch: $BRANCH_NAME"
  echo "Spec File: $SPEC_FILE"
  echo "Feature Dir: $FEATURE_DIR"
fi