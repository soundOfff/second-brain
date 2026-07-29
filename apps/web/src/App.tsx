import { Navigate, Route, Routes, useSearchParams } from "react-router-dom";
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

function ReviewRoute() {
  const [params] = useSearchParams();
  return <ReviewQueuePage demo={params.get("demo") === "1"} />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/feed/review" replace />} />
      <Route path="/demo" element={<DemoRedirect />} />
      <Route path="/feed" element={<Navigate to="/feed/review" replace />} />
      <Route path="/feed/review" element={<ReviewRoute />} />
      <Route path="/feed/stats" element={<FeedStatsPage />} />
      <Route path="/feed/settings" element={<SettingsPage />} />
      <Route path="/wiki" element={<WikiLayout />}>
        <Route index element={<WikiIndexPage />} />
        <Route path="source/:id" element={<SourceViewerPage />} />
        <Route path="*" element={<WikiPageView />} />
      </Route>
      <Route path="*" element={<Navigate to="/feed/review" replace />} />
    </Routes>
  );
}
