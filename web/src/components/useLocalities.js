import { useEffect, useState } from "react";

export function useLocalities() {
  const [localities, setLocalities] = useState(null);
  useEffect(() => {
    fetch("/data/floresti_localities.json").then((r) => r.json()).then(setLocalities);
  }, []);
  return localities;
}
