#!/usr/bin/env bash
set -euo pipefail

pull_request_number="${1:?Pull request number is required}"
: "${GH_TOKEN:?Merge token is required}"
: "${APPROVAL_TOKEN:?Approval token is required}"

pull_request_state() {
  gh pr view "$pull_request_number" \
    --json state,author,baseRefName,headRefName,isCrossRepository,autoMergeRequest,labels \
    --jq 'if .author.login != "app/github-actions" or .baseRefName != "main" or .isCrossRepository or (.headRefName | startswith("release-notes-") | not) or ([.labels[].name] | index("release-notes-automerge") | not) then "UNEXPECTED" elif .state != "OPEN" then .state elif .autoMergeRequest != null then "AUTO_MERGE" else "OPEN" end'
}

retry() {
  local attempt
  for attempt in 1 2 3 4 5; do
    if "$@"; then
      return 0
    fi
    if [ "$attempt" -lt 5 ]; then
      echo "Attempt $attempt failed for release PR #$pull_request_number; retrying in 10 seconds." >&2
      sleep 10
    fi
  done
  echo "Release PR #$pull_request_number still needs automerge follow-up." >&2
  return 1
}

case "$(pull_request_state)" in
  MERGED|CLOSED|AUTO_MERGE) exit 0 ;;
  OPEN) ;;
  *) echo "Refusing to approve an unexpected release PR #$pull_request_number." >&2; exit 1 ;;
esac

retry env GH_TOKEN="$APPROVAL_TOKEN" gh pr review --approve "$pull_request_number"

if retry gh pr merge --squash --auto --delete-branch "$pull_request_number"; then
  exit 0
fi

# A concurrent merge or successful API call with a lost response may have completed the request.
case "$(pull_request_state)" in
  MERGED|AUTO_MERGE) exit 0 ;;
  *) exit 1 ;;
esac
