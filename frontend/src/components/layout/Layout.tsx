import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

const drawerWidth = 260;

export default function Layout() {
  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <Topbar />

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          ml: `${drawerWidth}px`,
          mt: 8,
          bgcolor: "background.default",
          minHeight: "100vh",
          p: 4,
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
