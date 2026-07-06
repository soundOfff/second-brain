import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  type ReactNode,
} from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { Settings, SettingsPatch } from "@second-brain/types";
import { fetchSettings, patchSettings } from "../lib/api";
import { applyTheme, DEFAULT_SETTINGS } from "../lib/theme";

type Ctx = {
  settings: Settings;
  loading: boolean;
  update: (patch: SettingsPatch) => Promise<void>;
};

const SettingsContext = createContext<Ctx | null>(null);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["settings"],
    queryFn: fetchSettings,
  });

  const settings = data ?? DEFAULT_SETTINGS;

  useEffect(() => {
    applyTheme(settings);
  }, [settings]);

  const mutation = useMutation({
    mutationFn: patchSettings,
    onSuccess: (next) => {
      qc.setQueryData(["settings"], next);
      applyTheme(next);
    },
  });

  const update = useCallback(
    async (patch: SettingsPatch) => {
      await mutation.mutateAsync(patch);
    },
    [mutation],
  );

  const value = useMemo(
    () => ({ settings, loading: isLoading, update }),
    [settings, isLoading, update],
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) throw new Error("useSettings outside provider");
  return ctx;
}
