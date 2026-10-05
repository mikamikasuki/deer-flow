#!/usr/bin/env bash
# Assert that Helm declares a multi-replica Gateway to the startup safety gate.
#
# Usage:
#   scripts/check_chart_multi_instance_gate.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHART="$ROOT/deploy/helm/deer-flow"

if ! command -v helm >/dev/null 2>&1; then
  echo "::error::helm is required to run this check" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if ! helm template deer-flow "$CHART" --include-crds >"$TMP/single.yaml"; then
  echo "::error::default chart render failed" >&2
  exit 1
fi
if ! helm template deer-flow "$CHART" --include-crds --set gateway.replicas=2 >"$TMP/multi.yaml"; then
  echo "::error::multi-replica chart render failed" >&2
  exit 1
fi

has_env() {
  grep -qE "^[[:space:]]*- name: $1\$" "$2"
}

env_value() {
  grep -A1 -E "^[[:space:]]*- name: $1\$" "$2" | grep -oE 'value: "[^"]*"' | head -1
}

if has_env DEER_FLOW_MULTI_INSTANCE "$TMP/single.yaml"; then
  echo "FAIL  single-replica render must leave DEER_FLOW_MULTI_INSTANCE unset"
  exit 1
fi
echo "PASS  single-replica render leaves DEER_FLOW_MULTI_INSTANCE unset"

if ! has_env DEER_FLOW_MULTI_INSTANCE "$TMP/multi.yaml"; then
  echo "FAIL  multi-replica render must declare DEER_FLOW_MULTI_INSTANCE"
  exit 1
fi
if [ "$(env_value DEER_FLOW_MULTI_INSTANCE "$TMP/multi.yaml")" != 'value: "1"' ]; then
  echo "FAIL  multi-replica render must set DEER_FLOW_MULTI_INSTANCE=1"
  exit 1
fi
echo "PASS  multi-replica render declares DEER_FLOW_MULTI_INSTANCE=1"
