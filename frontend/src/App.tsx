import { Routes, Route } from "react-router-dom";

import Layout from "./components/layout/Layout";

import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import WBS from "./pages/WBS";
import Login from "./pages/Login";
import ModulePlaceholder from "./pages/ModulePlaceholder";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/wbs" element={<WBS />} />

        <Route
          path="/schedule"
          element={<ModulePlaceholder title="Schedule Intelligence" />}
        />

        <Route
          path="/engineering"
          element={<ModulePlaceholder title="Engineering Management" />}
        />

        <Route
          path="/procurement"
          element={<ModulePlaceholder title="Procurement Control" />}
        />

        <Route
          path="/construction"
          element={<ModulePlaceholder title="Construction Control" />}
        />

        <Route
          path="/cost"
          element={<ModulePlaceholder title="Cost Intelligence" />}
        />

        <Route
          path="/risk"
          element={<ModulePlaceholder title="Risk Management" />}
        />

        <Route
          path="/documents"
          element={<ModulePlaceholder title="Document Intelligence" />}
        />
      </Route>
    </Routes>
  );
}
