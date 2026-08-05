import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
  } from "@mui/material";
  
  import DashboardIcon from "@mui/icons-material/Dashboard";
  import FolderIcon from "@mui/icons-material/Folder";
  import AccountTreeIcon from "@mui/icons-material/AccountTree";
  import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
  import EngineeringIcon from "@mui/icons-material/Engineering";
  import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
  import PrecisionManufacturingIcon from "@mui/icons-material/PrecisionManufacturing";
  import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
  import WarningAmberIcon from "@mui/icons-material/WarningAmber";
  import DescriptionIcon from "@mui/icons-material/Description";
  
  import { NavLink } from "react-router-dom";
  
  const drawerWidth = 260;
  
  const menuItems = [
  { text: "Dashboard", path: "/", icon: <DashboardIcon /> },
  { text: "Projects", path: "/projects", icon: <FolderIcon /> },
  { text: "WBS", path: "/wbs", icon: <AccountTreeIcon /> },
  { text: "Schedule", path: "/schedule", icon: <CalendarMonthIcon /> },
  { text: "Engineering", path: "/engineering", icon: <EngineeringIcon /> },
  { text: "Procurement", path: "/procurement", icon: <ShoppingCartIcon /> },
  { text: "Construction", path: "/construction", icon: <PrecisionManufacturingIcon /> },
  { text: "Cost", path: "/cost", icon: <AttachMoneyIcon /> },
  { text: "Risk", path: "/risk", icon: <WarningAmberIcon /> },
  { text: "Documents", path: "/documents", icon: <DescriptionIcon /> },
  ];
  
  export default function Sidebar() {
  return (
  <Drawer
  variant="permanent"
  sx={{
  width: drawerWidth,
  flexShrink: 0,
  "& .MuiDrawer-paper": {
  width: drawerWidth,
  boxSizing: "border-box",
  bgcolor: "#17233a",
  color: "white",
  borderRight: "1px solid rgba(255,255,255,0.08)",
  },
  }}
  > <Toolbar> <Typography variant="h6" fontWeight="bold">
  PIP AI Platform </Typography> </Toolbar>
  
  
    <Box sx={{ px: 1, py: 2 }}>
      <List>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.text}
            component={NavLink}
            to={item.path}
            end={item.path === "/"}
            sx={{
              borderRadius: 2,
              mb: 1,
              color: "rgba(255,255,255,0.9)",
              "&.active": {
                bgcolor: "rgba(255,255,255,0.12)",
                color: "#ffffff",
              },
              "&:hover": {
                bgcolor: "rgba(255,255,255,0.08)",
              },
            }}
          >
            <ListItemIcon sx={{ color: "inherit", minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
  
            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  </Drawer>
  
  );
  }
  