import {
  Drawer,
  Toolbar,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
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
import SmartToyIcon from "@mui/icons-material/SmartToy";
import SettingsIcon from "@mui/icons-material/Settings";

const drawerWidth = 260;

const menuItems = [
  { text: "Dashboard", icon: <DashboardIcon /> },
  { text: "Projects", icon: <FolderIcon /> },
  { text: "WBS", icon: <AccountTreeIcon /> },
  { text: "Schedule", icon: <CalendarMonthIcon /> },
  { text: "Engineering", icon: <EngineeringIcon /> },
  { text: "Procurement", icon: <ShoppingCartIcon /> },
  { text: "Construction", icon: <PrecisionManufacturingIcon /> },
  { text: "Cost", icon: <AttachMoneyIcon /> },
  { text: "Risk", icon: <WarningAmberIcon /> },
  { text: "Documents", icon: <DescriptionIcon /> },
  { text: "AI Project Manager", icon: <SmartToyIcon /> },
  { text: "Settings", icon: <SettingsIcon /> },
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
          bgcolor: "background.paper",
          color: "white",
          borderRight: "1px solid rgba(255,255,255,0.08)",
        },
      }}
    >
      <Toolbar>

        <Typography
          variant="h6"
          fontWeight="bold"
        >
          PIP Platform
        </Typography>

      </Toolbar>

      <Divider />

      <List>

        {menuItems.map((item) => (

          <ListItemButton
            key={item.text}
            sx={{
              mx: 1,
              my: 0.5,
              borderRadius: 2,

              "&:hover": {
                bgcolor: "primary.main",
              },
            }}
          >

            <ListItemIcon
              sx={{
                color: "inherit",
                minWidth: 40,
              }}
            >
              {item.icon}
            </ListItemIcon>

            <ListItemText primary={item.text} />

          </ListItemButton>

        ))}

      </List>
    </Drawer>
  );
}