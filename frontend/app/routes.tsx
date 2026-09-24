import { useCallback, useEffect, useState } from "react";

function collectionIdFromPath(pathname: string) {
  const match = pathname.match(/^\/collections\/([^/]+)\/?$/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function useAppRoute() {
  const [collectionId, setCollectionId] = useState<string | null>(() =>
    collectionIdFromPath(window.location.pathname),
  );

  useEffect(() => {
    const handlePopState = () => {
      setCollectionId(collectionIdFromPath(window.location.pathname));
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const navigateToCollection = useCallback(
    (nextId: string | null, replace = false) => {
      const path = nextId ? `/collections/${encodeURIComponent(nextId)}` : "/";
      window.history[replace ? "replaceState" : "pushState"]({}, "", path);
      setCollectionId(nextId);
    },
    [],
  );

  return { collectionId, navigateToCollection };
}
