import {
  Box,
  Button,
  Paper,
  TextField,
  Typography,
} from "@mui/material";

export default function Login() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "#020b1f",
      }}
    >

      <Paper
        sx={{
          p: 4,
          width: 360,
          bgcolor: "#17233a",
          color: "white",
        }}
      >

        <Typography
          variant="h5"
          sx={{
            mb: 3,
            fontWeight: "bold",
            color: "white",
          }}
        >
          PIP AI Platform
        </Typography>


        <TextField
          fullWidth
          label="Username"
          sx={{ mb: 2, bgcolor: "white" }}
        />


        <TextField
          fullWidth
          label="Password"
          type="password"
          sx={{ mb: 3, bgcolor: "white" }}
        />


        <Button
          fullWidth
          variant="contained"
        >
          Login
        </Button>

      </Paper>

    </Box>
  );
}
