import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Avatar,
  IconButton,
  Badge,
} from "@mui/material";

import NotificationsIcon from "@mui/icons-material/Notifications";
import SearchIcon from "@mui/icons-material/Search";

const drawerWidth = 260;

export default function Topbar() {
  return (
    <AppBar
      position="fixed"
      elevation={1}
      sx={{
        width: `calc(100% - ${drawerWidth}px)`,
        ml: `${drawerWidth}px`,
        bgcolor: "#17233a",
        color: "white",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          sx={{
            fontWeight: "bold",
          }}
        >
          Project Intelligence
        </Typography>

        <Box sx={{ width: 30 }} />

        <Box
          sx={{
            width: 300,
            display: "flex",
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
