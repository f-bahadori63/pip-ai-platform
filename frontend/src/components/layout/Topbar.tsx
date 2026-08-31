import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Avatar,
  IconButton,
  Badge,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import NotificationsIcon from "@mui/icons-material/Notifications";
import SearchIcon from "@mui/icons-material/Search";
import ProjectSelector from "./ProjectSelector";

const drawerWidth = 260;

interface TopbarProps {
  onMenuClick: () => void;
}

export default function Topbar({ onMenuClick }: TopbarProps) {
  return (
    <AppBar
      position="fixed"
      elevation={1}
      sx={{
        width: { xs: "100%", md: `calc(100% - ${drawerWidth}px)` },
        ml: { xs: 0, md: `${drawerWidth}px` },
        bgcolor: "#17233a",
        color: "white",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <Toolbar sx={{ gap: { xs: 1, sm: 2 } }}>
        <IconButton
          color="inherit"
          edge="start"
          onClick={onMenuClick}
          sx={{ display: { xs: "inline-flex", md: "none" } }}
        >
          <MenuIcon />
        </IconButton>

        <Typography
          variant="h6"
          noWrap
          sx={{
            fontWeight: "bold",
            display: { xs: "none", sm: "block" },
          }}
        >
          Project Intelligence
        </Typography>

        <Box sx={{ width: 30, display: { xs: "none", sm: "block" } }} />

        <Box
          sx={{
            width: 300,
            display: { xs: "none", md: "flex" },
            alignItems: "center",
            bgcolor: "white",
            borderRadius: 2,
            px: 2,
            py: 0.75,
            color: "text.secondary",
          }}
        >
          <SearchIcon sx={{ mr: 1 }} />
          <Typography variant="body2">
            Search...
          </Typography>
        </Box>

        <ProjectSelector />
        <Box sx={{ flexGrow: 1 }} />
        <IconButton color="inherit">
          <Badge badgeContent={2} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
        <Typography
          sx={{
            mx: 2,
            fontWeight: 600,
            display: { xs: "none", sm: "block" },
          }}
        >
          Farzad
        </Typography>
        <Avatar sx={{ bgcolor: "primary.main" }}>
          F
        </Avatar>
      </Toolbar>
    </AppBar>
  );
}
