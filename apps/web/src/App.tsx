import { Navigate, Route, Routes, useSearchParams } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { ReviewQueuePage } from "./features/feed/ReviewQueuePage";
import { FeedStatsPage } from "./features/feed/FeedStatsPage";
import { SettingsPage } from "./features/feed/SettingsPage";
import { WikiLayout } from "./features/wiki/WikiLayout";
import { WikiPageView } from "./features/wiki/WikiPageView";
import { WikiIndexPage } from "./features/wiki/WikiIndexPage";
import { SourceViewerPage } from "./features/wiki/SourceViewerPage";

function DemoRedirect() {
  return <Navigate to="/feed/review?demo=1" replace />;
}

function FeedRoutes() {
  const [params] = useSearchParams();
  const demo = params.get("demo") === "1";

  return (
    <Routes>
      <Route path="review" element={<ReviewQueuePage demo={demo} />} />
      <Route path="stats" element={<FeedStatsPage demo={demo} />} />
      <Route path="settings" element={<SettingsPage />} />
      <Route path="*" element={<Navigate to="review" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/feed/review" replace />} />
      <Route path="/demo" element={<DemoRedirect />} />
      <Route
        path="/feed/*"
        element={
          <AppShell mode="feed">
            <FeedRoutes />
          </AppShell>
        }
      />
      <Route path="/wiki" element={<WikiLayout />}>
        <Route index element={<WikiIndexPage />} />
        <Route path="source/:id" element={<SourceViewerPage />} />
        <Route path="*" element={<WikiPageView />} />
      </Route>
      <Route path="*" element={<Navigate to="/feed/review" replace />} />
    </Routes>
  );
}
