export function downloadBlob(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function historyToCsv(history, monthLabels) {
  const cols = ["Governance", "Economy", "Stability", "Risk"];
  const header = ["", ...cols].join(",");
  const rows = history.map((row, i) => [monthLabels[i], ...cols.map((c) => row[c])].join(","));
  return [header, ...rows].join("\n");
}
