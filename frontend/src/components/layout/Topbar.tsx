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
        bgcolor: "background.paper",
        color: "white",
      }}
    >
      <Toolbar>
        <Typography variant="h6" fontWeight="bold">
          PIP AI Platform
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
            py: 1,
          }}
        >
          <SearchIcon
            sx={{
              color: "text.secondary",
              mr: 1,
            }}
          />

          <Typography variant="body2" color="text.secondary">
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

        <Avatar
          sx={{
            bgcolor: "primary.main",
          }}
        >
          F
        </Avatar>
      </Toolbar>
    </AppBar>
  );
}