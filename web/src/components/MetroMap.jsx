import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, GeoJSON, Marker, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import { useSimState, useSimActions } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE, MUNICIPALITY_COLORS } from "../data/metroStructure.js";
import { allProjectsWithScope, PROJECT_MAP_LOCATIONS } from "../data/projects.js";
import { pointInGeometry, geometryBounds, representativePoint, geometryParts, zoomForBounds, toLatLng } from "../utils/geo.js";

const TILE_URL = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png";
const TILE_ATTR =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';

function divIcon(html, extraClass = "") {
  return L.divIcon({ html, className: `map-divicon ${extraClass}`, iconSize: null });
}

function labelIcon(text, color) {
  return divIcon(
    `<div style="font-size:12px;font-weight:700;color:${color};text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff;white-space:nowrap;transform:translate(-50%,-50%);">${text}</div>`
  );
}

function projectIcon() {
  return divIcon(
    '<div style="font-size:20px;line-height:1;transform:translate(-50%,-100%);filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">🏗️</div>'
  );
}

// Imperatively sets the map's view once, whenever the target center/zoom
// changes -- mirrors baking a static zoom into the Python folium.Map(...)
// constructor instead of relying on fitBounds() timing quirks.
function SetView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [map, center[0], center[1], zoom]);
  return null;
}

function useGeoData() {
  const [data, setData] = useState(null);
  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetch("/data/floresti_localities.json").then((r) => r.json()),
      fetch("/data/floresti_district.geojson").then((r) => r.json()),
      fetch("/data/floresti_municipalities.geojson").then((r) => r.json()),
    ]).then(([localities, prefecture, municipalities]) => {
      if (!cancelled) setData({ localities, prefecture, municipalities });
    });
    return () => {
      cancelled = true;
    };
  }, []);
  return data;
}

export function findLocality(localities, name) {
  const matches = localities.filter((l) => l.name === name);
  const towns = matches.filter((l) => l.type === "town");
  return (towns.length ? towns : matches)[0];
}

export default function MetroMap() {
  const state = useSimState();
  const actions = useSimActions();
  const geo = useGeoData();

  const municipalityFeatures = useMemo(() => {
    if (!geo) return {};
    const out = {};
    for (const f of geo.municipalities.features) {
      if (f.properties.name === "Florești Metropole") continue;
      out[f.properties.name] = f;
    }
    return out;
  }, [geo]);

  const metroBoundaryFeature = useMemo(() => {
    if (!geo) return null;
    return geo.municipalities.features.find((f) => f.properties.name === "Florești Metropole") || null;
  }, [geo]);

  const { center, zoom } = useMemo(() => {
    if (state.metroActive && metroBoundaryFeature) {
      const bounds = geometryBounds(metroBoundaryFeature.geometry);
      const [minLon, minLat, maxLon, maxLat] = bounds;
      return {
        center: [(minLat + maxLat) / 2, (minLon + maxLon) / 2],
        zoom: zoomForBounds(bounds, 700, 500),
      };
    }
    return { center: [47.9, 28.35], zoom: 10 };
  }, [state.metroActive, metroBoundaryFeature]);

  if (!geo) {
    return <div className="map-loading">Loading map…</div>;
  }

  const projectEntries = allProjectsWithScope();

  return (
    <div className="map-shell">
      <MapContainer center={center} zoom={zoom} scrollWheelZoom style={{ height: 520, width: "100%" }}>
        <SetView center={center} zoom={zoom} />
        <TileLayer url={TILE_URL} attribution={TILE_ATTR} />
        <GeoJSON
          data={geo.prefecture}
          style={{ color: "#333333", weight: 2, dashArray: "6,4", fillOpacity: 0 }}
          onEachFeature={(_f, layer) => layer.bindTooltip("Florești Prefecture boundary")}
        />

        {state.metroActive && metroBoundaryFeature && (
          <GeoJSON
            key="metro-boundary"
            data={metroBoundaryFeature}
            style={{ color: "#e91e8c", weight: 3, fillOpacity: 0 }}
            onEachFeature={(_f, layer) => layer.bindTooltip("Florești Metropole boundary")}
          />
        )}

        {state.metroActive &&
          Object.entries(METRO_STRUCTURE).map(([name]) => {
            const feature = municipalityFeatures[name];
            if (!feature) return null;
            const color = MUNICIPALITY_COLORS[name];
            const active = state.inaugurated.includes(name);
            const tooltipText = `${name} ${active ? "✅ inaugurated" : "(not yet inaugurated)"}`;

            const anchorName = METRO_STRUCTURE[name].anchor;
            const anchorLoc = findLocality(geo.localities, anchorName);
            let labelPoint = null;
            if (anchorLoc && pointInGeometry(anchorLoc.lon, anchorLoc.lat, feature.geometry)) {
              labelPoint = [anchorLoc.lat, anchorLoc.lon];
            }
            const labelPoints = labelPoint
              ? [labelPoint]
              : geometryParts(feature.geometry).map((part) => {
                  const [lon, lat] = representativePoint(part);
                  return [lat, lon];
                });

            return (
              <div key={name}>
                <GeoJSON
                  data={feature}
                  style={{ color, weight: 3, fillColor: color, fillOpacity: active ? 0.6 : 0.4 }}
                  onEachFeature={(_f, layer) => {
                    layer.bindTooltip(tooltipText);
                    layer.on("click", () => actions.selectMunicipality(name));
                  }}
                />
                {labelPoints.map((pt, i) => (
                  <Marker key={i} position={pt} icon={labelIcon(`${name}${active ? " ✅" : ""}`, active ? "#111111" : "#333333")} interactive={false} />
                ))}
              </div>
            );
          })}

        {state.metroActive &&
          projectEntries.map(([project, scopeLabel]) => {
            const resolved = state.resolvedProjects[project.id];
            if (!resolved || resolved.choice === null) return null;
            const loc = PROJECT_MAP_LOCATIONS[project.id];
            if (!loc) return null;
            const tooltipText = `🏗️ ${project.title} (${scopeLabel}) — ${resolved.choice}) ${resolved.label}`;
            if (loc.type === "point") {
              return (
                <Marker
                  key={project.id}
                  position={loc.coord}
                  icon={projectIcon()}
                  eventHandlers={{ add: (e) => e.target.bindTooltip(tooltipText) }}
                />
              );
            }
            const positions = loc.points;
            const mid = [(positions[0][0] + positions[1][0]) / 2, (positions[0][1] + positions[1][1]) / 2];
            return (
              <div key={project.id}>
                <Polyline
                  positions={positions}
                  pathOptions={{ color: "#5a3921", weight: 4, opacity: 0.85, dashArray: "8,6" }}
                  eventHandlers={{ add: (e) => e.target.bindTooltip(tooltipText) }}
                />
                <Marker position={mid} icon={projectIcon()} eventHandlers={{ add: (e) => e.target.bindTooltip(tooltipText) }} />
              </div>
            );
          })}
      </MapContainer>

      {state.metroActive && (
        <div className="map-legend">
          <div className="map-legend-title">Municipalities</div>
          {Object.keys(METRO_STRUCTURE).map((name) => {
            const active = state.inaugurated.includes(name);
            return (
              <div className="map-legend-row" key={name}>
                <span className="map-legend-swatch" style={{ background: MUNICIPALITY_COLORS[name], opacity: active ? 1 : 0.35 }} />
                <span>{name} {active ? "✅" : ""}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
