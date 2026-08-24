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

// Sutherland-Hodgman: clip a single polygon ring (array of [lon,lat],
// closed or not) against an axis-aligned rectangle. Mirrors what
// shapely's polygon.intersection(box(...)) does in the Python app, without
// a full geometry-library dependency -- the municipality shapes are simple
// enough (no self-intersections) for this to be exact, not approximate.
function clipRingToRect(ring, minLon, minLat, maxLon, maxLat) {
  const edges = [
    { inside: (p) => p[0] >= minLon, x: (p, q) => intersectVertical(p, q, minLon) },
    { inside: (p) => p[0] <= maxLon, x: (p, q) => intersectVertical(p, q, maxLon) },
    { inside: (p) => p[1] >= minLat, x: (p, q) => intersectHorizontal(p, q, minLat) },
    { inside: (p) => p[1] <= maxLat, x: (p, q) => intersectHorizontal(p, q, maxLat) },
  ];
  const intersectVertical = (p, q, x) => [x, p[1] + ((q[1] - p[1]) * (x - p[0])) / (q[0] - p[0])];
  const intersectHorizontal = (p, q, y) => [p[0] + ((q[0] - p[0]) * (y - p[1])) / (q[1] - p[1]), y];

  let output = ring;
  for (const edge of edges) {
    const input = output;
    output = [];
    if (input.length === 0) break;
    for (let i = 0; i < input.length; i++) {
      const curr = input[i];
      const prev = input[(i - 1 + input.length) % input.length];
      const currIn = edge.inside(curr);
      const prevIn = edge.inside(prev);
      if (currIn) {
        if (!prevIn) output.push(edge.x(prev, curr));
        output.push(curr);
      } else if (prevIn) {
        output.push(edge.x(prev, curr));
      }
    }
  }
  return output;
}

function ringArea(ring) {
  let a = 0;
  for (let i = 0; i < ring.length; i++) {
    const [x1, y1] = ring[i];
    const [x2, y2] = ring[(i + 1) % ring.length];
    a += x1 * y2 - x2 * y1;
  }
  return Math.abs(a) / 2;
}

// Clip a Polygon/MultiPolygon geometry's outer rings (holes ignored -- none
// of this app's municipality shapes have any) against a quadrant rectangle,
// returning a single-part GeoJSON Polygon (the largest piece, if the clip
// produced more than one -- mirrors compute_district_polygons() in
// streamlit_app.py, which reduces to one Polygon for the same reason: a
// MultiPolygon here trips a streamlit-folium click-tracking bug on the
// Python side, so both apps keep district geometry single-part for
// consistency), or null if the quadrant doesn't overlap the shape at all.
export function clipGeometryToRect(geometry, minLon, minLat, maxLon, maxLat) {
  const parts = geometryParts(geometry)
    .map((part) => clipRingToRect(part.coordinates[0], minLon, minLat, maxLon, maxLat))
    .filter((ring) => ring.length >= 3);
  if (parts.length === 0) return null;
  const largest = parts.reduce((a, b) => (ringArea(b) > ringArea(a) ? b : a));
  return { type: "Polygon", coordinates: [[...largest, largest[0]]] };
}

// Approximate district sub-boundaries for a municipality: split its real
// territory into a 2x2 grid (NW/NE/SW/SE) and assign the municipality's 4
// named districts to the quadrants in order. Florești's districts aren't
// real cadastral units (invented for this sim, like the districts
// themselves), so this is a legible approximation, not a survey -- mirrors
// compute_district_polygons() in streamlit_app.py.
export function computeDistrictGeometries(geometry, districtNames) {
  const [minLon, minLat, maxLon, maxLat] = geometryBounds(geometry);
  const midLon = (minLon + maxLon) / 2;
  const midLat = (minLat + maxLat) / 2;
  const quadrants = [
    [minLon, midLat, midLon, maxLat],
    [midLon, midLat, maxLon, maxLat],
    [minLon, minLat, midLon, midLat],
    [midLon, minLat, maxLon, midLat],
  ];
  const result = {};
  districtNames.forEach((name, i) => {
    const [qMinLon, qMinLat, qMaxLon, qMaxLat] = quadrants[i];
    const clipped = clipGeometryToRect(geometry, qMinLon, qMinLat, qMaxLon, qMaxLat);
    if (clipped) result[name] = clipped;
  });
  return result;
}
