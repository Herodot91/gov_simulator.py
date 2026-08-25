import MetroMap from "./MetroMap.jsx";

export default function MapTab() {
  return (
    <>
      <p className="caption">
        The metropole's full territory, transit network, roads, and key sites. Click a municipality,
        district, or campus marker to drill into it — see the Decentralization Structure and Schools
        tabs for the result.
      </p>
      <MetroMap />
    </>
  );
}
