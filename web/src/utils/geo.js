// Minimal geometry helpers so we don't need a full turf/shapely-equivalent
// dependency for the two things the map needs: "is this point inside this
// polygon" (for anchoring municipality labels at their real locality) and a
// bounding box + representative point for polygons/multipolygons.

// Ray-casting point-in-polygon test for a single GeoJSON polygon ring set
// ([[outer], [hole1], ...], each ring an array of [lon, lat]).
function pointInRing(lon, lat, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    const intersect =
      yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

function pointInPolygonCoords(lon, lat, polygonCoords) {
  // polygonCoords: [outerRing, ...holeRings]
  if (!pointInRing(lon, lat, polygonCoords[0])) return false;
  for (let i = 1; i < polygonCoords.length; i++) {
    if (pointInRing(lon, lat, polygonCoords[i])) return false; // inside a hole
  }
  return true;
}

// geometry: a GeoJSON Polygon or MultiPolygon geometry object.
export function pointInGeometry(lon, lat, geometry) {
  if (!geometry) return false;
  if (geometry.type === "Polygon") {
    return pointInPolygonCoords(lon, lat, geometry.coordinates);
  }
  if (geometry.type === "MultiPolygon") {
    return geometry.coordinates.some((poly) => pointInPolygonCoords(lon, lat, poly));
  }
  return false;
}

// Bounding box [minLon, minLat, maxLon, maxLat] for a Polygon/MultiPolygon.
export function geometryBounds(geometry) {
  let minLon = Infinity, minLat = Infinity, maxLon = -Infinity, maxLat = -Infinity;
  const rings = geometry.type === "MultiPolygon" ? geometry.coordinates.flat() : geometry.coordinates;
  for (const ring of rings) {
    for (const [lon, lat] of ring) {
      if (lon < minLon) minLon = lon;
      if (lon > maxLon) maxLon = lon;
      if (lat < minLat) minLat = lat;
      if (lat > maxLat) maxLat = lat;
    }
  }
  return [minLon, minLat, maxLon, maxLat];
}

// A simple, dependable "somewhere inside this shape" point: the centroid of
// the largest ring by point count (good enough as a fallback when a real
// locality point isn't available/inside — Leaflet only needs *a* point on
// the shape for a label, not a perfect visual center).
export function representativePoint(geometry) {
  const polys = geometry.type === "MultiPolygon" ? geometry.coordinates : [geometry.coordinates];
  let best = null;
  let bestLen = -1;
  for (const poly of polys) {
    const outer = poly[0];
    if (outer.length > bestLen) {
      bestLen = outer.length;
      best = outer;
    }
  }
  let sumLon = 0, sumLat = 0;
  for (const [lon, lat] of best) {
    sumLon += lon;
    sumLat += lat;
  }
  return [sumLon / best.length, sumLat / best.length];
}

export function geometryParts(geometry) {
  if (geometry.type === "MultiPolygon") {
    return geometry.coordinates.map((coords) => ({ type: "Polygon", coordinates: coords }));
  }
  return [geometry];
}

// Compute a static Leaflet zoom level that fits `bounds` in a
// widthPx x heightPx viewport, mirroring the Python _zoom_for_bounds() —
// baked in at map-construction time instead of relying on fitBounds(),
// which can behave inconsistently depending on when the container is
// actually measured.
export function zoomForBounds(bounds, widthPx, heightPx, padding = 0.2) {
  let [minLon, minLat, maxLon, maxLat] = bounds;
  const dLon = (maxLon - minLon) * padding;
  const dLat = (maxLat - minLat) * padding;
  minLon -= dLon;
  maxLon += dLon;
  minLat -= dLat;
  maxLat += dLat;

  const mercY = (lat) => {
    const rad = (Math.max(Math.min(lat, 89.9), -89.9) * Math.PI) / 180;
    return Math.log(Math.tan(Math.PI / 4 + rad / 2));
  };

  const worldPx = 256;
  const lonDiff = Math.max(maxLon - minLon, 1e-9);
  const zoomLon = Math.log2((widthPx * 360) / (lonDiff * worldPx));
  const latDiff = Math.max(Math.abs(mercY(maxLat) - mercY(minLat)), 1e-9);
  const zoomLat = Math.log2((heightPx * (2 * Math.PI)) / (latDiff * worldPx));
  return Math.max(3, Math.min(18, Math.floor(Math.min(zoomLon, zoomLat))));
}

// [lon,lat] GeoJSON order -> [lat,lon] Leaflet order.
export const toLatLng = ([lon, lat]) => [lat, lon];
