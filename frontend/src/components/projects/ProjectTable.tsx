import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    } from "@mui/material";
    
    import StatusChip from "./StatusChip";
    
    interface Project {
    id: number;
    project_code: string;
    name: string;
    client: string;
    contract_value: number;
    currency: string;
    status: string;
    }
    
    interface Props {
    projects: Project[];
    }
    
    export default function ProjectTable({ projects }: Props) {
    return (
    <TableContainer
    component={Paper}
    sx={{ borderRadius: 3 }}
    > <Table> <TableHead> <TableRow> <TableCell><b>Code</b></TableCell> <TableCell><b>Project Name</b></TableCell> <TableCell><b>Client</b></TableCell> <TableCell align="right"><b>Contract Value</b></TableCell> <TableCell align="center"><b>Status</b></TableCell> </TableRow> </TableHead>
    
    
        <TableBody>
          {projects.map((project) => (
            <TableRow
              key={project.id}
              hover
            >
              <TableCell>
                <Typography sx={{ fontWeight: "bold" }}>
                  {project.project_code}
                </Typography>
              </TableCell>
    
              <TableCell>
                {project.name}
              </TableCell>
    
              <TableCell>
                {project.client}
              </TableCell>
    
              <TableCell align="right">
                {(project.contract_value / 1_000_000_000).toFixed(0)} B {project.currency}
              </TableCell>
    
              <TableCell align="center">
                <StatusChip status={project.status} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
        
    );
    }


