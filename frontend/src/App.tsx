import { Routes, Route } from "react-router-dom";

import { ProjectProvider } from "./context/ProjectContext";

import Layout from "./components/layout/Layout";

import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import WBS from "./pages/WBS";
import Login from "./pages/Login";
import Documents from "./pages/Documents";
import Schedule from "./pages/Schedule";
import Cost from "./pages/Cost";
import ModulePlaceholder from "./pages/ModulePlaceholder";

export default function App() {
  return (
    <ProjectProvider>
      <Routes>

      <Route
        path="/login"
        element={<Login />}
      />

      <Route element={<Layout />}>

        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/projects"
          element={<Projects />}
        />

        <Route
          path="/wbs"
          element={<WBS />}
        />

        <Route
          path="/schedule"
          element={<Schedule />}
        />

        <Route
          path="/engineering"
          element={
            <ModulePlaceholder
              title="Engineering Management"
            />
          }
        />

        <Route
          path="/procurement"
          element={
            <ModulePlaceholder
              title="Procurement Control"
            />
          }
        />

        <Route
          path="/construction"
          element={
            <ModulePlaceholder
              title="Construction Control"
            />
          }
        />

        <Route
          path="/cost"
          element={<Cost />}
        />

        <Route
          path="/risk"
          element={
            <ModulePlaceholder
              title="Risk Management"
            />
          }
        />

        <Route
          path="/documents"
          element={<Documents />}
        />

      </Route>

    </Routes>
    </ProjectProvider>
  );
}




