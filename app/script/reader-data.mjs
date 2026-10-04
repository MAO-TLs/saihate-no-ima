// A v1.0.0 hotfix keeps its version while invalidating older cached JSON.
export function scriptDataHref(file) {
  return `../script-data/${file}?rev=20261004-english-carryovers`;
}
