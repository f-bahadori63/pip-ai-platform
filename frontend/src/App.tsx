import { Routes, Route, Navigate } from "react-router-dom";

import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import WBS from "./pages/WBS";
function App() {
return ( <Layout> <Routes>
<Route path="/" element={<Dashboard />} />
<Route path="/projects" element={<Projects />} />


    {/* Temporary placeholders */}
    <Route path="/wbs" element={<WBS />} />
    <Route path="/schedule" element={<div>Schedule Module</div>} />
    <Route path="/engineering" element={<div>Engineering Module</div>} />
    <Route path="/procurement" element={<div>Procurement Module</div>} />
    <Route path="/construction" element={<div>Construction Module</div>} />
    <Route path="/cost" element={<div>Cost Module</div>} />
    <Route path="/risk" element={<div>Risk Module</div>} />
    <Route path="/documents" element={<div>Documents Module</div>} />

    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
</Layout>

);
}

export default App;
