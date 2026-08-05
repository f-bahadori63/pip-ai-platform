import { Chip } from "@mui/material";

interface StatusChipProps {
status: string;
}

export default function StatusChip({ status }: StatusChipProps) {
const getColor = () => {
switch (status) {
case "Active":
return "success";
case "Delayed":
return "error";
case "Planning":
return "warning";
default:
return "default";
}
};

return (
<Chip
label={status}
color={getColor()}
size="small"
sx={{ fontWeight: 600 }}
/>
);
}