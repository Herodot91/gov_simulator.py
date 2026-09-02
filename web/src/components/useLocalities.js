import localities from "../../public/data/floresti_localities.json";

// Bundled at build time (not fetched at runtime) so the app -- and an
// Artifact publish of it -- works with no server behind it.
export function useLocalities() {
  return localities;
}
