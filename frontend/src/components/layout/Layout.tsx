import { Box, Toolbar } from "@mui/material";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

interface LayoutProps {
children: React.ReactNode;
}

const drawerWidth = 260;

export default function Layout({ children }: LayoutProps) {
return (
<Box sx={{ display: "flex" }}> <Topbar /> <Sidebar />


  <Box
    component="main"
    sx={{
      flexGrow: 1,
      ml: `${drawerWidth}px`,
      mt: 8,
      bgcolor: "#020b1f",
      minHeight: "100vh",
      p: 4,
    }}
  >
    <Toolbar />
    {children}
  </Box>
</Box>


);
}
