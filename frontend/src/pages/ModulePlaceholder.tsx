import { Typography, Box } from "@mui/material";

interface Props {
  title: string;
}

export default function ModulePlaceholder({ title }: Props) {
  return (
    <Box>
      <Typography
        variant="h4"
        sx={{
          color: "white",
          fontWeight: "bold",
        }}
      >
        {title}
      </Typography>

      <Typography
        sx={{
          mt: 2,
          color: "white",
        }}
      >
        Module will be implemented in next MVP sprint.
      </Typography>

    </Box>
  );
}
