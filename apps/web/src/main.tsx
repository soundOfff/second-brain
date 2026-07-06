import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";
import App from "./App";
import { SettingsProvider } from "./hooks/useSettings";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5_000, retry: 1 },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <SettingsProvider>
          <App />
          <Toaster
            theme="dark"
            position="bottom-center"
            toastOptions={{
              className: "brain-toast",
              style: {
                fontFamily: "var(--font-mono)",
                background: "var(--ac)",
                color: "var(--ac-on)",
                border: "none",
              },
            }}
          />
        </SettingsProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
