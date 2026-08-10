import { useEffect, useState } from "react";
import api from "../../services/api";

export default function CriticalActivities() {

  const [activities, setActivities] = useState<any[]>([]);

  useEffect(() => {

    api
      .get("/dashboard/critical-activities/1")
      .then((response) => {
        console.log("CRITICAL ACTIVITIES:", response.data);
        setActivities(response.data.activities || []);
      })
      .catch((error) => {
        console.error("Critical Activities Error:", error);
      });

  }, []);


  return (
    <div>

      <h3>Critical Activities</h3>

      <table
        style={{
          width: "100%",
          borderCollapse: "collapse"
        }}
      >

        <thead>
          <tr>
            <th>Code</th>
            <th>Activity</th>
            <th>Planned %</th>
            <th>Actual %</th>
            <th>Variance</th>
            <th>Risk</th>
          </tr>
        </thead>


        <tbody>

        {activities.map((item) => (

          <tr key={item.activity_id}>

            <td>{item.activity_code}</td>

            <td>
              {item.activity_name}
            </td>

            <td>
              {item.planned_progress}%
            </td>

            <td>
              {item.actual_progress}%
            </td>

            <td>
              {item.schedule_variance}%
            </td>

            <td>
              {item.risk_level}
            </td>

          </tr>

        ))}

        </tbody>

      </table>

    </div>
  );
}




