import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
  useMediaQuery,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
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
  {
    text: "Construction",
    path: "/construction",
    icon: <PrecisionManufacturingIcon />,
  },
  { text: "Cost", path: "/cost", icon: <AttachMoneyIcon /> },
  { text: "Risk", path: "/risk", icon: <WarningAmberIcon /> },
  { text: "Documents", path: "/documents", icon: <DescriptionIcon /> },
];

interface SidebarProps {
  mobileOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ mobileOpen, onClose }: SidebarProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  const drawerContent = (
    <>
      <Toolbar />
      <Box sx={{ px: 3, pb: 2 }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: "bold",
          }}
        >
          PIP AI Platform
        </Typography>
      </Box>
      <List sx={{ px: 1 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.text}
            component={NavLink}
            to={item.path}
            end={item.path === "/"}
            onClick={isMobile ? onClose : undefined}
            sx={{
              borderRadius: 2,
              mb: 1,
              color: "rgba(255,255,255,0.9)",
              "&.active": {
                bgcolor: "rgba(255,255,255,0.12)",
              },
              "&:hover": {
                bgcolor: "rgba(255,255,255,0.08)",
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
    </>
  );

  const paperSx = {
    width: drawerWidth,
    boxSizing: "border-box" as const,
    bgcolor: "#17233a",
    color: "white",
    borderRight: "1px solid rgba(255,255,255,0.08)",
  };

  if (isMobile) {
    return (
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        sx={{
          "& .MuiDrawer-paper": paperSx,
        }}
      >
        {drawerContent}
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        "& .MuiDrawer-paper": paperSx,
      }}
    >
      {drawerContent}
    </Drawer>
  );
}
