import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { aiChat } from "../../services/api";

interface AIChatProps {
  projectId?: number | null;
}

export default function AIChat({ projectId = null }: AIChatProps) {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    const trimmedPrompt = prompt.trim();

    if (!trimmedPrompt || loading) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await aiChat(trimmedPrompt, projectId);

      setResponse(result.response || "");
    } catch (err: any) {
      console.error("AI Chat failed:", err);

      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        err?.message ||
        "AI service request failed.";

      setError(String(detail));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 2,
      }}
    >
      <Stack spacing={2}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            PIP AI Assistant
          </Typography>

          <Typography variant="body2" color="text.secondary">
            Ask the project intelligence assistant about your project.
          </Typography>
        </Box>

        {error && (
          <Alert severity="error">
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          multiline
          minRows={2}
          maxRows={5}
          label="Ask PIP AI"
          placeholder="Example: What is the current schedule condition?"
          value={prompt}
          disabled={loading}
          onChange={(event) => setPrompt(event.target.value)}
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey
            ) {
              event.preventDefault();
              void handleSubmit();
            }
          }}
        />

        <Box>
          <Button
            variant="contained"
            onClick={() => void handleSubmit()}
            disabled={loading || !prompt.trim()}
          >
            {loading ? (
              <>
                <CircularProgress
                  size={18}
                  color="inherit"
                  sx={{ mr: 1 }}
                />
                Analyzing...
              </>
            ) : (
              "Ask AI"
            )}
          </Button>
        </Box>

        {response && (
          <Box
            sx={{
              p: 2,
              borderRadius: 1,
              bgcolor: "action.hover",
            }}
          >
            <Typography
              variant="subtitle2"
              gutterBottom
              sx={{ fontWeight: 600 }}
            >
              AI Response
            </Typography>

            <Typography
              variant="body2"
              sx={{ whiteSpace: "pre-wrap" }}
            >
              {response}
            </Typography>
          </Box>
        )}
      </Stack>
    </Paper>
  );
}
