import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",

    primary: {
      main: "#1976d2",
    },

    secondary: {
      main: "#26a69a",
    },

    background: {
      default: "#0f172a",
      paper: "#1e293b",
    },

    success: {
      main: "#4caf50",
    },

    warning: {
      main: "#ff9800",
    },

    error: {
      main: "#ef5350",
    },
  },

  shape: {
    borderRadius: 12,
  },

  typography: {
    fontFamily: "Roboto, Arial, sans-serif",

    h4: {
      fontWeight: 700,
    },

    h5: {
      fontWeight: 600,
    },

    h6: {
      fontWeight: 600,
    },
  },
});

export default theme;