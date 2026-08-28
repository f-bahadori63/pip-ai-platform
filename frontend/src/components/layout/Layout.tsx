import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

const drawerWidth = 260;

export default function Layout() {
  return (
    <Box sx={{ display: "flex", width: "100%", minWidth: 0, minHeight: "100vh" }}>
      <Sidebar />
      <Topbar />

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: `calc(100% - ${drawerWidth}px)`,
          minWidth: 0,
          mt: 8,
          bgcolor: "background.default",
          minHeight: "calc(100vh - 64px)",
          p: { xs: 2, md: 3 },
          boxSizing: "border-box",
          overflowX: "hidden",
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
